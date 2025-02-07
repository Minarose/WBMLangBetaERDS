import os
import numpy as np
import pickle
import mne
import matplotlib.pyplot as plt

data_path = "/path/to/data"  # Change this to your data directory
empirical_path = os.path.join(data_path, "empirical/preprocessed")
sim_path = os.path.join(data_path, "simulated")  # Path to simulated predictions
subs = ['Subject01','Subject02','Subject03']

emp_verb_allsubs = []
emp_noise_allsubs = []
sim_verb_allsubs = []
sim_noise_allsubs = []

for sub in subs:
    print(f"Loading empirical data for {sub}...")
    verb_file = os.path.join(empirical_data_path, sub, 'preprocessed', 'verb.npy')
    noise_file = os.path.join(empirical_data_path, sub, 'preprocessed', 'noise.npy')

    emp_verb_allsubs.append(np.load(verb_file))  # (channels x timepoints)
    emp_noise_allsubs.append(np.load(noise_file))

# Load simulated data from .pkl files
for sub in subs:
    print(f"Loading simulated data for: {subj}")

    n_file = os.path.join(sim_path, subj, f"{subj}_noise_fittingresults_stim_exp.pkl")
    v_file = os.path.join(sim_path, subj, f"{subj}_verb_fittingresults_stim_exp.pkl")

    # Load noise condition
    with open(n_file, 'rb') as n:
        noise = pickle.load(n)
    sim_noise_allsubs.append(noise.eeg_test)

    # Load verb condition
    with open(v_file, 'rb') as v:
        verb = pickle.load(v)
    sim_verb_allsubs.append(verb.eeg_test)

# Convert simulated data into MNE EvokedArray objects to plot wth MNE
# Load sample MEG info from an example file
sample_meg_file = "/path/to/sample_meg.fif"  # Provide a valid .fif file
ev_samp_file = mne.read_epochs(sample_meg_file, preload=True).resample(1000)
info = ev_samp_file.info  # Use existing MEG channel structure

# Convert empirical data to MNE format
emp_verb_evoked = [mne.EvokedArray(data[:, :500], info, tmin=0) for data in emp_verb_allsubs]
emp_noise_evoked = [mne.EvokedArray(data[:, :500], info, tmin=0) for data in emp_noise_allsubs]

# Convert simulated data to MNE format
sim_verb_evoked = [mne.EvokedArray(data[:, :500], info, tmin=0) for data in sim_verb_allsubs]
sim_noise_evoked = [mne.EvokedArray(data[:, :500], info, tmin=0) for data in sim_noise_allsubs]

# Plot empirical verb vs. simulated verb for each subject
for idx, sub in enumerate(subs):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Plot empirical verb
    emp_verb_evoked[idx].plot_joint(title=f"Empirical Verb: {sub}", show=False, axes=axes[0])
    
    # Plot simulated verb
    sim_verb_evoked[idx].plot_joint(title=f"Simulated Verb: {sub}", show=False, axes=axes[1])

    plt.show()

# Plot empirical noise vs. simulated noise for each subject
for idx, sub in enumerate(subs):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Plot empirical noise
    emp_noise_evoked[idx].plot_joint(title=f"Empirical Noise: {sub}", show=False, axes=axes[0])
    
    # Plot simulated noise
    sim_noise_evoked[idx].plot_joint(title=f"Simulated Noise: {sub}", show=False, axes=axes[1])

    plt.show()



