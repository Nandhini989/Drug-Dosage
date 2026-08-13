💊 Enhanced Prescription Analyzer

An AI-inspired Prescription Analysis Web Application built with Python, FastAPI, and Ngrok. The system analyzes prescription text, identifies known medicines using fuzzy matching, and provides educational information about dosage, indications, precautions, and alternatives based on the patient's age, weight, and medical condition.

«⚠️ Disclaimer: This project is for educational/demo purposes only. It is not a medical diagnosis or treatment system. Always consult a qualified healthcare professional before taking or changing medication.»

🚀 Features

- 📝 Prescription Text Analysis – Accepts prescription information as text.
- 💊 Drug Identification – Detects medicines from the entered prescription.
- 🔍 Fuzzy Drug Matching – Handles minor spelling variations and drug aliases.
- 👨‍⚕️ Age-Based Analysis – Provides different information for adults and children.
- ⚖️ Weight-Based Calculation – Calculates example pediatric dosage ranges for supported medicines.
- 🩺 Disease Relevance Analysis – Compares the entered condition with stored drug indications.
- 💡 Drug Alternatives – Displays alternative medicines stored in the database.
- ⚠️ Safety Notes – Shows precautions and important notes associated with medicines.
- 🌐 Web Interface – Provides a simple responsive HTML interface.
- 🔗 Public Access with Ngrok – Allows the FastAPI application to be accessed through a temporary public URL.

🛠️ Technologies Used

Backend

- Python
- FastAPI
- Uvicorn

Libraries

- "rapidfuzz" – Fuzzy medicine-name matching
- "pyngrok" – Ngrok tunneling
- "nest_asyncio" – Asyncio compatibility in Colab/Jupyter
- "requests" – HTTP requests

Frontend

- HTML5
- CSS3
- Google Fonts

Deployment / Development

- Google Colab / Jupyter Notebook
- Ngrok
- Git & GitHub

🏗️ System Workflow

User
  │
  ▼
Prescription Text + Patient Details
  │
  ▼
FastAPI Web Application
  │
  ▼
Drug Entity Extraction
  │
  ▼
Fuzzy Drug Name Matching
  │
  ▼
Drug Database
  │
  ├── Dosage Information
  ├── Indications
  ├── Precautions
  └── Alternatives
  │
  ▼
Age & Weight Based Analysis
  │
  ▼
Disease Relevance Analysis
  │
  ▼
Prescription Analysis Results
  │
  ▼
Web Browser

📋 Input Parameters

The application accepts:

Input| Description
Prescription Text| Medicine names and prescription information
Age| Patient age in years
Weight| Patient weight in kilograms
Disease/Condition| Primary disease or condition

Example Input

Prescription:
Amoxicillin 500mg
Paracetamol if fever

Age:
30

Weight:
65 kg

Condition:
Fever and bacterial infection

💊 Supported Medicines

The current demonstration database contains:

- Paracetamol
- Ibuprofen
- Amoxicillin
- Azithromycin
- Loratadine
- Metoprolol

Each medicine contains information such as:

Medicine Name
├── Aliases
├── Adult Dosage
├── Pediatric Dosage
├── Weight-Based Dosage
├── Indications
├── Safety Notes
└── Alternatives

🔍 Fuzzy Matching

The application uses RapidFuzz to identify medicine names even when the user enters minor spelling variations.

For example:

Input:
Paracetmol

Matched:
Paracetamol

A matching threshold is used to avoid accepting unrelated medicine names.

⚙️ Installation

Install the required Python libraries:

pip install fastapi "uvicorn[standard]" pyngrok requests rapidfuzz nest_asyncio

▶️ Running the Application

Run the Python/Colab code.

The application starts a FastAPI server on:

http://0.0.0.0:8000

Ngrok creates a temporary public URL such as:

https://xxxx-xxxx.ngrok-free.app

Open the generated URL in a browser to access the application.

📁 Project Structure

Prescription-Analyzer/
│
├── prescription_analyzer.py
├── README.md
└── requirements.txt

If using Google Colab:

Prescription Analyzer Notebook
│
├── Configuration
├── Dependency Installation
├── Drug Database
├── Drug Matching Functions
├── Prescription Analysis
├── FastAPI Application
├── HTML/CSS Interface
└── Ngrok Deployment

🔐 Security Note

Do not upload or commit your Ngrok authentication token to GitHub.

Instead of hardcoding:

NGROK_AUTH_TOKEN = "YOUR_TOKEN"

use an environment variable:

import os

NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN")

Then configure the token securely in your local/Colab environment.

If the token you pasted in the code is a real active token, revoke/rotate it in your Ngrok account before publishing this project publicly.

📊 Example Output

The application displays a results table containing:

Matched Drug| Recommended Dose| Analysis Notes| Alternatives
Paracetamol| Adult dosage information| Disease relevance + precautions| Ibuprofen
Amoxicillin| Adult dosage information| Disease relevance + precautions| Azithromycin, Cefuroxime

⚠️ Limitations

- The medicine database is limited and manually defined.
- It does not perform real OCR on prescription images.
- It does not verify prescriptions against a medical authority or pharmacy database.
- Dosage information is simplified for demonstration.
- Drug interactions are not comprehensively evaluated.
- Medical history, allergies, pregnancy status, renal function, liver function, and other clinical factors are not considered.
- The system should not be used to make real-world medication decisions.

🔮 Future Enhancements

- 📷 Prescription image upload and OCR.
- 🤖 LLM-based prescription understanding.
- 🧠 Advanced drug interaction detection.
- 🗃️ Integration with a verified medical/drug database.
- 👨‍⚕️ Doctor/pharmacist verification workflow.
- 🔐 User authentication and secure patient records.
- 📄 PDF prescription report generation.
- 🌍 Multilingual prescription analysis.
- 📱 Mobile-friendly interface.
- 🧪 Comprehensive validation and clinical safety rules.

🎯 Project Objective

The primary objective of this project is to demonstrate how FastAPI, fuzzy matching, structured medicine data, and patient information can be combined to build a web-based prescription analysis prototype.

It demonstrates practical concepts including:

- REST API development
- Backend development with FastAPI
- Form handling
- Data processing
- Fuzzy string matching
- Rule-based analysis
- HTML/CSS UI development
- Temporary cloud tunneling using Ngrok

📌 Important

This project is a software prototype for educational purposes and must not be considered a substitute for professional medical advice, diagnosis, or treatment.
