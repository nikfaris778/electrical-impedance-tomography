from machine import Pin, I2C
import time
import struct
import json

class AD5933:
    """Hardware Abstraction Layer for the AD5933 Impedance Converter."""
    ADDR = 0x0D
    
    # Register Map
    REG_CTRL_HB = 0x80
    REG_CTRL_LB = 0x81
    REG_START_FREQ_1 = 0x82
    REG_FREQ_INC_1 = 0x85
    REG_NUM_INC_1 = 0x88
    REG_SETTLING_CYCLES_1 = 0x8A
    REG_STATUS = 0x8F
    REG_REAL_DATA_1 = 0x94
    REG_IMAG_DATA_1 = 0x96

    # Control Commands
    CTRL_STANDBY = 0xB0
    CTRL_INIT_START_FREQ = 0x10
    CTRL_START_FREQ_SWEEP = 0x20
    CTRL_INC_FREQ = 0x30
    
    def __init__(self, i2c_bus, ext_clk=16776000):
        self.i2c = i2c_bus
        self.clk = ext_clk
        self.verify_connection()
        self.reset()

    def verify_connection(self):
        devices = self.i2c.scan()
        if self.ADDR not in devices:
            raise RuntimeError("AD5933 not found on I2C bus. Check 3V3 rail and SDA/SCL pull-ups.")
        print("AD5933 verified at 0x0D.")

    def write_reg(self, reg, value):
        self.i2c.writeto_mem(self.ADDR, reg, bytes([value]))

    def read_reg(self, reg):
        return self.i2c.readfrom_mem(self.ADDR, reg, 1)[0]

    def reset(self):
        # Reset command to Control Register Low Byte
        self.write_reg(self.REG_CTRL_LB, 0x10)
        time.sleep_ms(10)
        self.set_standby()

    def set_standby(self):
        self.write_reg(self.REG_CTRL_HB, self.CTRL_STANDBY)

    def program_sweep(self, start_hz, inc_hz, num_inc, settling_cycles):
        """Calculates and loads the 24-bit frequency words."""
        # Calculate Start Frequency Code
        start_code = int((start_hz / (self.clk / 4)) * (2**27))
        self.write_reg(self.REG_START_FREQ_1, (start_code >> 16) & 0xFF)
        self.write_reg(self.REG_START_FREQ_1 + 1, (start_code >> 8) & 0xFF)
        self.write_reg(self.REG_START_FREQ_1 + 2, start_code & 0xFF)

        # Calculate Increment Code
        inc_code = int((inc_hz / (self.clk / 4)) * (2**27))
        self.write_reg(self.REG_FREQ_INC_1, (inc_code >> 16) & 0xFF)
        self.write_reg(self.REG_FREQ_INC_1 + 1, (inc_code >> 8) & 0xFF)
        self.write_reg(self.REG_FREQ_INC_1 + 2, inc_code & 0xFF)

        # Number of increments (9-bit limit, max 511)
        self.write_reg(self.REG_NUM_INC_1, (num_inc >> 8) & 0x01)
        self.write_reg(self.REG_NUM_INC_1 + 1, num_inc & 0xFF)

        # Settling time cycles (D10-D9 for multiplier, D8-D0 for cycles)
        # Using 1x multiplier for standard EIT frequencies
        self.write_reg(self.REG_SETTLING_CYCLES_1, (settling_cycles >> 8) & 0x07)
        self.write_reg(self.REG_SETTLING_CYCLES_1 + 1, settling_cycles & 0xFF)

    def measure_single_point(self):
        """Executes a single point measurement with strict polling."""
        self.write_reg(self.REG_CTRL_HB, self.CTRL_INIT_START_FREQ)
        time.sleep_ms(5) # Allow internal DC bias to settle
        self.write_reg(self.REG_CTRL_HB, self.CTRL_START_FREQ_SWEEP)

        # Poll Status Register for Valid Data (Bit 1)
        timeout = time.ticks_add(time.ticks_ms(), 100)
        while not (self.read_reg(self.REG_STATUS) & 0x02):
            if time.ticks_diff(timeout, time.ticks_ms()) < 0:
                raise TimeoutError("AD5933 conversion timed out.")

        # Read 16-bit Two's Complement Data
        real_high = self.read_reg(self.REG_REAL_DATA_1)
        real_low = self.read_reg(self.REG_REAL_DATA_1 + 1)
        imag_high = self.read_reg(self.REG_IMAG_DATA_1)
        imag_low = self.read_reg(self.REG_IMAG_DATA_1 + 1)

        real = struct.unpack('>h', bytes([real_high, real_low]))[0]
        imag = struct.unpack('>h', bytes([imag_high, imag_low]))[0]

        self.set_standby()
        return real, imag

class MUX_Matrix:
    """Manages the 16 independent GPIOs for the 4-Pole MUX array."""
    def __init__(self):
        # Mapped strictly to schematic Multicontroller_9.jpg
        self.inj_p_pins = [Pin(i, Pin.OUT) for i in (2, 3, 4, 5)]
        self.inj_n_pins = [Pin(i, Pin.OUT) for i in (6, 7, 8, 9)]
        self.meas_p_pins = [Pin(i, Pin.OUT) for i in (10, 11, 12, 13)]
        self.meas_n_pins = [Pin(i, Pin.OUT) for i in (14, 15, 16, 17)]
        
        # Enable Pins (Active Low)
        self.en_inject = Pin(18, Pin.OUT, value=1) 
        self.en_measure = Pin(19, Pin.OUT, value=1)

    def disable_all(self):
        """Break-before-make absolute enforcement."""
        self.en_inject.value(1)
        self.en_measure.value(1)
        time.sleep_us(10) # 10us guard band for logic switching

    def set_address(self, pins, channel):
        """Writes binary address to specific MUX S-lines."""
        for i in range(4):
            pins[i].value((channel >> i) & 1)

    def route_frame(self, inj_p, inj_n, meas_p, meas_n):
        """Executes a surgical 4-pole routing change."""
        self.disable_all()
        
        self.set_address(self.inj_p_pins, inj_p)
        self.set_address(self.inj_n_pins, inj_n)
        self.set_address(self.meas_p_pins, meas_p)
        self.set_address(self.meas_n_pins, meas_n)
        
        # Re-enable the paths
        self.en_inject.value(0)
        self.en_measure.value(0)
        
        # Settle delay for the Howland Pump's Virtual Ground RC constant
        time.sleep_us(500) 

class EIT_System:
    """Top-level frame grabber and telemetry manager."""
    def __init__(self):
        print("Initializing EIT Multicontroller...")
        # I2C initialized to 400kHz for high-throughput phase
        self.i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
        
        try:
            self.ad5933 = AD5933(self.i2c)
            self.mux = MUX_Matrix()
            # Standard single-frequency test profile: 50kHz
            self.ad5933.program_sweep(start_hz=50000, inc_hz=0, num_inc=0, settling_cycles=15)
        except Exception as e:
            print(f"Hardware Boot Failure: {e}")
            raise

    def get_adjacent_measurement(self):
        """
        Executes a classic 16-electrode adjacent scan protocol.
        Yields 208 independent measurements (16 * 13).
        """
        frame_data = []
        try:
            for inj_idx in range(16):
                inj_p = inj_idx
                inj_n = (inj_idx + 1) % 16
                
                for meas_idx in range(16):
                    meas_p = meas_idx
                    meas_n = (meas_idx + 1) % 16
                    
                    # Prevent measuring on the active injection pair (contact impedance error)
                    if (meas_p in [inj_p, inj_n]) or (meas_n in [inj_p, inj_n]):
                        continue
                    
                    # 1. Route the hardware
                    self.mux.route_frame(inj_p, inj_n, meas_p, meas_n)
                    
                    # 2. Trigger the impedance extraction
                    real, imag = self.ad5933.measure_single_point()
                    
                    # 3. Store the result
                    data_point = {
                        "inj": [inj_p, inj_n],
                        "meas": [meas_p, meas_n],
                        "re": real,
                        "im": imag
                    }
                    frame_data.append(data_point)
                    
            return frame_data

        finally:
            # HARDWARE SURVIVAL: Ensures current pump is always disconnected 
            # if the code crashes or the user hits Ctrl+C.
            self.mux.disable_all()
            print("System Safed. MUXes Disabled.")

    def transmit_telemetry(self, data):
        """Serializes the frame into JSON and pushes it out the USB UART."""
        payload = json.dumps({"frame": data})
        print(payload)

# ==========================================
# Main Execution Block
# ==========================================
if __name__ == "__main__":
    eit = EIT_System()
    print("Beginning 4-Pole Adjacent Protocol Scan...")
    
    # Grab a single frame
    frame_measurements = eit.get_adjacent_measurement()
    
    print(f"Scan complete. Captured {len(frame_measurements)} data points.")
    
    # Transmit to PC for MATLAB/Python image reconstruction
    eit.transmit_telemetry(frame_measurements)