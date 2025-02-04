%% Pipeline for Generating Subject-Specific Shen Atlas & Distance Matrix
%
% This pipeline consists of three parts:
%
% 1. Generate a subject-specific Shen atlas in individual space using SPM.
% 2. Extract parcel centroids from the subject-specific Shen atlas.
% 3. Compute the Euclidean distance matrix (the final output) from these centroids.
%
% The final output (saved as "distance.txt" in each subject’s nMR folder) is the
% distance matrix that should be used as the distnace matrix input to your model.
%
% Before running, update the paths below and ensure SPM is on your MATLAB path.

%% =================== PART 0: Configuration & Setup ========================
% List of subjects (update with your subject IDs)
subjectNames = {...
    'Subject01', 'Subject02', 'Subject03' ...
    % add more subjects as needed
};

% Base directory where subject data are stored. For each subject, it is assumed
% that the T1 image is in:    <baseDir>/<subject>/nMR/T1/
baseDir = '/path/to/subject/data';

% Path to the standard Shen atlas (to be normalized into subject space)
shenAtlasPath = '/path/to/shen_atlas.nii';

% Path to the SPM TPM file (e.g. from SPM12)
spmTemplate = '/path/to/spm12/tpm/TPM.nii';

% Temporary directory for writing intermediate parcel images (for centroid extraction)
tempDir = fullfile('/path/to/temp', 'atlas_breakout');
if ~exist(tempDir, 'dir')
    mkdir(tempDir);
end

% Set SPM defaults (make sure SPM is installed)
spm('defaults', 'FMRI');

%% =================== PART 1: Generate Subject-Specific Shen Atlas ========================
% For each subject, we segment the T1 image and then apply the inverse deformation 
% to the standard Shen atlas so that it is in the subject’s native (individual) space.
for i = 1:length(subjectNames)
    subject = subjectNames{i};
    fprintf('\n=== Processing subject: %s ===\n', subject);
    
    % Define the subject’s T1 directory (update folder names if needed)
    subjectT1Dir = fullfile(baseDir, subject, 'nMR', 'T1');
    cd(subjectT1Dir);
    
    % Check for the T1-weighted image (assumed name: T1W.nii)
    t1File = fullfile(subjectT1Dir, 'T1W.nii');
    if ~isfile(t1File)
        error('T1 file not found for subject %s in %s', subject, subjectT1Dir);
    end
    
    %%% SPM Segmentation & Warp Inversion to Obtain Inverse Deformation %%%
    % The segmentation job will write the inverse deformation field (e.g., y_T1W.nii)
    % which will be used to normalize the standard Shen atlas.
    clear matlabbatch;
    matlabbatch{1}.spm.spatial.preproc.channel.vols = {t1File};
    matlabbatch{1}.spm.spatial.preproc.channel.biasreg = 0.001;
    matlabbatch{1}.spm.spatial.preproc.channel.biasfwhm = 60;
    matlabbatch{1}.spm.spatial.preproc.channel.write = [0 0];
    % Configure tissue classes (here we use 6 tissues; adjust as needed)
    for t = 1:6
        matlabbatch{1}.spm.spatial.preproc.tissue(t).tpm = {sprintf('%s,%d', spmTemplate, t)};
        % Here we set number of Gaussians; adjust according to your preference:
        if t == 3
            matlabbatch{1}.spm.spatial.preproc.tissue(t).ngaus = 2;
        elseif t == 4
            matlabbatch{1}.spm.spatial.preproc.tissue(t).ngaus = 3;
        elseif t == 5
            matlabbatch{1}.spm.spatial.preproc.tissue(t).ngaus = 4;
        elseif t == 6
            matlabbatch{1}.spm.spatial.preproc.tissue(t).ngaus = 2;
        else
            matlabbatch{1}.spm.spatial.preproc.tissue(t).ngaus = 1;
        end
        matlabbatch{1}.spm.spatial.preproc.tissue(t).native = [0 0];
        matlabbatch{1}.spm.spatial.preproc.tissue(t).warped = [0 0];
    end
    matlabbatch{1}.spm.spatial.preproc.warp.mrf = 1;
    matlabbatch{1}.spm.spatial.preproc.warp.cleanup = 1;
    matlabbatch{1}.spm.spatial.preproc.warp.reg = [0 0.001 0.5 0.05 0.2];
    matlabbatch{1}.spm.spatial.preproc.warp.affreg = 'mni';
    matlabbatch{1}.spm.spatial.preproc.warp.fwhm = 0;
    matlabbatch{1}.spm.spatial.preproc.warp.samp = 3;
    % Write both the deformation field and the inverse deformation field
    matlabbatch{1}.spm.spatial.preproc.warp.write = [1 1];
    
    % Run the segmentation job (this produces, among other files, the inverse deformation field y_T1W.nii)
    spm_jobman('run', matlabbatch);
    
    %%% Normalize the Standard Shen Atlas into Subject Space %%%
    % Use the inverse deformation field (e.g., y_T1W.nii) to transform the standard atlas.
    % (The function spm_deformations is used here; if not available, see SPM documentation for alternative methods.)
    defField = fullfile(subjectT1Dir, 'y_T1W.nii'); % Inverse deformation field output
    outAtlas = fullfile(subjectT1Dir, [subject, '_shen_in_individual_space_shen_atlas.nii']);
    if ~isfile(defField)
        error('Inverse deformation field not found for subject %s', subject);
    end
    % The following call applies the inverse deformation to the standard atlas.
    spm_deformations('inverse', defField, shenAtlasPath, outAtlas);
    
    fprintf('Subject-specific Shen atlas generated for %s\n', subject);
    cd(baseDir);
end

%% =================== PART 2: Extract Parcel Centroids from Shen Atlas ========================
% For each subject, we load the subject-specific Shen atlas (now in individual space),
% split it into parcels, and compute the centroid (x, y, z in mm) for each parcel.
for i = 1:length(subjectNames)
    subject = subjectNames{i};
    % Assume the subject-specific Shen atlas is now saved in the nMR folder
    subjectnMRDir = fullfile(baseDir, subject, 'nMR');
    shenAtlasFile = fullfile(subjectnMRDir, [subject, '_shen_in_individual_space_shen_atlas.nii']);
    if ~isfile(shenAtlasFile)
        error('Shen atlas file not found for subject %s in %s', subject, subjectnMRDir);
    end
    fprintf('\nExtracting centroids for subject: %s\n', subject);
    
    % Load the atlas image using SPM
    V = spm_vol(shenAtlasFile);
    atlasData = spm_read_vols(V);
    
    % Get the unique parcel labels (assume background = 0)
    uniqueLabels = unique(atlasData);
    uniqueLabels = uniqueLabels(uniqueLabels ~= 0);
    numParcels = length(uniqueLabels);
    
    % (Optional) Write out each parcel as an individual NIfTI for debugging.
    for label = uniqueLabels'
        parcelFile = fullfile(tempDir, sprintf('%03d.nii', label));
        expression = sprintf('i1>(%f-0.1) & i1<(%f+0.1)', label, label);
        spm_imcalc({shenAtlasFile}, parcelFile, expression);
    end
    
    % Compute centroids (in subject space) for each parcel.
    centroids = zeros(numParcels, 3); % to store [x y z] coordinates
    parcelFiles = dir(fullfile(tempDir, '*.nii'));
    for p = 1:length(parcelFiles)
        pf = fullfile(tempDir, parcelFiles(p).name);
        Vp = spm_vol(pf);
        data = spm_read_vols(Vp);
        idx = find(data > 0.001);
        if isempty(idx)
            warning('No voxels found in parcel file: %s', parcelFiles(p).name);
            continue;
        end
        [x, y, z] = ind2sub(size(data), idx);
        % Convert voxel indices to mm coordinates using the affine matrix
        coords = Vp.mat * [x, y, z, ones(length(x), 1)]';
        coords = coords(1:3, :)';
        centroids(p, :) = mean(coords, 1);
    end
    
    % Save the centroid coordinates to a text file (for later use)
    centroidFile = fullfile(subjectnMRDir, 'shen_centroid.txt');
    writematrix(centroids, centroidFile, 'Delimiter', '\t');
    fprintf('Centroids saved for subject %s at:\n%s\n', subject, centroidFile);
end

%% =================== PART 3: Compute Euclidean Distance Matrix ========================
% For each subject, read the centroid file and compute the pairwise Euclidean
% distances between parcels. The resulting matrix is saved as "distance.txt" and
% serves as the final output (i.e. the weights matrix input to your model).
for i = 1:length(subjectNames)
    subject = subjectNames{i};
    subjectnMRDir = fullfile(baseDir, subject, 'nMR');
    centroidFile = fullfile(subjectnMRDir, 'shen_centroid.txt');
    if ~isfile(centroidFile)
        error('Centroid file not found for subject %s in %s', subject, subjectnMRDir);
    end
    centroids = readmatrix(centroidFile);
    numCentroids = size(centroids, 1);
    distanceMatrix = zeros(numCentroids, numCentroids);
    
    for m = 1:numCentroids
        for n = 1:numCentroids
            distanceMatrix(m, n) = norm(centroids(m, :) - centroids(n, :));
        end
    end
    
    % Save the distance matrix to a text file (tab-delimited)
    outputDistanceFile = fullfile(subjectnMRDir, 'distance.txt');
    writematrix(distanceMatrix, outputDistanceFile, 'Delimiter', '\t');
    fprintf('Distance matrix saved for subject %s at:\n%s\n', subject, outputDistanceFile);
end

%% =================== End of Pipeline ========================
% The pipeline above:
%   1. Generates a subject-specific Shen atlas by segmenting the T1 image and
%      applying the inverse deformation to the standard Shen atlas.
%   2. Extracts the centroids of each atlas parcel.
%   3. Computes the Euclidean distance matrix between centroids.
%
% The final output for each subject (distance.txt) is the distance matrix that
% should be used as input to your model.
