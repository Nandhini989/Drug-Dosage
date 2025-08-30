# -----------------------
# 0) Tokens & Configuration
# -----------------------
# Your Ngrok token has been added below.
NGROK_AUTH_TOKEN = "31yGV6EkRtgEp9pQJlV5npsM646_4sEuMcZamK1jjSFWcMsMd" 

# -----------------------
# 1) Install dependencies
# -----------------------
print("⏳ Installing required libraries (this may take a moment)...")
import os
import sys
# Redirect output to null to keep the installation process clean
with open(os.devnull, 'w') as f:
    old_stdout = sys.stdout
    sys.stdout = f
    os.system("pip install -q fastapi 'uvicorn[standard]' pyngrok requests rapidfuzz nest_asyncio")
    sys.stdout = old_stdout
print("✅ Installation complete.")


# -----------------------
# 2) Imports
# -----------------------
import nest_asyncio
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from rapidfuzz import fuzz, process
from pyngrok import ngrok
from typing import Optional
import uvicorn
import threading
import time

# -----------------------
# 3) Fix asyncio in Colab/Jupyter environments
# -----------------------
nest_asyncio.apply()

# -----------------------
# 4) Expanded Drug DB with Dosing Formulas & Indications
# -----------------------
DRUG_DB = {
    "paracetamol": {
        "aliases": ["paracetamol", "acetaminophen", "calpol", "tylenol"],
        "adult_dose": "500-1000 mg every 4-6 hours. Max 4g/day.",
        "child_dose_text": "10-15 mg/kg per dose.",
        "child_dose_kg_mg": (10, 15), # Min/Max mg per kg
        "indications": ["fever", "pain", "headache", "migraine"],
        "notes": "Caution in patients with liver issues.",
        "alternatives": ["ibuprofen"]
    },
    "ibuprofen": {
        "aliases": ["ibuprofen", "motrin", "advil", "nurofen"],
        "adult_dose": "200-400 mg every 4-6 hours. Max 1.2g/day.",
        "child_dose_text": "5-10 mg/kg every 6-8 hours.",
        "child_dose_kg_mg": (5, 10),
        "indications": ["fever", "pain", "inflammation", "arthritis"],
        "notes": "Take with food to avoid stomach upset. Avoid in patients with kidney problems or stomach ulcers.",
        "alternatives": ["paracetamol"]
    },
    "amoxicillin": {
        "aliases": ["amoxicillin", "amoxil"],
        "adult_dose": "500 mg three times daily for 7-10 days.",
        "child_dose_text": "40-90 mg/kg/day in 2-3 divided doses.",
        "child_dose_kg_mg": (40, 90), # This is per DAY, so needs to be divided
        "indications": ["bacterial infection", "ear infection", "pneumonia", "bronchitis"],
        "notes": "Complete the full course even if you feel better.",
        "alternatives": ["azithromycin", "cefuroxime"]
    },
    "azithromycin": {
        "aliases": ["azithromycin", "zithromax", "z-pak"],
        "adult_dose": "500 mg on day 1, then 250 mg daily for 4 days.",
        "child_dose_text": "10 mg/kg on day 1, then 5 mg/kg for 4 days.",
        "child_dose_kg_mg": (10, 5), # Special dosing: (Day 1 dose, Subsequent days dose)
        "indications": ["bacterial infection", "pneumonia", "strep throat"],
        "notes": "Commonly known as a 'Z-Pak'.",
        "alternatives": ["amoxicillin"]
    },
    "loratadine": {
        "aliases": ["loratadine", "claritin"],
        "adult_dose": "10 mg once daily.",
        "child_dose_text": "5 mg (for age 2-5) or 10 mg (for age 6+) once daily.",
        "child_dose_kg_mg": None, # Dosing is age-based, not weight-based
        "indications": ["allergies", "hay fever", "hives", "allergic rhinitis"],
        "notes": "A non-drowsy antihistamine.",
        "alternatives": ["cetirizine", "fexofenadine"]
    },
    "metoprolol": {
        "aliases": ["metoprolol", "betaloc", "lopressor"],
        "adult_dose": "50-100 mg once or twice daily.",
        "child_dose_text": "N/A",
        "child_dose_kg_mg": None,
        "indications": ["high blood pressure", "hypertension", "angina", "heart failure"],
        "notes": "Beta-blocker. Do not stop taking suddenly.",
        "alternatives": ["atenolol", "carvedilol"]
    }
}

# Flatten all names and aliases for matching
ALL_DRUG_NAMES = []
for k, v in DRUG_DB.items():
    ALL_DRUG_NAMES.append(k)
    for a in v.get("aliases", []):
        if a.lower() not in ALL_DRUG_NAMES:
            ALL_DRUG_NAMES.append(a.lower())

# -----------------------
# 5) Enhanced Helper Functions
# -----------------------
def fuzzy_match_drug(name: str, limit=1):
    """Finds the best match for a drug name in the database."""
    name_low = name.lower()
    res = process.extract(name_low, ALL_DRUG_NAMES, scorer=fuzz.WRatio, limit=limit)
    if res and res[0][1] >= 70:
        match_name = res[0][0]
        for k, v in DRUG_DB.items():
            if match_name == k or match_name in [a.lower() for a in v.get("aliases", [])]:
                return k, res[0][1]
    return None, None

def extract_drug_entities(text: str):
    """Extracts unique drug names from a block of text."""
    words = [w.strip(".,():;") for w in text.lower().replace("\n", " ").split()]
    found = []
    for w in words:
        drug, score = fuzzy_match_drug(w)
        if drug and drug not in found:
            found.append(drug)
    return found

def analyze_drugs(drug_entities, age_years, weight_kg, disease):
    """Analyzes a list of drugs based on patient's age, weight, and condition."""
    results = []
    for ent in drug_entities:
        info = DRUG_DB.get(ent)
        if not info:
            continue

        dose_recommendation = "N/A"
        analysis_notes = ""

        # --- Dosing Logic ---
        is_child = age_years < 18
        if is_child and weight_kg and info.get("child_dose_kg_mg"):
            dose_range = info["child_dose_kg_mg"]
            min_dose = weight_kg * dose_range[0]
            max_dose = weight_kg * dose_range[1]
            dose_recommendation = f"{min_dose:.1f} - {max_dose:.1f} mg per dose. ({info['child_dose_text']})"
            # Special case for daily doses
            if "day" in info["child_dose_text"]:
                 dose_recommendation = f"{min_dose:.1f} - {max_dose:.1f} mg per DAY, to be given in divided doses."

        elif is_child:
            dose_recommendation = info.get("child_dose_text", "Not typically prescribed for this age group.")
        else: # Adult
            dose_recommendation = info.get("adult_dose", "N/A")

        # --- Disease Relevance Logic ---
        if disease and disease.strip():
            disease_lower = disease.lower().strip()
            indications = info.get("indications", [])
            is_indicated = any(indication in disease_lower for indication in indications)
            if is_indicated:
                analysis_notes += f"✅ Relevant for '{disease}'. "
            else:
                analysis_notes += f"⚠ May not be the primary treatment for '{disease}'. "

        # Add general notes from DB
        analysis_notes += info.get("notes", "")

        results.append({
            "matched_drug": ent.capitalize(),
            "recommended_dose": dose_recommendation,
            "alternatives": info.get("alternatives", []),
            "notes": analysis_notes.strip()
        })
    return results

# -----------------------
# 6) FastAPI App with Upgraded UI
# -----------------------
app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
      <head>
        <title>Enhanced Prescription Analyzer</title>
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
          body { font-family: 'Roboto', sans-serif; background-color: #f8f9fa; color: #343a40; line-height: 1.6; }
          .container { max-width: 700px; margin: 40px auto; padding: 30px; background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
          h2 { color: #0056b3; text-align: center; }
          textarea { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #ced4da; font-size: 16px; transition: border-color 0.2s; }
          textarea:focus { border-color: #0056b3; outline: none; }
          .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }
          .form-group label { font-weight: 500; display: block; margin-bottom: 5px; }
          input[type="number"], input[type="text"] { width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #ced4da; font-size: 16px; }
          input[type="submit"] { width: 100%; background-color: #0069d9; color: white; cursor: pointer; border: none; padding: 15px; font-size: 18px; font-weight: 500; border-radius: 8px; transition: background-color 0.2s; }
          input[type="submit"]:hover { background-color: #0056b3; }
          .disclaimer { color: #e63946; text-align: center; margin-top: 20px; font-weight: 500; }
        </style>
      </head>
      <body>
        <div class="container">
          <h2>Enhanced Prescription Analyzer</h2>
          <form action="/analyze" method="post">
            <div class="form-group">
                <label for="prescription_text">Prescription Text:</label>
                <textarea id="prescription_text" name="prescription_text" rows="8" placeholder="e.g., Rx: Amoxicillin 500mg, Paracetamol if fever..."></textarea>
            </div>
            <div class="form-grid">
                <div class="form-group">
                    <label for="age">Age (years):</label>
                    <input id="age" name="age" type="number" value="30" required/>
                </div>
                 <div class="form-group">
                    <label for="weight">Weight (kg):</label>
                    <input id="weight" name="weight" type="number" step="0.1" placeholder="Optional for child dose"/>
                </div>
            </div>
             <div class="form-group">
                <label for="disease">Primary Disease/Condition:</label>
                <input id="disease" name="disease" type="text" placeholder="e.g., Fever and headache"/>
            </div>
            <br/>
            <input type="submit" value="Analyze Prescription">
          </form>
          <p class="disclaimer">🚨 Demo only. This is not medical advice. Always consult a qualified healthcare professional.</p>
        </div>
      </body>
    </html>
    """

@app.post("/analyze", response_class=HTMLResponse)
async def analyze_prescription(
    prescription_text: str = Form(...),
    age: int = Form(...),
    weight: Optional[float] = Form(None),
    disease: Optional[str] = Form(None)
):
    drug_entities = extract_drug_entities(prescription_text)
    analysis = analyze_drugs(drug_entities, age, weight, disease)

    html_style = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
        body { font-family: 'Roboto', sans-serif; background-color: #f8f9fa; color: #343a40; padding: 20px; }
        .container { max-width: 1000px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
        h2 { color: #0056b3; }
        .patient-info { background-color: #e9ecef; padding: 15px; border-radius: 8px; margin-bottom: 20px; display: flex; justify-content: space-around; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 15px; border: 1px solid #dee2e6; text-align: left; }
        th { background-color: #0056b3; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .disclaimer { color: #e63946; margin-top: 20px; font-weight: bold; text-align: center; }
        .back-button { display: inline-block; margin-top: 20px; padding: 12px 20px; background-color: #28a745; color: white; text-decoration: none; border-radius: 8px; transition: background-color 0.2s; }
        .back-button:hover { background-color: #218838; }
    </style>
    """

    table_rows = ""
    if not analysis:
        table_rows = "<tr><td colspan='4'>No matching drugs found in the database from the provided text.</td></tr>"
    else:
        for drug in analysis:
            alternatives = ", ".join(drug['alternatives']) if drug['alternatives'] else "None"
            table_rows += f"""
            <tr>
                <td><b>{drug['matched_drug']}</b></td>
                <td>{drug['recommended_dose']}</td>
                <td>{drug['notes']}</td>
                <td>{alternatives}</td>
            </tr>
            """

    html_content = f"""
    <html>
        <head><title>Analysis Results</title>{html_style}</head>
        <body>
            <div class="container">
                <h2>Prescription Analysis Results</h2>
                <div class="patient-info">
                    <span><b>Age:</b> {age} years</span>
                    <span><b>Weight:</b> {weight or 'N/A'} kg</span>
                    <span><b>Condition:</b> {disease or 'N/A'}</span>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Matched Drug</th>
                            <th>Recommended Dose</th>
                            <th>Analysis Notes</th>
                            <th>Alternatives</th>
                        </tr>
                    </thead>
                    <tbody>{table_rows}</tbody>
                </table>
                <p class="disclaimer">🚨 Demo only. Information is for educational purposes and is not a substitute for professional medical advice.</p>
                <a href="/" class="back-button">Analyze Another</a>
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# -----------------------
# 7) Start Server (FINAL, CORRECTED VERSION)
# -----------------------

# Kill any existing ngrok tunnels to ensure a clean start
ngrok.kill()

# Set your Ngrok authentication token
if NGROK_AUTH_TOKEN:
    ngrok.set_auth_token(NGROK_AUTH_TOKEN)
    print("✅ Ngrok token set successfully.")
else:
    print("❌ ERROR: Your NGROK_AUTH_TOKEN is missing.")

# Create the Ngrok tunnel BEFORE starting the server
# This gets the public URL and prints it reliably in the main thread
try:
    public_url = ngrok.connect(8000, "http").public_url
    print(f"✅ Your app is live at: {public_url}")
    print(">> Open this URL in your browser to use the Prescription Analyzer.")
except Exception as e:
    print(f"❌ An error occurred with Ngrok: {e}")
    print("➡ This is likely due to an invalid NGROK_AUTH_TOKEN.")

# Define a function that only runs the Uvicorn server (this is a blocking call)
def run_server():
    # Add loop="asyncio" to force the standard loop that's compatible with nest_asyncio
    uvicorn.run(app, host="0.0.0.0", port=8000, loop="asyncio")

# Start the Uvicorn server in a separate thread
# The main Colab cell can now finish, but the server will keep running in the background.
thread = threading.Thread(target=run_server)
thread.start()

print("\n⏳ The server is starting up in the background...")
time.sleep(2) # A small delay to allow the server to initialize
print("✅ Server is running. You can now use the URL above.")