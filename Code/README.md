# **Development of Inhibitory Circuits Drives Language Lateralization in Childhood**  
**Minarose M Ismail**, Davide Momi, Zheng Wang, Sorenza P. Bastiaens, M. Parsa Oveisi, Hansel M. Greiner, **John D. Griffiths***, **Darren S. Kadis***

**Affiliations**  
1. Department of Physiology, University of Toronto  
2. Neurosciences & Mental Health, The Hospital for Sick Children, Toronto  
3. Krembil Centre for Neuroinformatics, Centre for Addiction and Mental Health, Toronto  
4. Institute of Medical Sciences, University of Toronto  
5. Department of Psychiatry, University of Toronto  
6. Department of Pediatrics, College of Medicine, University of Cincinnati  

**Corresponding Authors**    
- Darren S. Kadis ([darren.kadis@sickkids.ca](mailto:darren.kadis@sickkids.ca))
- John D. Griffiths ([jdavidgriffiths@gmail.com](mailto:jdavidgriffiths@gmail.com))  

---

## **Overview**  
This repository contains the complete code for the study:  

> **"Development of Inhibitory Circuits Drives Language Lateralization in Childhood"**  
> *Ismail et al., 2025*

![figure1_modified (1)](https://github.com/user-attachments/assets/c0a3da7c-89ad-4dee-8a9c-3988d4545b3b)

In this study, we explore the **mechanisms underlying language lateralization** in childhood using **personalized whole-brain network models**. Our findings reveal that interhemispheric inhibitory circuits play a crucial role in shaping lateralized language function, with local inhibition decreasing over development while interhemispheric inhibition increases.  

Using **systematic model manipulations** and **virtual transplant experiments**, we show that the reduction in local inhibition allows pre-existing asymmetries in interhemispheric inhibition to drive laterality. This work provides a **developmental framework** for understanding how inhibitory circuits shape language networks.

---

## ** Repository Structure**  
```
├── data/               # Example datasets or links to data sources
├── scripts/            # Core analysis and simulation scripts
├── notebooks/          # Jupyter/Colab notebooks for step-by-step execution
├── results/            # Figures and output files
├── README.md           # This file
└── LICENSE             # Licensing information
```

---

## ** Installation & Requirements**  
To run the scripts, install the required dependencies using:  

```bash
pip install -r requirements.txt
```
Alternatively, manually install key dependencies:  

```bash
pip install numpy pandas matplotlib scipy mne
```

If using Jupyter notebooks, install Jupyter:  
```bash
pip install jupyter
```

---

## **📊 Usage**  

### **1️⃣ Data Preprocessing**  
Preprocess MEG and MRI data using the following script:  
```bash
python scripts/preprocess_data.py
```

### **2️⃣ Running the Computational Model**  
Execute the whole-brain network model simulations:  
```bash
python scripts/run_model.py
```

### **3️⃣ Analyzing and Visualizing Results**  
Generate plots and statistical analyses:  
```bash
python scripts/plot_results.py
```

Jupyter notebooks for exploratory analysis are provided in the `notebooks/` directory.

---

## ** Methods Summary**  
Our study employs **personalized whole-brain network models** based on individual structural connectivity and MEG-derived functional activity. The key computational model parameters include:  

- **Local Inhibition (I-P coupling):** Decreases with age but does not directly predict laterality.  
- **Interhemispheric Inhibition (P-I coupling):** Increases with age and correlates with laterality.  
- **Model Manipulations:** Virtual lesion and transplant experiments to assess causality in lateralization.  

For more details, see the **Methods** section of the paper.

---

## ** Data Availability**  
The dataset used in this study is **not publicly available** due to institutional and ethical restrictions.  

---

## ** Citation**  
If you use this code, please cite our work as follows:  

```
@article{Ismail2025,
  author = {Minarose Ismail, Davide Momi, Zheng Wang, Sorenza P. Bastiaens, 
            M. Parsa Oveisi, Hansel M. Greiner, John D. Griffiths, Darren S. Kadis},
  title = {Development of Inhibitory Circuits Drives Language Lateralization in Childhood},
  journal = {Journal Name},
  year = {2025},
  doi = {XXXX}
}
```

---

## ** Contact **  
For inquiries, feel free to **open an issue** or contact:  
- 📧 Minarose Ismail: [minaroseismail@gmail.com](mailto:minaroseismail@gmail.com)  
- 📧 John D. Griffiths: [jdavidgriffiths@gmail.com](mailto:jdavidgriffiths@gmail.com)  
- 📧 Darren S. Kadis: [darren.kadis@sickkids.ca](mailto:darren.kadis@sickkids.ca)  
