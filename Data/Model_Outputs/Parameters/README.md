# Extracted Model Parameters and Laterality Indices
This folder contains a summary DataFrame of subject-specific parameters and laterality indices extracted from personalized whole-brain neurophysiological models fit using the WBMLangBetaERDS pipeline.

Due to file size limitations, the full fitted models (2 conditions × 43 subjects) are not included in this repository. Instead, we provide the key parameters extracted from each subject’s fitted model, alongside empirical and simulated Laterality Indices (LI) and subject age. These features are sufficient to reproduce all group-level and subject-level analyses shown in the manuscript.

## What's Included?

The main file in this repository is:
- `subject_data.pkl`: a dataframe where each row corresponds to one subject. Including 39 subjects after exluding subjects with LI = 0

This dataframe contains:
- Fitted model parameters (local, long-range, etc.)
- Empirical and simulated laterality indices (`t_LI_emp`, `t_LI_sim`)
- Subject age

All scripts to reproduce the figures and statistical analyses in the manuscript can be found in the [`Analysis`](https://github.com/Minarose/WBMLangBetaERDS/tree/main/Analysis) directory of the main repository. This extracted data can be used as input to those scripts.

## Variable Glossary

| Column Name                   | Description |
|------------------------------|-------------|
| `a_verb`, `a_noise`          | Excitatory gain (α) during verb/noise trials |
| `b_verb`, `b_noise`          | Inhibitory gain (β) during verb/noise trials |
| `g_verb`, `g_noise`          | Global coupling strength during verb/noise trials |
| `g_f_verb`, `g_f_noise`      | Feedforward global coupling |
| `g_b_verb`, `g_b_noise`      | Feedback global coupling |
| `c1_verb`, `c1_noise`        | Local E→E coupling |
| `c2_verb`, `c2_noise`        | Local E→I coupling |
| `c3_verb`, `c3_noise`        | Local I→E coupling |
| `c4_verb`, `c4_noise`        | Local I→I coupling (inhibition of inhibitory neurons) |
| `fr_int_p2i_*`               | *Frontal interhemispheric* P→I coupling (e.g., `fr_int_p2i_verb_L2R` = left-to-right) |
| `fr_int_p2e_*`               | Frontal interhemispheric P→E coupling |
| `fr_int_p2p_*`               | Frontal interhemispheric P→P coupling |
| `wb_int_p2i_*`               | Whole-brain interhemispheric P→I coupling |
| `wb_int_p2e_*`               | Whole-brain interhemispheric P→E coupling |
| `wb_int_p2p_*`               | Whole-brain interhemispheric P→P coupling |
| `Age`                        | Subject age in years |
| `t_LI_emp`                   | Empirical laterality index (computed from MEG beta ERD/S) |
| `t_LI_sim`                   | Simulated laterality index (computed from model-generated beta ERD/S) |

**Note:**  
"P" = Pyramidal population, "I" = Inhibitory interneuron, "E" = Excitatory interneuron
