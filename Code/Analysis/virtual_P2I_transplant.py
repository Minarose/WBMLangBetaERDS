import numpy as np
import torch
import pickle
import sys
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

# -----------------------------
#  Load Input Parameters
# -----------------------------
sub = sys.argv[1]  # Subject ID
run = sys.argv[2]  # Trial name

# Define paths
data_path = "/path/to/data/"
output_path = data_path + "Transplant_Results/"
fitting_results_path = data_path + "Fitting_Results/"

# -----------------------------
#  Load M/EEG, SC, and Distance Data
# -----------------------------
meg_file = f"{data_path}{sub}/{run}.npy"
meg_data = np.load(meg_file)

sc_file = f"{data_path}{sub}/weights.csv"
dist_file = f"{data_path}{sub}/distance.txt"

sc_df = pd.read_csv(sc_file, header=None)
sc = sc_df.values
dist = np.loadtxt(dist_file)

# Normalize Structural Connectivity
sc = np.log1p(sc) / np.linalg.norm(np.log1p(sc))

# -----------------------------
#  Load Model Fitting Results
# -----------------------------
fitting_file = f"{fitting_results_path}{sub}_{run}_fittingresults_stim_exp.pkl"
with open(fitting_file, 'rb') as f:
    F = pickle.load(f)

# -----------------------------
#  Load Source Group P2I Data
# -----------------------------
source_group = "YC"  # Modify as needed (e.g., 'Adol', 'Young Children')
source_p2i_file = f"{data_path}avg_{source_group}_sc_p2i.npy"
avg_source_p2i = np.load(source_p2i_file)

# -----------------------------
# Define Frontal ROIs and Split Left/Right Hemisphere nodes
# -----------------------------
NEW_Frontal_roi = np.array([2, 7, 10, 17, 18, 24, 25, 26, 28, 30, 31, 33,
                             37, 38, 42, 50, 56, 59, 61, 62, 65, 66, 68, 71,
                             77, 78, 83, 91, 92, 94, 96, 98, 99, 100, 101, 102, 103,
                             108, 110, 113, 117, 125, 126, 129, 132, 133, 135, 137,
                             140, 142, 150, 158, 161, 172, 178, 180, 182, 183])

R_Frontal_idx = NEW_Frontal_roi[NEW_Frontal_roi < 94] - 1  # Right Hemisphere Indices
L_Frontal_idx = NEW_Frontal_roi[NEW_Frontal_roi > 93] - 1  # Left Hemisphere Indices

# -----------------------------
# Apply P2I Transplantation from Source to Target Group only between frontal hemispheres
# -----------------------------
new_sc_m_b = F.model.sc_m_b.detach().clone()

tensor_to_assign1 = torch.from_numpy(avg_source_p2i[np.ix_(L_Frontal_idx, R_Frontal_idx)]).to(
    dtype=new_sc_m_b.dtype, device=new_sc_m_b.device)
tensor_to_assign2 = torch.from_numpy(avg_source_p2i[np.ix_(R_Frontal_idx, L_Frontal_idx)]).to(
    dtype=new_sc_m_b.dtype, device=new_sc_m_b.device)

new_sc_m_b[np.ix_(L_Frontal_idx, R_Frontal_idx)] = tensor_to_assign1
new_sc_m_b[np.ix_(R_Frontal_idx, L_Frontal_idx)] = tensor_to_assign2

F.model.sc_m_b = new_sc_m_b  # Update the model with the transplanted P2I

# -----------------------------
#  Set Up Model Simulation Parameters
# -----------------------------
meg_sub = np.zeros((meg_data.shape[0], 1500))
meg_sub[:, :meg_data.shape[1]] = meg_data * 1.0e13  # Scale M/EEG data

node_size = sc.shape[0]
output_size = meg_sub.shape[0]
batch_size = 250
step_size = 0.0001
num_epoches = 250
tr = 0.001
state_size = 6
base_batch_num = 250
time_dim = meg_sub.shape[1]
hidden_size = int(tr / step_size)

# -----------------------------
#  Run Model Simulation
# -----------------------------
#dataloader defined in JR script
data_mean = dataloader((meg_sub - meg_sub.mean(0)).T, num_epoches, batch_size)
F.ts = data_mean

# Define external stimulation input
u = np.zeros((node_size, hidden_size, time_dim))
u[:, :, 100:140] = 5000  # Apply stimulus

output_test = F.test(base_batch_num, u=u)

# -----------------------------
#  Save the Simulated Results
# -----------------------------
transplant_label = f"{source_group}p2i"
source_file = f"{output_path}{sub}_{run}_{transplant_label}_pred1500_source_ts.npy"
sensor_file = f"{output_path}{sub}_{run}_{transplant_label}_pred1500_sensor_ts.npy"

np.save(source_file, F.output_sim.P_test)
np.save(sensor_file, F.output_sim.eeg_test)

print(f"Saved results to:\n  {source_file}\n  {sensor_file}")
