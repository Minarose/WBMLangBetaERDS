import os
import numpy as np
import pickle
import mne
import matplotlib.pyplot as plt

data_path = "/path/to/data"  # Change this to your data directory
empirical_path = os.path.join(data_path, "empirical/preprocessed")
sim_path = os.path.join(data_path, "simulated")  # Path to simulated predictions
subs = []
# Load simulated data from .pkl files
for subj in subs:
    print(f"Loading simulated data for: {subj}")

    n_file = os.path.join(sim_path, subj, f"{subj}_noise_fittingresults_stim_exp.pkl")
    v_file = os.path.join(sim_path, subj, f"{subj}_verb_fittingresults_stim_exp.pkl")

    # Load noise condition
    with open(n_file, 'rb') as n:
        noise = pickle.load(n)
    sim_ev_n_allsubs.append(noise.eeg_test)

    # Load verb condition
    with open(v_file, 'rb') as v:
        verb = pickle.load(v)
    sim_ev_v_allsubs.append(verb.eeg_test)

# Convert simulated data into MNE EvokedArray objects to plot wth MNE
# Load an empirical evoked file for reference
empirical_file = os.path.join(empirical_path, "sample_subject_verb_epo.fif")
ev_samp_file = mne.read_epochs(empirical_file, preload=True)
ev_samp_file = ev_samp_file.drop_channels('MLC12-3405').resample(1000).apply_baseline((-0.5, 0))

sim_verb = [mne.EvokedArray(v[:, 75:500], ev_samp_file.info, tmin=-0.025) for v in sim_ev_v_allsubs]
sim_noise = [mne.EvokedArray(n[:, 75:500], ev_samp_file.info, tmin=-0.025) for n in sim_ev_n_allsubs]

# Plot simulated data
for idx, sub in enumerate(subs):
    sim_verb[idx].plot_joint(title=f"Simulated Verb - {sub}")
    plt.show()

for idx, sub in enumerate(subs):
    sim_noise[idx].plot_joint(title=f"Simulated Noise - {sub}")
    plt.show()


