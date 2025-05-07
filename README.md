# 🧠 Traffy Fondue DSDE Final Project

## Overview

This project visualizes and analyzes urban problems reported in **Bangkok Metropolitan Area** using the **Traffy Fondue** dataset. The dashboard displays issues through **maps, graphs, tables**, and **detailed problem comments**.

### 🔍 Analysis Concept

Our core idea is to **cluster problems** based on their **location** and **type**, enabling better tracking and evaluation of recurring issues.

### 📌 Problem Definition

A "new problem occurrence" is defined as:

- A **new report** of the same **problem type** at the same **location**,  
- **After** the original problem has been marked as **resolved**.

> 🔁 Multiple reports **before** the issue is resolved are counted as **one** problem, to prevent duplication from citizen follow-ups.


### 🚀 How to Run

1. **Clone the repository:**

   ```bash
   git clone https://github.com/subhakritsc/Traffy-Fondue-DSDE-Final-Project.git
   cd Traffy-Fondue-DSDE-Final-Project/streamlit_app

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt

3. **Set up data files:**

   Run the following commands to download the necessary CSV files:
   ```bash
   gdown "https://drive.google.com/uc?id=1YQKG7PWSw9H8ONYXjORrya5SGreIeHme" #changed later
   gdown "https://drive.google.com/uc?id=1GJVlJnb6duoBW7lwe5vRtmipUQLnpDwb"

4. **Run the app:**

   ```bash
   streamlit run app.py
   ```

   Visit `http://localhost:8501` to view the app.
