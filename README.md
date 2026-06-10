# Electical Impedance Tomography with Embroidered Electrodes

![Status: Prototype / Simulated Validation](https://img.shields.io/badge/Status-Simulated%20Validation-blue)
![Platform: Raspberry Pi Pico](https://img.shields.io/badge/Platform-RP2040%20(Pico)-green)
![Environment: MATLAB & EIDORS](https://img.shields.io/badge/Environment-MATLAB%20%7C%20EIDORS-orange)

## 📌 Project Overview
This repository contains the MicroPython firmware and MATLAB simulation scripts for a 16-channel, 3D Electrical Impedance Tomography (EIT) system. Developed as part of a Master of Engineering (MEng) thesis, the project aimed to bridge the gap between low-cost analog hardware and true volumetric impedance imaging using custom CNC-embroidered textile electrodes (HC40 silver-plated thread).

Due to hardware compliance voltage limitations discovered in the V2.0 PCB iteration, the physical system was mathematically validated via synthetic forward modeling. The MATLAB scripts provided here rigorously prove the viability of the system's 3D cross-planar opposite-drive architecture against simulated hardware noise floors.

## 📂 Repository Structure

```text
├── /firmware                  # MicroPython code for the RP2040 (Raspberry Pi Pico)
│   ├── ad5933_wakeup.py       # AD5933 initialisation
│   ├── eit_driver.py          # I2C driver for the AD5933 Impedance Converter
│   └── MUX_control.py         # GPIO routing logic for the 16-channel matrix
│
├── /simulations               # MATLAB scripts using the EIDORS toolbox
│   ├── ValidationCode.m       # Core 3D EIT simulation (Single Target)
│   ├── SpatialComparison.m    # Multi-quadrant spatial variance loop
│   └── README_Simulations.md  # Specific instructions for EIDORS dependencies
│
├── /hardware_docs             # Schematics and PCB Layouts
│   ├── EIT_CONNECTIONS.pdf    # Patient protection block layout
│   ├── EIT_CURRENTSTAGE.pdf   # Analogue front end layout
│   ├── EIT_MULTICONTROLLER.pdf # Pi Pico 2 arrangement with pins
│   ├── EIT_MUXERS.pdf         # Multiplexer routing arrangement
│   └── EIT_board.PcbPrj       # Altium PCB project
└── README.md                  # This document
```
## 🧠 System Architecture
1. Hardware & Firmware Topology
- The physical system utilizes a four-pole (Kelvin) measurement strategy to mathematically negate the high and variable contact impedance ($Z_{contact}$) of the dry textile electrodes.
- Excitation Stage: Enhanced Howland Current Pump (designed for 1mA AC).
- Sensing Stage: AD8221 Instrumentation Amplifier.
- Impedance Converter: AD5933.
- Firmware Protocol: The MicroPython state machine dictates a dual-ring, cross-planar opposite-drive sequence (skip 8). This forces out-of-plane vertical current density vectors ($J_z$) critical for depth-resolved 3D tomography.

2. MATLAB / EIDORS Simulation
To validate the architecture, the MicroPython switching matrix was algorithmically mirrored in EIDORS.
- Noise Injection: Additive White Gaussian Noise (AWGN) at 40dB SNR was injected to simulate the real-world thermal noise limits of the AD8221.
- Inverse Solver: The system utilizes Time-Difference EIT with NOSER Regularization to compensate for the inherently low central sensitivity of the Jacobian matrix, successfully isolating 3D volumetric anomalies.

## 🚀 Getting Started
# Running the EIDORS Simulations
1. Ensure you have MATLAB installed.
2. Download and install the EIDORS 3.11 Toolbox.
3. In the MATLAB console, initialize EIDORS by running:
```matlab
run /path/to/eidors/startup.m
```
4. Open and run validation_3D.m to generate the 3D thresholded tomograms and 2D cross-sectional slices.
# Flashing the Firmware
1. Flash your Raspberry Pi Pico with the latest MicroPython UF2 bootloader.
2. Open the /firmware directory in an IDE like Thonny.
3. Upload main.py, ad5933.py, and mux_control.py to the Pico's root directory.

## ⚠️ Known Hardware Limitations & V3.0 Roadmap
This section documents critical system bring-up findings for future researchers.The V2.0 hardware iteration experienced a severe power domain mismatch ("Compliance Voltage Paradox"). The $\pm 9\text{V}$ analog supply required by the Howland Current Pump to drive high-impedance biological loads forward-biased the internal ESD diodes of the 3.3V CD74HC4067 multiplexers, causing catastrophic CMOS latch-up.

# V3.0 Recommendations:
1. Routing Matrix: Replace the logic-level CMOS multiplexers with high-voltage bipolar analog switches (e.g., Analog Devices ADG1406 or ADG1606) powered directly from the $\pm 9\text{V}$ analog rails.
2. Textile Interfaces: Implement active-electrode buffer topologies directly on the embroidered fabric substrate to combat the long-term oxidation of the HC40 silver thread.
3. Verification: Mandate SPICE transient analysis prior to Gerber generation to ensure safe mixed-signal boundary transitions.

## 📝 License
This project is open-source and available under the MIT License.
