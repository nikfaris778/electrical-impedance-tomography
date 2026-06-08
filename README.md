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
│   ├── main.py                # Main state machine and execution loop
│   ├── ad5933.py              # I2C driver for the AD5933 Impedance Converter
│   └── mux_control.py         # GPIO routing logic for the 16-channel matrix
│
├── /simulations               # MATLAB scripts using the EIDORS toolbox
│   ├── validation_3D.m        # Core 3D EIT simulation (Single Target)
│   ├── spatial_variance.m     # Multi-quadrant spatial variance loop
│   └── README_Simulations.md  # Specific instructions for EIDORS dependencies
│
├── /hardware_docs             # (Optional) Schematics and PCB Layouts
│   └── V2_Schematic.pdf       # Schematic outlining the AFE and routing matrix
│
└── README.md                  # This document
