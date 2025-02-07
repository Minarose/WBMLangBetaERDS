import numpy as np
import torch
import pickle
import sys
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

# -----------------------------
# Load Input Parameters
# -----------------------------
sub = sys.argv[1]  # Subject ID
run = sys.argv[2]  # Task/Run name
manipulation_type = sys.argv[3]  # 'increase' or 'decrease'

# Define paths
data_path = "/path/to/data/"
output_path = data_path + "Transplant_Results/"
fitting_results_path = data_path + "Fitting_Results/"


# -----------------------------
#  Load Model Fitting Results
# -----------------------------
fitting_file = f"{fitting_results_path}{sub}_{run}_fittingresults_stim_exp.pkl"
with open(fitting_file, 'rb') as f:
    F = pickle.load(f)

# -----------------------------
# Define Local Inhibition (c4) Manipulation
# -----------------------------
mean_diff_c4 = 0.6442991186  # Mean difference between groups (Modify if needed)

# Convert tensor param to float for manipulation
if manipulation_type == 'increase':
    new_c4 = F.model.c4.detach() + mean_diff_c4
    manipulation_label = "c4inc"
elif manipulation_type == 'decrease':
    new_c4 = F.model.c4.detach() - mean_diff_c4
    manipulation_label = "c4dec"
else:
    raise ValueError("Invalid manipulation_type. Choose 'increase' or 'decrease'.")

# Assign the new c4 value as a model parameter
F.model.c4 = torch.nn.Parameter(new_c4)


meg_file = f"{data_path}{sub}/{run}.npy"
meg_data = np.load(meg_file)

sc_file = f"{data_path}{sub}/shen_indiv.csv"
dist_file = f"{data_path}{sub}/distance.txt"

sc_df = pd.read_csv(sc_file, header=None)
sc = sc_df.values
dist = np.loadtxt(dist_file)

# Normalize Structural Connectivity
sc = np.log1p(sc) / np.linalg.norm(np.log1p(sc))
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
# Define external stimulation input
u = np.zeros((node_size, hidden_size, time_dim))
u[:, :, 100:140] = 5000  # Apply stimulus

output_test = F.test(base_batch_num, u=u)

# -----------------------------
# Save the Simulated Results
# -----------------------------
source_file = f"{output_path}{sub}_{run}_{manipulation_label}_pred1500_source_ts.npy"
sensor_file = f"{output_path}{sub}_{run}_{manipulation_label}_pred1500_sensor_ts.npy"

np.save(source_file, F.output_sim.P_test)
np.save(sensor_file, F.output_sim.meg_test)

print(f"Saved results to:\n  {source_file}\n  {sensor_file}")
