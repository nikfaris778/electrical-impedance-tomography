# MUX control tests
from machine import Pin
import time

# 🚨 REPLACE these numbers with your actual GP pin numbers! 🚨
# Group them by MUX to make your life easier when probing.
mux_1_pins = [Pin(2, Pin.OUT), Pin(3, Pin.OUT), Pin(4, Pin.OUT), Pin(5, Pin.OUT)]
mux_2_pins = [Pin(6, Pin.OUT), Pin(7, Pin.OUT), Pin(8, Pin.OUT), Pin(9, Pin.OUT)]
mux_3_pins = [Pin(10, Pin.OUT), Pin(11, Pin.OUT), Pin(12, Pin.OUT), Pin(13, Pin.OUT)]
mux_4_pins = [Pin(14, Pin.OUT), Pin(15, Pin.OUT), Pin(16, Pin.OUT), Pin(17, Pin.OUT)]

all_mux_pins = mux_1_pins + mux_2_pins + mux_3_pins + mux_4_pins
 
print("Starting 16-Pin MUX diagnostic.")
print("Check MUX 1, then MUX 2, etc. Take your time.")
print("-------------------------------------------------------------")

try:
    while True:
        print("--> Driving ALL 16 pins HIGH (3.3V)")
        for pin in all_mux_pins:
            pin.value(1)
        time.sleep(8)  # 8 seconds to give you time to probe  
        
        print("--> Driving ALL 16 pins LOW (0V)")
        for pin in all_mux_pins:
            pin.value(0)
        time.sleep(8) 

except KeyboardInterrupt:
    for pin in all_mux_pins:
        pin.value(0)
    print("\nTest stopped. Pins grounded.")