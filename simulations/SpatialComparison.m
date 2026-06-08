%% Initialisation
clc; clear; clf;
run D:\MATLAB\EIDORS\eidors-v3.12-ng\eidors\startup.m

%%
% =========================================================================
% EIT 3D SPATIAL VARIANCE ANALYSIS
% Objective: Validate reconstruction accuracy across different XY quadrants.
% =========================================================================

% 1 & 2. BUILD FORWARD MODEL & FIRMWARE PROTOCOL (Run Once)
fmdl = mk_common_model('b3cz2', [16, 1]); 
[stim, meas_select] = mk_stim_patterns(16, 1, [0,8], [0,1], {'no_meas_current'}, 1);
fmdl.fwd_model.stimulation = stim;
fmdl.fwd_model.meas_select = meas_select; 

% 3. SET BASELINE (Saline Calibration) & PRE-COMPUTE SOLVER
img_baseline = mk_image(fmdl.fwd_model, 0.3); 
vh = fwd_solve(img_baseline); % Pre-calculate baseline voltages

imdl = eidors_obj('inv_model', '3D EIT Reconstruction');
imdl.reconst_type = 'difference'; 
imdl.fwd_model = fmdl.fwd_model;
imdl.jacobian_bkgnd.value = 0.3; 
imdl.solve = @inv_solve_diff_GN_one_step;
imdl.RtR_prior = @prior_noser; 
imdl.hyperparameter.value = 1.0; 

% Extract XYZ coordinates of the mesh
xyz = interp_mesh(fmdl.fwd_model);
x = xyz(:,1); y = xyz(:,2); z = xyz(:,3);

% =========================================================================
% 4. DEFINE THE TEST COORDINATES [X, Y]
% =========================================================================
test_positions = [
    0.0,  0.0;  % Position 1: Dead Center
    -0.5,  0.5;  % Position 2: Top-Left Quadrant
    0.5, -0.5   % Position 3: Bottom-Right Quadrant
    ];

% Prepare the Figure Window
figure('Name', 'Spatial Variance Analysis', 'Position', [100, 100, 1500, 500]);

% =========================================================================
% 5. EXECUTE THE SIMULATION LOOP
% =========================================================================
for i = 1:size(test_positions, 1)

    % Model the Rod at the current loop coordinates
    img_rod = img_baseline;
    rod_elements = (x - test_positions(i,1)).^2 + (y - test_positions(i,2)).^2 < 0.2^2;
    img_rod.elem_data(rod_elements) = 0.001;

    % Forward solve
    vi = fwd_solve(img_rod);

    % Inject Hardware Noise (SNR = 40dB)
    SNR_dB = 40; 
    signal_power = var(vi.meas - vh.meas);
    noise_power = signal_power / (10^(SNR_dB / 10));
    thermal_noise = sqrt(noise_power) * randn(size(vi.meas));
    vi_noisy = vi;
    vi_noisy.meas = vi.meas + thermal_noise;

    % Inverse solve
    img_reconstructed = inv_solve(imdl, vh, vi_noisy);

    % Thresholding for 3D Render
    img_thresh = img_reconstructed;
    peak_anomaly = min(img_thresh.elem_data); 
    threshold = peak_anomaly * 0.25; 
    img_thresh.elem_data(img_thresh.elem_data > threshold) = NaN; 
    img_thresh.calc_colours.clim = max(abs(img_thresh.elem_data));

    % Render the Subplot
    subplot(1, 3, i);
    show_fem(img_thresh);
    view(3); camlight;
    title(sprintf('Rod Reconstructed at X: %.1f, Y: %.1f', test_positions(i,1), test_positions(i,2)));

end