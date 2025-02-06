%% Source Localization and Leadfield Computation
% This script computes:
%   1. The leadfield matrix (used for simulating MEG activity in the model).
%   2. Source localization of MEG activity for empirical comparison.
% Dependencies: FieldTrip andd Individual T1.nii

clear all; close all; clc;
addpath('/path/to/fieldtrip');
ft_defaults;

%% Define Subjects and Data Paths
subs = {'Subject01', 'Subject02'};  % Add subject IDs
baseDir = '/path/to/data/';  % Update with correct path

for s = 1:length(subs)
    subject = subs{s};
    subject_folder = fullfile(baseDir, subject, 'MEG');

    % Load preprocessed sensor-level MEG data (saved in Script 1)
    sensor_verb_file = fullfile(subject_folder, 'sensor_verb.mat');
    sensor_noise_file = fullfile(subject_folder, 'sensor_noise.mat');
    load(sensor_verb_file, 'v_data');
    load(sensor_noise_file, 'n_data');

    % Remove electrode information if EEG data is also included for simultaneous datasets
    v_data = rmfield(v_data, 'elec');
    n_data = rmfield(n_data, 'elec');

    %% Load & Align MRI for Subject
    T1 = fullfile(baseDir, subject, 'T1.nii');
    mri = ft_read_mri(T1, 'dataformat', 'nifti_spm');

    cfg = [];
    cfg.method = 'flip';
    mri = ft_volumereslice(cfg, mri);

    cfg = [];
    cfg.method = 'interactive';
    cfg.coordsys = 'ctf';
    mri_aligned = ft_volumerealign(cfg, mri);
    save(fullfile(baseDir, subject, 'mri_aligned.mat'), "mri_aligned");

    %% Segment MRI and Create Head Model
    cfg = [];
    cfg.output = {'brain', 'skull', 'scalp'};
    cfg.spmversion = 'spm12';
    segmented_mri = ft_volumesegment(cfg, mri_aligned);
    save(fullfile(baseDir, subject, 'segmented_mri.mat'), "segmented_mri");

    %% Load Template Grid and Prepare Individual Source Model
    load('/path/to/temp_grid.mat', 'template_grid');

    cfg = [];
    cfg.method = 'singleshell';
    individual_headmodel = ft_prepare_headmodel(cfg, segmented_mri);
    save(fullfile(baseDir, subject, 'individual_headmodel.mat'), 'individual_headmodel');

    cfg = [];
    cfg.method = 'basedonmni';
    cfg.template = template_grid;
    cfg.nonlinear = 'yes';
    cfg.mri = mri_aligned;
    individual_grid = ft_prepare_sourcemodel(cfg);
    save(fullfile(baseDir, subject, 'individual_grid.mat'), 'individual_grid');

    %% Compute Leadfield Matrix (Model Input)
    cfg = [];
    cfg.reducerank = 2;
    cfg.sourcemodel = individual_grid;
    cfg.headmodel = individual_headmodel;
    cfg.grad = ft_read_sens(fullfile(subject_folder, '*verbs*'), 'senstype', 'meg');

    % Compute leadfield
    timelock = ft_timelockanalysis([], ft_appenddata([], v_data, n_data));
    sourcemodel = ft_prepare_leadfield(cfg, timelock);
    leadfield = sourcemodel.leadfield;
    save(fullfile(baseDir, subject, 'leadfield.mat'), "leadfield");

    % Convert leadfield into 3D matrix for model input
    nRows = size(leadfield{1}, 1);
    nCols = size(leadfield{1}, 2);
    nCells = numel(leadfield);
    leadfield_3d = zeros(nCells, nRows, nCols);
    for k = 1:nCells
        leadfield_3d(k, :, :) = leadfield{k};
    end
    save(fullfile(baseDir, subject, 'leadfield_3d.mat'), "leadfield_3d");

    %% Source Localization using LCMV Beamforming
    cfg = [];
    cfg.method = 'lcmv';
    cfg.sourcemodel = individual_grid;
    cfg.headmodel = individual_headmodel;
    cfg.grad = ft_read_sens(fullfile(subject_folder, '*verbs*'), 'senstype', 'meg');
    cfg.lcmv.lambda = '.1%';
    cfg.lcmv.keepfilter = 'yes';
    cfg.lcmv.fixedori = 'yes';
    source_verb_noise = ft_sourceanalysis(cfg, timelock);
    save(fullfile(baseDir, subject, 'source_verb_noise.mat'), "source_verb_noise");

    % Source Analysis for Verb and Noise Separately
    source_verb = ft_sourceanalysis(cfg, ft_timelockanalysis([], v_data));
    source_noise = ft_sourceanalysis(cfg, ft_timelockanalysis([], n_data));

    % Normalize by noise projection (NAI computation)
    for tr = 1:length(source_verb.trial)
        for coord = 1:length(source_verb.trial(1).mom)
            source_verb.trial(tr).nai{coord} = source_verb.trial(tr).mom{coord} ./ source_verb.trial(tr).noise(coord);
        end
    end
    for tr = 1:length(source_noise.trial)
        for coord = 1:length(source_noise.trial(1).mom)
            source_noise.trial(tr).nai{coord} = source_noise.trial(tr).mom{coord} ./ source_noise.trial(tr).noise(coord);
        end
    end

    % Assign MNI Coordinates to Source Data
    source_verb.pos = template_grid.pos;
    source_noise.pos = template_grid.pos;
    save(fullfile(baseDir, subject, 'source_verb.mat'), 'source_verb');
    save(fullfile(baseDir, subject, 'source_noise.mat'), 'source_noise');

    %% Save Source-Level Trial Time Series
    verb_trial = {source_verb.trial.mom}.';
    noise_trial = {source_noise.trial.mom}.';
    save(fullfile(baseDir, subject, 'source_verb_trialts.mat'), 'verb_trial');
    save(fullfile(baseDir, subject, 'source_noise_trialts.mat'), 'noise_trial');
    
    fprintf('Source analysis and leadfield computed for subject %s.\n', subject);
end
