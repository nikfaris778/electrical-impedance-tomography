# Synthetic Validation Environment (EIDORS 3D)

This directory contains the MATLAB simulation scripts utilized to mathematically validate the 3D opposite-drive architecture of the EIT system. 

Because physical biological validation was precluded by a power domain mismatch (CMOS latch-up) on the V2.0 hardware, these scripts serve as the definitive proof of the system's underlying firmware state machine and analog sensitivity limits.

## 🧰 Prerequisites
To run these scripts, you must have the following installed:
* **MATLAB** (Tested on R2022a and newer)
* **EIDORS Toolbox** (Electrical Impedance Tomography and Diffuse Optical Tomography Reconstruction Software) - Version 3.11 or newer.

[Download EIDORS here](http://eidors3d.sourceforge.net/download.shtml)

## ⚙️ Setup Instructions
EIDORS must be initialized in your MATLAB workspace before running the simulation scripts.
1. Download and extract the EIDORS toolbox to your local machine.
2. Open MATLAB.
3. In the command window, run the EIDORS startup script:
   ```matlab
   run('C:\Path\To\Your\eidors3.11\eidors\startup.m')
4. You should see EIDORS: <Version> print in the console. You are now ready to run the simulations.

## File manifest
``text
