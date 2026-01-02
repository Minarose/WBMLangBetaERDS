# **Developmental Disinhibition Gates Language Lateralization in Childhood**  
**Minarose M Ismail**, Davide Momi, Zheng Wang, Sorenza P. Bastiaens, M. Parsa Oveisi, Hansel M. Greiner, Donald J. Mabbott, John D. Griffiths, Darren S. Kadis

**Affiliations**  
1. Department of Physiology, University of Toronto  
2. Neurosciences & Mental Health, The Hospital for Sick Children, Toronto  
3. Krembil Centre for Neuroinformatics, Centre for Addiction and Mental Health, Toronto  
4. Institute of Medical Sciences, University of Toronto
5. Department of Psychology, University of Toronto
6. Department of Psychiatry, University of Toronto  
7. Department of Pediatrics, College of Medicine, University of Cincinnati 
---

## **Overview**  
This repository contains the complete code for the study:  

> **"Developmental Disinhibition Gates Language Lateralization in Childhood"**  
> *Ismail et al., 2026*

![figure1_modified (1)](https://github.com/user-attachments/assets/c0a3da7c-89ad-4dee-8a9c-3988d4545b3b)

Hemispheric specialization is a hallmark of brain organization across species, yet the mechanisms that drive the formation of functionally specialized circuits remain poorly understood. In humans, the gradual emergence of left-hemisphere dominance for language over the first two decades offers a well-characterized model for probing these mechanisms. Here, we constructed personalized whole-brain neurophysiological models in children and adolescents, to simulate task-evoked dynamics from auditory perception to language production. These models were grounded in individual structural connectivity from diffusion MRI and fit to magnetoencephalography data using machine learning optimization.  We demonstrate that hemispheric specialization emerges through distinct inhibitory processes during development.   

Early in life, asymmetries in interhemispheric inhibition are present, with stronger projections from left pyramidal cells to right inhibitory interneurons. However, these asymmetries alone are insufficient to drive functional specialization. Using \textit{in silico} manipulations, including virtual circuit transplants, we show that progressive developmental reduction in local inhibition is necessary to unmask the functional influence of early asymmetries. Local disinhibition enables structural asymmetries to shape functional lateralization. Our findings reveal a mechanistic model in which functional specialization arises from the interaction between early structural asymmetries and developmental disinhibition, a process that can be generalized across species and cognitive domains using our computational framework.

---

## **Repository Structure**  
```
├── Code/ # Preprocessing, modelling, analysis & simulation scripts
├── Data/ # Extracted model parameters, laterality indices, and age
├── README.md # This file
```

---

## **Data Availability**  

### **Raw Data**
The raw MEG and MRI data used in this study are **not publicly available** due to institutional and ethical restrictions.

### **Preprocessed Model Inputs (Provided)**
We provide all **preprocessed model inputs** required to run the model fitting pipeline:
- **Location:** `Data/Model_Inputs/`
- **Contents:** 
  - Trial-averaged evoked MEG responses (`verb_evoked.npy`, `noise_evoked.npy`)
  - Structural connectivity matrices (`shen_indiv.csv` or `weights.csv`)
  - Distance matrices (`distance.txt`)
  - Leadfield matrices (`leadfield_3d.mat`)
- **See:** `Data/Model_Inputs/README.md` for detailed file descriptions

These preprocessed inputs allow you to:
- Run the model fitting pipeline (`Code/JR_Model_Fitting.py`)
- Generate your own model simulations
- Reproduce the model fitting process

### **Model Outputs (Provided)**
We also provide:
- **Extracted Model Parameters:** `Data/Model_Outputs/Parameters/subject_data.pkl` - Summary DataFrame with fitted model parameters, laterality indices, and subject age
- **Simulations:** `Data/Model_Outputs/Simulations/` - Simulated time series in source and sensor space

These outputs allow for full replication of the group-level analyses and figures in the manuscript.

---

## **Citation**  
Coming soon ... 

---

## **Contact**  
For inquiries, feel free to **open an issue** or contact:  
- 📧 Minarose Ismail: [minarose.ismail@mail.utoronto.ca](mailto:minarose.ismail@mail.utoronto.ca) 
