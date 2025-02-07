import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.signal
from scipy import stats

# Sampling parameters
fs = 1000  # Sampling frequency (Hz)
nperseg = 512  # Segment length (500 ms)
noverlap = 256  # 50% overlap

# Index of frequency range for beta power corresponding to (13-30 Hz)
start_freq = 7
end_freq = 16

# Define frontal ROIs of shen atlas based on mask (subtract 1 for Python indexing)
frontal_rois = np.array([2, 7, 10, 17, 18, 24, 25, 26, 28, 30, 31, 33,
                         37, 38, 42, 50, 56, 59, 61, 62, 65, 66, 68, 71, 77,
                         78, 83, 91, 92, 94, 96, 98, 99, 100, 101, 102, 103,
                         108, 110, 113, 117, 125, 126, 129, 132, 133, 135, 137,
                         140, 142, 150, 158, 161, 172, 178, 180, 182, 183]) - 1

# Separate left and right hemisphere indices
right_frontal_idx = frontal_rois[frontal_rois < 93]
left_frontal_idx = frontal_rois[frontal_rois > 93]

# Initialize storage lists
adol_emp_verb_psd, adol_emp_noise_psd = [], []
yc_emp_verb_psd, yc_emp_noise_psd = [], []
adol_sim_verb_psd, adol_sim_noise_psd = [], []
yc_sim_verb_psd, yc_sim_noise_psd = [], []

# Compute power spectral density (PSD) using Welch's method for 700-1200 ms window (time series are -500 to 1500 ms)
for i in range(len(Adol_subs)):
    emp_verb = scipy.signal.welch(Adol_emp_verb[i][:, :, 1200:1700], fs=fs, noverlap=noverlap, nperseg=nperseg, detrend='linear')
    emp_noise = scipy.signal.welch(Adol_emp_noise[i][:, :, 1200:1700], fs=fs, noverlap=noverlap, nperseg=nperseg, detrend='linear')

    sim_verb = scipy.signal.welch(Adol_sim_verb[i][:, 800:1300], fs=fs, noverlap=noverlap, nperseg=nperseg, detrend='linear')
    sim_noise = scipy.signal.welch(Adol_sim_noise[i][:, 800:1300], fs=fs, noverlap=noverlap, nperseg=nperseg, detrend='linear')

    adol_emp_verb_psd.append(emp_verb)
    adol_emp_noise_psd.append(emp_noise)
    adol_sim_verb_psd.append(sim_verb)
    adol_sim_noise_psd.append(sim_noise)

for i in range(len(YC_subs)):
    emp_verb = scipy.signal.welch(YC_emp_verb[i][:, :, 1200:1700], fs=fs, noverlap=noverlap, nperseg=nperseg, detrend='linear')
    emp_noise = scipy.signal.welch(YC_emp_noise[i][:, :, 1200:1700], fs=fs, noverlap=noverlap, nperseg=nperseg, detrend='linear')

    sim_verb = scipy.signal.welch(YC_sim_verb[i][:, 800:1300], fs=fs, noverlap=noverlap, nperseg=nperseg, detrend='linear')
    sim_noise = scipy.signal.welch(YC_sim_noise[i][:, 800:1300], fs=fs, noverlap=noverlap, nperseg=nperseg, detrend='linear')

    yc_emp_verb_psd.append(emp_verb)
    yc_emp_noise_psd.append(emp_noise)
    yc_sim_verb_psd.append(sim_verb)
    yc_sim_noise_psd.append(sim_noise)

# Compute beta power averages
def compute_beta_power_difference(emp_verb_psd, emp_noise_psd, sim_verb_psd, sim_noise_psd):
    emp_verb_beta, emp_noise_beta = [], []
    sim_verb_beta, sim_noise_beta = [], []

    for i in range(len(emp_verb_psd)):
        emp_verb_beta.append(np.mean(emp_verb_psd[i][1][:, :, start_freq:end_freq], axis=(2))[frontal_rois])
        emp_noise_beta.append(np.mean(emp_noise_psd[i][1][:, :, start_freq:end_freq], axis=(2))[frontal_rois])

        sim_verb_beta.append(np.mean(sim_verb_psd[i][1][:, start_freq:end_freq], axis=1)[frontal_rois])
        sim_noise_beta.append(np.mean(sim_noise_psd[i][1][:, start_freq:end_freq], axis=1)[frontal_rois])

    emp_beta_diff = np.array(emp_verb_beta) - np.array(emp_noise_beta)
    sim_beta_diff = np.array(sim_verb_beta) - np.array(sim_noise_beta)

    return emp_beta_diff, sim_beta_diff

# Compute beta power differences for both groups
adol_emp_beta_diff, adol_sim_beta_diff = compute_beta_power_difference(adol_emp_verb_psd, adol_emp_noise_psd, adol_sim_verb_psd, adol_sim_noise_psd)
yc_emp_beta_diff, yc_sim_beta_diff = compute_beta_power_difference(yc_emp_verb_psd, yc_emp_noise_psd, yc_sim_verb_psd, yc_sim_noise_psd)

# Compute mean beta power for left and right frontal regions
def compute_mean_beta_per_hemisphere(emp_beta_diff, sim_beta_diff):
    right_emp_avg = np.mean(emp_beta_diff[:, right_frontal_idx], axis=1)
    left_emp_avg = np.mean(emp_beta_diff[:, left_frontal_idx], axis=1)

    right_sim_avg = np.mean(sim_beta_diff[:, right_frontal_idx], axis=1)
    left_sim_avg = np.mean(sim_beta_diff[:, left_frontal_idx], axis=1)

    return pd.DataFrame({'Empirical_Left': left_emp_avg, 'Empirical_Right': right_emp_avg,
                         'Simulated_Left': left_sim_avg, 'Simulated_Right': right_sim_avg})

adol_beta_df = compute_mean_beta_per_hemisphere(adol_emp_beta_diff, adol_sim_beta_diff)
yc_beta_df = compute_mean_beta_per_hemisphere(yc_emp_beta_diff, yc_sim_beta_diff)

# Normalize with sign preservation
adol_beta_df = adol_beta_df.apply(lambda x: x / np.abs(x).max())
yc_beta_df = yc_beta_df.apply(lambda x: x / np.abs(x).max())

# Function to plot results
def plot_beta_barplot(beta_df, title, filename):
    mean_values = beta_df.mean()
    sem_values = beta_df.sem()

    labels = ['Empirical', 'Simulated']
    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(3, 3), dpi=300)

    ax.bar(x - width / 2, [mean_values['Empirical_Left'], mean_values['Simulated_Left']], width,
           yerr=[sem_values['Empirical_Left'], sem_values['Simulated_Left']], label='Left Frontal',
           capsize=5, color='#6a9ef9', edgecolor='#6a9ef9')

    ax.bar(x + width / 2, [mean_values['Empirical_Right'], mean_values['Simulated_Right']], width,
           yerr=[sem_values['Empirical_Right'], sem_values['Simulated_Right']], label='Right Frontal',
           capsize=5, color='#e97773', edgecolor='#e97773')

    ax.set_ylabel('Noun-Noise Beta Power', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    plt.axhline(0, color='black', linewidth=1)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    ax.set_ylim(-0.6, 0.6)

    fig.savefig(filename, dpi=300, bbox_inches='tight')
    plt.show()

# Plot results
plot_beta_barplot(adol_beta_df, "Adolescents Beta Power", "adol_beta_plot.png")
plot_beta_barplot(yc_beta_df, "Young Children Beta Power", "yc_beta_plot.png")

import numpy as np

# Function to compute Laterality Index (LI)
def compute_laterality_index(beta_power_diff):
    """
    Computes the Laterality Index (LI) based on beta power differences
    between left and right frontal regions.

    LI = (# Positive in Right + # Negative in Left) - (# Negative in Right + # Positive in Left)
         --------------------------------------------------------------------------------------
                                   Total Number of Regions (58)
    
    Args:
        beta_power_diff (numpy array): Array of beta power differences (size 58)
    
    Returns:
        float: Computed Laterality Index (LI)
    """
    num_pos_right = np.sum(beta_power_diff[:29] > 0)
    num_neg_right = np.sum(beta_power_diff[:29] <= 0)
    
    num_pos_left = np.sum(beta_power_diff[29:] > 0)
    num_neg_left = np.sum(beta_power_diff[29:] <= 0)

    # Compute LI
    num = (num_pos_right + num_neg_left) - (num_neg_right + num_pos_left)
    den = len(beta_power_diff)  # 58 regions in total

    return num / den if den != 0 else float('nan')

# Compute LI for Adolescents (Empirical vs. Simulated)
adol_emp_beta_diff = np.mean(bytrial_avg_adols_fr_beta_diff, axis=0)
adol_sim_beta_diff = np.mean(adols_sim_beta_diff, axis=0)

adol_emp_LI = compute_laterality_index(adol_emp_beta_diff)
adol_sim_LI = compute_laterality_index(adol_sim_beta_diff)

print(f"Adolescent Empirical LI: {adol_emp_LI:.4f}")
print(f"Adolescent Simulated LI: {adol_sim_LI:.4f}")

# Compute LI for Young Children (Empirical vs. Simulated)
yc_emp_beta_diff = np.mean(bytrial_avg_yc_fr_beta_diff, axis=0)
yc_sim_beta_diff = np.mean(yc_sim_beta_diff, axis=0)

yc_emp_LI = compute_laterality_index(yc_emp_beta_diff)
yc_sim_LI = compute_laterality_index(yc_sim_beta_diff)

print(f"Young Children Empirical LI: {yc_emp_LI:.4f}")
print(f"Young Children Simulated LI: {yc_sim_LI:.4f}")

