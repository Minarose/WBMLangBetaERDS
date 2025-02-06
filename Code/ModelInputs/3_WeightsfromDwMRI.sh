#!/bin/bash
#SBATCH --mail-user=your.email@example.com         # Replace with your email address
#SBATCH --mail-type=FAIL
#SBATCH --mail-type=END
#SBATCH --job-name='diffusion_prepro'
#SBATCH --account=your_account                      # Replace with your account name
#SBATCH -N 1
#SBATCH --cpus-per-task=15
#SBATCH --mem=32G
#SBATCH --tmp=80G
#SBATCH --time=3-00:00:00
#SBATCH --gpus=1

# Number of threads to use (adjust as needed)
export cores=13

##############################################
# Load required modules
##############################################
module load ANTs/2.3.2
module load dcm2niix/1.0.20211006
module load freesurfer/7.3.2
module load fsl/6.0.0_cuda_11.2
source ${FSLDIR}/etc/fslconf/fsl.sh
module load mrtrix3/3.0.3

##############################################
# Define Variables and Paths
##############################################
# List of subjects to process (update with your subject IDs)
subs=("Subject01" "Subject02" "Subject03")

# Define key directories (update these to match your environment)
DATA_DIR="/path/to/data"                      # Base directory where subject DTI, T1 data AND 
                                              # shen atlas image in indiv space are stored extracted in script 2
SCRATCH_DIR="/path/to/scratch"                # Local scratch directory for processing
FINAL_DEST="/path/to/final/destination"       # Final destination for processed data
SL_ORDER_FILE="/path/to/sl_order.txt"         # Shell order file used for eddy correction (if needed)

##############################################
# Processing Pipeline for Each Subject
##############################################
for i in ${!subs[@]}; do
    echo "Processing subject ${subs[$i]} (index #${i})"
    
    # Copy subject DTI data to local scratch for faster I/O
    cp -R "${DATA_DIR}/${subs[$i]}/DTI" "${SCRATCH_DIR}/${subs[$i]}"
    cd "${SCRATCH_DIR}"
    
    # (Optional) List files/directories for verification
    ls "${subs[$i]}"
    
    # Convert DICOM to NIFTI using dcm2niix
    dcm2niix -f "%f_%p_%s" -b n -p y -z y "${subs[$i]}"
    cd "${subs[$i]}"
    
    # Compress the T1-weighted image and adjust permissions
    gzip T1W.nii
    chmod -R +rwx *
    
    ##############################################
    # Locate Files Dynamically
    ##############################################
    # Adjust the name patterns as needed to match your file naming convention
    B1000_2000NIFTI=$(find . -type f -name '*2shell*' -and -name '*.nii.gz')
    B3000NIFTI=$(find . -type f -name '*1shell*' -and -name '*.nii.gz')
    B1000_2000bvec=$(find . -type f -name '*2shell*' -and -name '*.bvec')
    B1000_2000bval=$(find . -type f -name '*2shell*' -and -name '*.bval')
    B3000bvec=$(find . -type f -name '*1shell*' -and -name '*.bvec')
    B3000bval=$(find . -type f -name '*1shell*' -and -name '*.bval')
    B0NIFTI=$(find . -type f -name '*EPI*' -and -name '*.nii.gz')
    T1NIFTI=$(find . -type f -name '*T1*' -and -name '*.nii.gz')
    
    echo "T1 image found: $T1NIFTI"
    
    # Ensure all essential files are present
    if [[ -z "$B1000_2000NIFTI" || -z "$B3000NIFTI" || -z "$B0NIFTI" || -z "$T1NIFTI" ]]; then
        echo "Error: Essential files missing for subject ${subs[$i]}"
        exit 1
    fi

    ##############################################
    # Convert NIFTI to MRtrix (.mif) Format
    ##############################################
    mrconvert "$B1000_2000NIFTI" b1000_2000.mif -fslgrad "$B1000_2000bvec" "$B1000_2000bval"
    mrconvert "$B3000NIFTI" b3000.mif -fslgrad "$B3000bvec" "$B3000bval"
    mrconvert "$B0NIFTI" b0.mif

    # Concatenate multi-shell images into a single DWI file
    mrcat b1000_2000.mif b3000.mif raw_dwi.mif

    ##############################################
    # Denoising and Gibbs Ringing Correction
    ##############################################
    dwidenoise raw_dwi.mif dwi_den.mif -noise noise.mif -nthreads $cores
    mrdegibbs dwi_den.mif dwi_den_unr.mif -nthreads $cores

    ##############################################
    # Preprocessing: b0 Extraction and Mean Image Calculation
    ##############################################
    dwiextract dwi_den_unr.mif - -bzero | mrmath - mean mean_b0_AP.mif -axis 3
    mrconvert b0.mif - | mrmath - mean mean_b0_PA.mif -axis 3
    mrcat mean_b0_AP.mif mean_b0_PA.mif -axis 3 b0_pair.mif

    ##############################################
    # Eddy-Current and Motion Correction
    ##############################################
    dwifslpreproc dwi_den_unr.mif dwi_den_unr_preproc.mif \
        -pe_dir AP -rpe_pair -se_epi b0_pair.mif \
        -readout_time 0.0687 -eddyqc_all eddyqc_all \
        -eddy_slspec="${SL_ORDER_FILE}" \
        -eddy_options "--slm=linear --repol --mporder=12 --data_is_shelled" \
        -nthreads $cores

    ##############################################
    # Bias Field Correction and Masking
    ##############################################
    dwibiascorrect ants dwi_den_unr_preproc.mif dwi_den_unr_preproc_unbiased.mif \
        -bias bias.mif -nthreads $cores
    dwi2mask dwi_den_unr_preproc_unbiased.mif mask_den_unr_preproc_unb.mif -nthreads $cores

    ##############################################
    # Response Function Estimation and FOD Computation
    ##############################################
    dwi2response dhollander dwi_den_unr_preproc_unbiased.mif wm.txt gm.txt csf.txt \
        -voxels voxels.mif -nthreads $cores
    dwi2fod msmt_csd dwi_den_unr_preproc_unbiased.mif -mask mask_den_unr_preproc_unb.mif \
        wm.txt wmfod.mif gm.txt gmfod.mif csf.txt csffod.mif -nthreads $cores

    # Normalize the FOD images
    mtnormalise wmfod.mif wmfod_norm.mif gmfod.mif gmfod_norm.mif csffod.mif csffod_norm.mif \
        -mask mask_den_unr_preproc_unb.mif -nthreads $cores

    ##############################################
    # T1 to DWI Coregistration
    ##############################################
    bet "$T1NIFTI" T1_bet.nii.gz
    5ttgen fsl -premasked T1_bet.nii.gz 5tt_nocoreg.mif -nthreads $cores
    dwiextract dwi_den_unr_preproc_unbiased.mif - -bzero | mrmath - mean mean_b0_preprocessed.mif -axis 3
    mrconvert mean_b0_preprocessed.mif mean_b0_preprocessed.nii
    flirt -in mean_b0_preprocessed.nii -ref T1_bet.nii.gz -dof 6 -omat diff2struct_fsl.mat
    transformconvert diff2struct_fsl.mat mean_b0_preprocessed.nii T1_bet.nii.gz \
        flirt_import diff2struct_mrtrix.txt
    mrconvert T1_bet.nii.gz T1_raw.mif
    mrtransform T1_raw.mif -linear diff2struct_mrtrix.txt -inverse T1_coreg.mif
    mrtransform 5tt_nocoreg.mif -linear diff2struct_mrtrix.txt -inverse 5tt_coreg.mif

    ##############################################
    # Streamline Generation and Connectome Creation
    ##############################################
    5tt2gmwmi 5tt_coreg.mif gmwmSeed_coreg.mif -nthreads $cores
    tckgen -act 5tt_coreg.mif -backtrack -seed_gmwmi gmwmSeed_coreg.mif \
        -select 100000000 wmfod_norm.mif tracts_100million.tck -nthreads $cores
    tcksift2 -act 5tt_coreg.mif tracts_100million.tck wmfod_norm.mif \
        sift2_100million.txt -nthreads $cores    
    
    ##############################################
    # Shen Atlas Processing for Connectome Creation
    ##############################################
    # The Shen atlas is used here to parcellate the brain. The output
    # file "shen_indiv.csv" is the weights matrix that will be used as input
    # to your model for connectome-based analysis.
    dti_dir="${SCRATCH_DIR}/${subs[$i]}"
    shen_file=$(find "$dti_dir" -type f -name "*shen_in_individual_space*.nii")  #this is created in script 2
    if [[ -z "$shen_file" ]]; then
        echo "Error: Shen atlas file not found in DTI directory for subject ${subs[$i]}"
        exit 1
    fi
    mrconvert "$shen_file" shen_indiv.mif -force
    mrtransform shen_indiv.mif -interp nearest -linear diff2struct_mrtrix.txt \
        -inverse -datatype uint32 shen_diff_coreg.mif
    tck2connectome -symmetric -zero_diagonal -scale_invnodevol \
        -tck_weights_in sift2_100million.txt tracts_100million.tck \
        shen_diff_coreg.mif shen_indiv.csv \
        -out_assignment shen_assignment_parcels_coreg.csv

    # IMPORTANT:
    # The file "shen_indiv.csv" generated above is the weights matrix which
    # should be used as the input to your downstream model.

    ##############################################
    # Move Processed Data to Final Destination
    ##############################################
    echo "Moving files to final destination..."
    mv "${SCRATCH_DIR}/${subs[$i]}" "${FINAL_DEST}"
    echo "Completed processing for subject ${subs[$i]}"
done
