import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind, linregress

# -----------------------------
# Function to Compute Empirical LI
# -----------------------------
def compute_empirical_LI(v_beta, n_beta, idx, subjects):
    """
    Computes empirical Laterality Index (LI) for each subject.

    Args:
        v_beta (list): Beta power during verb trials.
        n_beta (list): Beta power during noise trials.
        idx (array): Indices of brain regions.
        subjects (list): List of subject IDs.

    Returns:
        significant_regions (dict): Regions with significant beta differences.
        LI_results (dict): Computed LI values per subject.
        LI_neg_results (dict): Computed LI_neg values per subject.
    """
    significant_regions = {}
    LI_results = {}
    LI_neg_results = {}

    for s, subj in enumerate(subjects):
        sig_positive_regions = []
        sig_negative_regions = []
        t_stats = []

        # Perform t-tests per region
        for i in range(len(idx)):
            t_stat, p = ttest_ind(v_beta[s][i], n_beta[s][i], equal_var=False)
            t_stats.append(t_stat)
            if p < 0.05:
                if t_stat > 0:
                    sig_positive_regions.append(i)
                else:
                    sig_negative_regions.append(i)

        significant_regions[subj] = {'positive': sig_positive_regions, 'negative': sig_negative_regions}

        # Count occurrences in left and right hemispheres
        counts = [0, 0, 0, 0]  # pos_right, neg_right, pos_left, neg_left
        for i in sig_positive_regions + sig_negative_regions:
            right = i < len(idx) / 2
            if t_stats[i] > 0:
                counts[0 if right else 2] += 1
            else:
                counts[1 if right else 3] += 1

        # Compute LI and LI_neg
        num = counts[0] + counts[3] - (counts[1] + counts[2])
        den = sum(counts)
        LI_results[subj] = num / den if den != 0 else float('nan')

        num_neg = counts[3] - counts[1]
        den_neg = counts[3] + counts[1]
        LI_neg_results[subj] = num_neg / den_neg if den_neg != 0 else float('nan')

    return significant_regions, LI_results, LI_neg_results


# -----------------------------
#   Function to Compute Simulated LI (Using Significant Regions from Empirical Data)
# -----------------------------
def compute_simulated_LI(v_beta, n_beta, idx, subjects, significant_regions):
    """
    Computes simulated Laterality Index (LI) using significant regions from empirical data.

    Args:
        v_beta (list): Simulated beta power for verb trials.
        n_beta (list): Simulated beta power for noise trials.
        idx (array): Indices of brain regions.
        subjects (list): List of subject IDs.
        significant_regions (dict): Significant regions from empirical data.

    Returns:
        LI_results (dict): Computed simulated LI values per subject.
        LI_neg_results (dict): Computed simulated LI_neg values per subject.
    """
    LI_results = {}
    LI_neg_results = {}

    for s, subj in enumerate(subjects):
        sig_regions = significant_regions[subj]
        sig_pos_regions = sig_regions['positive']
        sig_neg_regions = sig_regions['negative']
        counts = [0, 0, 0, 0]  # pos_right, neg_right, pos_left, neg_left

        # Evaluate simulated beta power in significant regions
        for region in sig_pos_regions + sig_neg_regions:
            diff = v_beta[s][region] - n_beta[s][region]
            right = region < len(idx) / 2
            if diff > 0:
                counts[0 if right else 2] += 1
            else:
                counts[1 if right else 3] += 1

        num = counts[0] + counts[3] - (counts[1] + counts[2])
        den = sum(counts)
        LI_results[subj] = num / den if den != 0 else float('nan')

        num_neg = counts[3] - counts[1]
        den_neg = counts[3] + counts[1]
        LI_neg_results[subj] = num_neg / den_neg if den_neg != 0 else float('nan')

    return LI_results, LI_neg_results


# -----------------------------
#  Compute LI for Each Group
# -----------------------------
significant_regions_A, LI_emp_A, LI_neg_emp_A = compute_empirical_LI(Aemp_v_beta, Aemp_n_beta, idx, Adol_subs)
LI_sim_A, LI_neg_sim_A = compute_simulated_LI(Asim_v_beta, Asim_n_beta, idx, Adol_subs, significant_regions_A)

significant_regions_Y, LI_emp_Y, LI_neg_emp_Y = compute_empirical_LI(Yemp_v_beta, Yemp_n_beta, idx, YC_subs)
LI_sim_Y, LI_neg_sim_Y = compute_simulated_LI(Ysim_v_beta, Ysim_n_beta, idx, YC_subs, significant_regions_Y)


# -----------------------------
#  Prepare Data for Plotting
# -----------------------------
def prepare_data(group_name, subjects, LI_emp, LI_neg_emp, LI_sim, LI_neg_sim):
    return pd.DataFrame({
        'Group': group_name,
        'Subject': subjects,
        'Age': [int(sub[7:9]) for sub in subjects],
        'LI_emp': [LI_emp[sub] for sub in subjects],
        'LI_neg_emp': [LI_neg_emp[sub] for sub in subjects],
        'LI_sim': [LI_sim[sub] for sub in subjects],
        'LI_neg_sim': [LI_neg_sim[sub] for sub in subjects]
    })


# Combine all data into a single DataFrame
all_data = pd.concat([
    prepare_data('Adolescents', Adol_subs, LI_emp_A, LI_neg_emp_A, LI_sim_A, LI_neg_sim_A),
    prepare_data('Young Children', YC_subs, LI_emp_Y, LI_neg_emp_Y, LI_sim_Y, LI_neg_sim_Y)
], ignore_index=True)


# -----------------------------
#  Plot Empirical & Simulated LI vs. Age
# -----------------------------
def plot_LI_vs_age(df):
    """
    Plots Laterality Index (LI) vs. Age, including linear regression.

    Args:
        df (DataFrame): Data containing 'Age', 'LI_emp', and 'LI_sim'.
    """
    plt.figure(figsize=(6, 5), dpi=300)

    # Scatter plots
    plt.scatter(df['Age'], df['LI_emp'], color='black', marker='o', label='Empirical', s=50, alpha=0.8)
    plt.scatter(df['Age'], df['LI_sim'], color='mediumaquamarine', marker='o', label='Simulated', s=50, alpha=0.8)

    # Linear regression function
    def plot_regression(x, y, label, color):
        slope, intercept, r_value, p_value, _ = linregress(x, y)
        plt.plot(x, slope * x + intercept, color=color, linestyle='-', label=f'{label}: r={r_value:.3f}, p={p_value:.3f}', linewidth=3)

    # Regression lines
    plot_regression(df['Age'], df['LI_emp'], 'Empirical', 'black')
    plot_regression(df['Age'], df['LI_sim'], 'Simulated', 'mediumaquamarine')

    # Plot 
    plt.xlabel('Age', fontsize=12)
    plt.ylabel('Frontal Beta ERD/S Laterality Index', fontsize=12)
    plt.axhline(0, color='gray', linewidth=1.5, linestyle='--')
    plt.ylim(-1.1, 1.1)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(fontsize=10)
    sns.despine()

    # Show & save plot
    plt.tight_layout()
    plt.savefig("LI_vs_Age.png", dpi=300, bbox_inches='tight')
    plt.show()

# Execute the plotting function
plot_LI_vs_age(all_data)
