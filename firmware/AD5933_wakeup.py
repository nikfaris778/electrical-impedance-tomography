from machine import Pin, I2C
import time

# ==========================================
# 1. I2C Bus Scan (AD5933 Verification)
# ==========================================
# Referencing Multicontroller_6.jpg: SDA = GP0, SCL = GP1
# We start at 100kHz. Once we prove communication, we can bump to 400kHz.
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=100000) 

def scan_i2c():
    print("Scanning I2C bus...")
    devices = i2c.scan()
    if devices:
        for d in devices:
            # The AD5933 has a fixed I2C address of 0x0D (13 decimal)
            print(f"Device found at hex address: {hex(d)}")
            if d == 0x0D:
                print("-> SUCCESS: AD5933 Impedance Converter detected.")
    else:
        print("-> FAULT: No I2C devices found. Check 3V3 rail and SDA/SCL pull-ups.")

# ==========================================
# 2. CD74HC4067 MUX Logic Test
# ==========================================
# Update these GPIO pin numbers to match your exact physical wiring for S0-S3
addr_pins = [Pin(i, Pin.OUT) for i in (4, 5, 6, 7)] 

# Enable pins - initialized HIGH (Disabled) for safety
en_inject = Pin(24, Pin.OUT, value=1) 
en_measure = Pin(25, Pin.OUT, value=1)

def test_mux_logic():
    print("\nStarting MUX slow-step test. Get your multimeter ready.")
    print("Probing the E (Enable) and S0-S3 pins on the IC packages.")
    
    # Enable the MUXes (Drive LOW)
    en_inject.value(0)
    en_measure.value(0)
    print("Enable pins driven LOW. MUXes ACTIVE.")
    time.sleep(2) # Time to verify E pins are actually ~0V
    
    for channel in range(4): # Just testing the first 4 channels to verify the bus
        print(f"Switching to logic state for Channel {channel} (Binary: {channel:04b})")
        for i in range(4):
            addr_pins[i].value((channel >> i) & 1)
        
        # We hold here for 5 seconds so you can physically probe the S0, S1, S2, S3 
        # pins on the CD74HC4067 to verify the Pico is successfully driving the traces.
        time.sleep(5) 
        
    print("Test complete. Disabling MUXes to return to safe state.")
    en_inject.value(1)
    en_measure.value(1)

# Run the diagnostics
scan_i2c()
# Uncomment the line below when you are ready to probe with your DMM
test_mux_logic()