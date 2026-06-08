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

## 📄 File Manifest
```text
ValidationCode.m
```
The core validation script. It builds a 16-electrode, dual-ring cylindrical mesh and simulates a central non-conductive inclusion (representing an acrylic rod). It applies the 4-pole cross-planar firmware protocol, injects hardware noise, and outputs a thresholded 3D isosurface and 2D Z-axis cross-sections.

```text
SpatialComparison.m
```
A multi-target iterative script. It loops the forward and inverse solvers across three distinct XY coordinates (Dead Center, Top-Left, Bottom-Right) and generates a side-by-side comparative plot. This formally proves that the NOSER-regularized solver is robust against the inherently low central sensitivity of the EIT Jacobian matrix.

## 🎛️ Key Parameters for Experimentation
If you wish to modify the simulations to test different hardware constraints, look for the following variables in the scripts:
1. SNR_dB (Default: 40): Controls the Additive White Gaussian Noise (AWGN). 40dB represents the calculated thermal noise floor and quantization error of the V2.0 AD8221/AD5933 frontend. Lowering this value simulates a noisier PCB.
2. imdl.hyperparameter.value (Default: 1.0): The $\lambda$ tuning knob for the NOSER regularization algorithm.
   - Increase this value (e.g., 10.0) to heavily penalize boundary noise (results in a blurry, over-regularized image).
   - Decrease this value (e.g., 0.1) to reduce the penalty (results in high spatial resolution but severe peripheral noise artifacts).

## ⚠️ Important Note on Spatial Coordinates
The simulated saline tank has an absolute radius of 1.0. When modifying the $X$ and $Y$ coordinates of the acrylic rod, ensure that the outer edge of the rod does not exceed the tank boundary.If the condition sqrt(X^2 + Y^2) + Radius > 1.0 is met, the inclusion will physically clip outside the finite element mesh, and the solver will throw a NaN boundary exception.
