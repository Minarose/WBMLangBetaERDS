%% MEG Preprocessing Script using FieldTrip
% This script processes MEG data using FieldTrip.
% It performs preprocessing, artifact rejection, resampling, independent 
% component analysis (ICA), and component rejection for both "verb" and 
% "noise" trials. Cleaned data and trial information are then saved for 
% further analysis.
%
% Requirements:
%   - FieldTrip toolbox (https://www.fieldtriptoolbox.org/)
%   - Data organized by subject in a base directory, with a subfolder "MEG"
%     containing the dataset. The .ds filename contains a 
%     distinguishing keyword ('verbs') used to locate the file.
%
% Instructions:
%   1. Update the paths for FieldTrip and your data.
%   2. Update the list of subjects.
%   3. Adjust trial definition and processing parameters as needed.
%   4. Run the script in MATLAB.

clear all; close all; clc;

%% Add FieldTrip to the MATLAB path
% Replace the path below with the location of your FieldTrip installation.
addpath('/path/to/fieldtrip');
ft_defaults;  % Initialize FieldTrip defaults

%% Define Subjects and Base Directory
% List the subject IDs you wish to process.
subs = {'Subject01', 'Subject02'};  % Subject IDs

% Define the base directory where each subject folder is located.
base_folder = '/path/to/your/data/';  % Update to your data directory

%% Loop through each subject
for s = 1:length(subs)
    subject = subs{s};
    
    % Construct the full path to the subject's folder
    subject_folder = fullfile(base_folder, subject);
    
    % Define the MEG data folder
    meg_folder = fullfile(subject_folder, 'MEG');
    
    % Locate the dataset file containing 'verbs' in its filename (for both noise and verb data)
    files = dir(meg_folder);
    file_names = {files.name};
    idx = contains(file_names, 'verbs');
    
    if ~any(idx)
        warning('No dataset file found in %s containing "verbs".', meg_folder);
        continue;
    end
    dataset = fullfile(meg_folder, file_names{idx});
    
    %% Process "Verb" Trials
    % Configure preprocessing parameters for the "verb" condition.
    cfg = [];
    cfg.dataset    = dataset;
    cfg.channel    = {'MEG', '-MLC12'};  % Exclude channel 'MLC12'
    cfg.dftfilter  = 'yes';
    cfg.dftfreq    = [60 120 180];
    cfg.lpfilter   = 'yes';
    cfg.lpfreq     = 40;
    cfg.hpfilter   = 'yes';
    cfg.hpfreq     = 1;
    cfg.demean     = 'yes';
    
    % Define trial parameters: here we use 'noun' as the event type for "verb" trials.
    cfg.trialfun         = 'ft_trialfun_general';
    cfg.trialdef.eventtype = 'noun';
    cfg.trialdef.prestim   = 0.5;
    cfg.trialdef.poststim  = 1.5;
    
    % Define the trials
    cfg = ft_definetrial(cfg);
    
    % Preprocess the data (filtering, epoching, etc.)
    verb = ft_preprocessing(cfg);
    
    % Artifact rejection: detect jump artifacts
    cfg = ft_artifact_jump(cfg);         
    verb_data = ft_rejectartifact(cfg, verb);
    
    % Resample data to 1000 Hz and perform baseline correction
    cfg = [];
    cfg.resamplefs    = 1000;
    cfg.demean        = 'yes';
    cfg.baselinewindow = [-0.5 0];
    rs_verb = ft_resampledata(cfg, verb_data);
    
    % Perform ICA to decompose the signal into components
    cfg = []; 
    cfg.channel      = 'MEG';
    cfg.method       = 'runica'; 
    cfg.numcomponent = 20;
    comp = ft_componentanalysis(cfg, rs_verb);
    
    % Visualize ICA components for manual selection of artifact components
    cfg = [];
    cfg.layout   = 'CTF275.lay';  % Update if using a different sensor layout
    cfg.viewmode = 'component';
    ft_databrowser(cfg, comp);
    
    % Prompt the user to input which components to remove
    prompt = "Which components to remove? (e.g., [1 2 3]): ";
    reject_x = input(prompt);
    
    % Remove the selected components from the data
    cfg = [];
    cfg.component = reject_x;  % components to remove
    v_data = ft_rejectcomponent(cfg, comp, rs_verb);

    % Extract trials & Average across trials
    verb_trials = cat(3, v_data.trial{:});  % Convert cell array to 3D matrix
    verb_avg = mean(verb_trials, 3);  % Average over trials
    
    
    %% Process "Noise" Trials
    % Configure preprocessing parameters for the "noise" condition.
    cfg = [];
    cfg.dataset    = dataset;
    cfg.channel    = {'MEG', '-MLC12'};
    cfg.dftfilter  = 'yes';
    cfg.dftfreq    = [60 120 180];
    cfg.lpfilter   = 'yes';
    cfg.lpfreq     = 40;
    cfg.hpfilter   = 'yes';
    cfg.hpfreq     = 1;
    cfg.demean     = 'yes';
    
    % Define trial parameters: now use 'noise' as the event type.
    cfg.trialfun         = 'ft_trialfun_general';
    cfg.trialdef.eventtype = 'noise';
    cfg.trialdef.prestim   = 0.5;
    cfg.trialdef.poststim  = 1.5;
    
    % Define the trials for noise data
    cfg = ft_definetrial(cfg);
    
    % Preprocess the noise data
    noise = ft_preprocessing(cfg);
    
    % Artifact rejection for noise data (jump artifact detection)
    [cfg, artifact] = ft_artifact_jump(cfg);          
    noise_data = ft_rejectartifact(cfg, noise);
    
    % Resample and apply baseline correction to noise data
    cfg = [];
    cfg.resamplefs    = 1000;
    cfg.demean        = 'yes';
    cfg.baselinewindow = [-0.5 0];
    rs_noise = ft_resampledata(cfg, noise_data);
    
    % Perform ICA on noise data
    cfg = []; 
    cfg.channel      = 'MEG';
    cfg.method       = 'runica'; 
    cfg.numcomponent = 20;
    comp = ft_componentanalysis(cfg, rs_noise);
    
    % Visualize ICA components for noise data
    cfg = [];
    cfg.layout   = 'CTF275.lay';
    cfg.viewmode = 'component';
    ft_databrowser(cfg, comp);
    
    % Prompt the user to input which components to remove for noise data
    prompt = "Which components to remove for noise? (e.g., [1 2 3]): ";
    reject_x = input(prompt);
    
    % Remove the selected components from the noise data
    cfg = [];
    cfg.component = reject_x; 
    n_data = ft_rejectcomponent(cfg, comp, rs_noise);

    % Extract trials & Average across trials
    noise_trials = cat(3, n_data.trial{:});  % Convert cell array to 3D matrix
    noise_avg = mean(noise_trials, 3);  % Average over trials

    %% SAVE AS NUMPY FILES
    npy_path = fullfile(subject_folder, 'preprocessed');
    if ~exist(npy_path, 'dir')
        mkdir(npy_path);
    end

    % Save averaged time series as .npy
    verb_npy_file = fullfile(npy_path, 'verb.npy');
    noise_npy_file = fullfile(npy_path, 'noise.npy');
    
    % Use Python's NumPy to save as .npy
    py.numpy.save(verb_npy_file, verb_avg);
    py.numpy.save(noise_npy_file, noise_avg);

    fprintf('Saved NumPy arrays for subject: %s\n', subject);

    %%%%%%% save sensor trial data (un-averaged) for source localization in script 4
    n_trial = {n_data.trial}.';
    path = fullfile(dir_folder,'noise_sensor_trials.mat');
    save(path,'n_trial')

    v_trial = {v_data.trial}.';
    path = fullfile(dir_folder,'verb_sensor_trials.mat');
    save(path,'v_trial')
    
end
