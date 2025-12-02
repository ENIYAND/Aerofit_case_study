# Aerofit Case Study

**Short summary:**  
This case study analyzes customer profiles and buying behavior for Aerofit treadmill models (KP281, KP481, KP781). The goal is to understand which customer characteristics influence product choice and to recommend targeted marketing strategies. Insights are derived from exploratory data analysis, probability calculations, customer segmentation, and outlier detection.

---

## 📁 Repository Structure

- `notebooks/01-aerofit-exploratory-analysis.ipynb` — complete analysis notebook with EDA, plots, segment insights, and probability calculations.
- `reports/AeroFit_Case_Study.pdf` — printable formatted report with visuals and conclusions.
- `src/` — optional scripts for data preprocessing and plotting.
- `data/` — placeholder for raw or processed datasets.
- `figures/` — exported charts used in the report and notebook.
- `.github/workflows/ci.yml` — optional CI workflow for notebook validation.
- `README.md` — project documentation (this file).
- `requirements.txt` — dependencies required to run the notebook.

---

## 🧩 TL;DR — Key Findings

### **1. Product Preference Insights**
- **KP281 (Entry Model)**  
  - Most purchased model (~44%).  
  - Customers have moderate income and medium usage.  
  - Balanced gender distribution.  
  - Ideal for beginners/general fitness users.

- **KP481 (Mid Model)**  
  - Purchased by ~33% of customers.  
  - Very consistent usage pattern (narrow IQR).  
  - Good choice for disciplined, routine-focused users.

- **KP781 (Premium Model)**  
  - Purchased by high-income customers (median ₹76k+).  
  - Highest usage and miles covered.  
  - Predominantly male demographic.  
  - Strong fit for serious runners and premium buyers.

---

### **2. Feature Relationships**
- **Miles vs Usage** → Strongest positive correlation (~0.7).  
- **Income** → Key factor differentiating product choice (especially KP781).  
- **Age & Education** → Not strong predictors of product preference.

---

### **3. Outlier Observations**
- KP481 shows low variance in usage → outliers here represent high consistency, not anomalies.  
- Some very high-mileage customers identified → potential brand ambassadors or premium upgrade targets.

---

## 🎯 Business Recommendations

### **KP781 (Premium Model)**
- Focus marketing on **high-income, fitness-focused** customers.
- Create **female-focused campaigns** to improve women engagement in premium category.
- Highlight performance, durability, and training value.

### **KP481 (Mid Model)**
- Market as **durable & routine-friendly**.
- Target users who work out consistently (3–5+ days/week).
- Good positioning for small gyms and fitness clubs.

### **KP281 (Entry Model)**
- Promote as **affordable & beginner-friendly**.
- Bundle with accessories or extended warranty for upsell.
- Target general population via broad marketing channels.

### **Cross-segment Strategy**
- Use **Miles** & **Usage** to drive personalized offers.  
- Promote accessories/maintenance packs to high-mileage users.


---

## Badges / Demos
- Report PDF: reports/Aerofit_case_study.pdf
---- 

## Binder Launch
[![Open In Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ENIYAND/aerofit-case-study/main?urlpath=lab)

---

## Contact
ENIYAN D — umayalini64@gmail.com
LinkedIn - www.linkedin.com/in/tamil-eniyan-

---

## 🚀 How to Run the Project Locally

```bash
# Clone the repo
git clone https://github.com/<your-username>/aerofit-case-study.git
cd aerofit-case-study

# Create virtual environment
python -m venv venv

# Activate environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Launch Jupyter Lab
jupyter lab
# Open notebooks/01-aerofit-exploratory-analysis.ipynb
