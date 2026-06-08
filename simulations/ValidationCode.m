% =========================================================================
% EIT 3D SYSTEM VALIDATION VIA SYNTHETIC FORWARD MODELING
% =========================================================================
% Objective: Reconstruct a 3D non-conductive inclusion (Acrylic Rod) 
% using a 2x8 dual-ring opposite-drive protocol and NOSER regularization.
% =========================================================================
%% Initialisation
clc; clear; clf;
run D:\MATLAB\EIDORS\eidors-v3.12-ng\eidors\startup.m

%% One-line starter

% 1. BUILD THE 3D FORWARD MODEL (The Virtual Tank)
fmdl = mk_common_model('b3cz2', [16, 1]); 

% 2. DEFINE THE FIRMWARE INJECTION PROTOCOL
% 16 electrodes, inject across i and i+8 (cross-planar diagonal), measure adjacent.
% {'no_meas_current'} enforces the 4-pole topology, generating 192 measurement pairs.
[stim, meas_select] = mk_stim_patterns(16, 1, [0,8], [0,1], {'no_meas_current'}, 1);

% Overwrite BOTH the stimulation sequence and the measurement matrix mask
fmdl.fwd_model.stimulation = stim;
fmdl.fwd_model.meas_select = meas_select; 

% 3. SET THE BASELINE HOMOGENEOUS STATE (Saline Calibration)
% Conductivity of 0.3 S/m simulates standard saline.
img_baseline = mk_image(fmdl.fwd_model, 0.3); 

% 4. MODEL MULTIPLE NON-CONDUCTIVE INCLUSIONS (Acrylic Rods)
img_rod = img_baseline;
% Extract XYZ coordinates of all finite elements in the mesh
xyz = interp_mesh(fmdl.fwd_model);
x = xyz(:,1); y = xyz(:,2); z = xyz(:,3);

% Define the spatial boundaries for three distinct rods
% Rod 1: Center-Right
rod1 = (x).^2 + (y).^2 < 0.2^2;
% Rod 2: Top-Left Quadrant
% rod2 = (x + 0.4).^2 + (y - 0.4).^2 < 0.2^2;
% % Rod 3: Bottom-Right Quadrant
% rod3 = (x - 0.4).^2 + (y+0.4).^2 < 0.2^2;

% Combine them using the logical OR operator (|)
rod_elements = rod1;

% Set the conductivity of all combined rod elements to an insulator value
img_rod.elem_data(rod_elements) = 0.001;

% Set rod conductivity to a near-zero value (0.001 S/m) to represent acrylic.
img_rod.elem_data(rod_elements) = 0.001;

% 5. SOLVE THE FORWARD PROBLEM (Simulate the Hardware)
% Calculate what the perfect, ideal boundary voltages would be.
vh = fwd_solve(img_baseline); % Homogeneous reference voltages
vi = fwd_solve(img_rod);      % Inhomogeneous (Rod) voltages

% 6. INJECT HARDWARE PARASITICS (AD8221 Noise Simulation)
% We inject Additive White Gaussian Noise (AWGN) to simulate
% thermal noise and the AD5933 ADC quantization error.
SNR_dB = 40; % Realistic Signal-to-Noise Ratio for a V1.0 PCB
signal_power = var(vi.meas - vh.meas);
noise_power = signal_power / (10^(SNR_dB / 10));
thermal_noise = sqrt(noise_power) * randn(size(vi.meas));

% Corrupt the ideal data with the noise vector
vi_noisy = vi;
vi_noisy.meas = vi.meas + thermal_noise;

% 7. CONFIGURE THE INVERSE SOLVER (The Reconstruction Math)
imdl = eidors_obj('inv_model', '3D EIT Reconstruction');
imdl.reconst_type = 'difference'; % Execute Time-Difference EIT
imdl.fwd_model = fmdl.fwd_model;
imdl.jacobian_bkgnd.value = 0.3; % Inform solver of baseline conductivity

% Apply NOSER Regularization to counteract central sensitivity decay
imdl.solve = @inv_solve_diff_GN_one_step;
imdl.RtR_prior = @prior_noser; 
imdl.hyperparameter.value = 1.0; % Penalty weight (tune this between 0.1 and 10)

% 8. EXECUTE THE INVERSE PROBLEM 
% Map the noisy boundary voltages back to a 3D conductivity matrix
img_reconstructed = inv_solve(imdl, vh, vi_noisy);


% =========================================================================
% 9. RENDER THESIS FIGURES (Dynamic Coordinate Fix)
% =========================================================================

% EXTRACT PHYSICAL MESH LIMITS TO PREVENT OUT-OF-BOUNDS ERRORS
xyz = interp_mesh(fmdl.fwd_model);
max_z = max(xyz(:,3)); 
min_z = min(xyz(:,3));

% Calculate dynamic slice planes based on the actual mesh height
z_mid = (max_z + min_z) / 2;             % Dead center of the tank
z_upper = min_z + 0.75 * (max_z - min_z);  % 75% height (Top Ring)
z_lower = min_z + 0.25 * (max_z - min_z);  % 25% height (Bottom Ring)

clf;
% Figure 1: The True Forward Model (What is actually in the tank)
f1 = figure(1);
show_fem(img_rod);
view(3); camlight;

% Figure 2: Horizontal Slices (Z-Axis Cross Sections)
f2 = figure(2);
% Slicing dynamically at the upper and lower rings
levels = [inf, inf, z_upper;  
          inf, inf, z_lower]; 
show_slices(img_reconstructed, levels);

% Figure 3: 3D Volumetric Iso-Surface (Bypassing the MATLAB trimesh bug)
f3 = figure(3);
% Create a copy of the reconstruction for thresholding
img_thresh = img_reconstructed;

% In difference EIT, replacing saline with an insulator (acrylic) 
% creates a highly NEGATIVE conductivity change. 
% We isolate the rod by finding the peak negative value in the mesh.
peak_anomaly = min(img_thresh.elem_data); 

% Set a mathematical threshold (e.g., 25% of the peak negative change)
% Any voxel with a negative change stronger than this threshold is part of the rod.
threshold = peak_anomaly * 0.25; 

% Strip away the saline background. 
% We set all elements greater than the threshold (closer to 0 or positive) to NaN.
img_thresh.elem_data(img_thresh.elem_data > threshold) = NaN; 

% EIDORS show_fem will completely ignore NaN elements, leaving only the 3D rod visible.
% We also force the color map limits so the rod renders with high contrast.
img_thresh.calc_colours.clim = max(abs(img_thresh.elem_data));
show_fem(img_thresh);

% Formatting the 3D view
view(3); 
camlight;

% export graphics
exportgraphics(f1,'ForwardModel.png',Resolution=600);
exportgraphics(f2,'2DSlices.png',Resolution=600);
exportgraphics(f3,'VolumetricIsoSurface2.png',Resolution=600);