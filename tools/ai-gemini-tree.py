import json
import os
import time
from pathlib import Path
import pdfplumber
from google import genai

# --- Chargement .env ---
ENV = {}
if Path(".env").exists():
    with open(".env", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                ENV[k.strip()] = v.strip().strip('"').strip("'")

GEMINI_API_KEY = ENV.get("GEMINI_API_KEY") or ENV.get("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    print("❌ Ajoute GEMINI_API_KEY dans .env")
    raise SystemExit(1)

client = genai.Client(api_key=GEMINI_API_KEY)

PDF_PATH = "themes/T1.pdf"
OUTPUT = "data/ai-gemini-tree.json"

# 1. Extraction du texte du PDF
print(f"📄 Extraction du texte de {PDF_PATH}...")
texte_complet = ""
with pdfplumber.open(PDF_PATH) as pdf:
    for i, page in enumerate(pdf.pages):
        t = page.extract_text()
        if t:
            texte_complet += f"\n--- PAGE {i+1} ---\n{t}\n"

print(f"✅ {len(texte_complet)} caractères extraits.")
texte_complet = texte_complet[:30000]

# 2. Préparation du prompt
prompt = f"""
Tu es un concepteur pédagogique expert en DALF C1. 
Voici le texte brut extrait du Thème 1 (La Justice) d'un manuel de français :

{texte_complet}

Ta mission : Proposer un "Arbre de compétences" idéal pour une application type Duolingo.
Analyse TOUT le contenu (manuel + cahier) et propose une structure d'unités pédagogiques.
Pour chaque unité, indique :
- Un titre
- Un type (comprehension_orale, comprehension_ecrite, production_orale, production_ecrite, vocabulaire, grammaire)
- Une description courte
- Le nombre estimé de questions/éléments

Format de sortie attendu : Un objet JSON strict.
{{
  "titre_theme": "La Justice",
  "unites": [
    {{"titre": "...", "type": "...", "description": "...", "nb_elements_estime": 0}}
  ]
}}
"""

# 3. Appel avec retry automatique (3 essais) et modèles de secours
modeles = ["gemini-2.5-flash", "gemini-3.5-flash-lite"]
arbre = None

for modele in modeles:
    for essai in range(3):
        try:
            print(f"🧠 Essai avec {modele} (tentative {essai+1}/3)...")
            response = client.models.generate_content(
                model=modele,
                contents=prompt
            )
            result_text = response.text.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:-3].strip()
            elif result_text.startswith("```"):
                result_text = result_text[3:-3].strip()
            
            arbre = json.loads(result_text)
            print(f"✅ Succès avec {modele} !")
            break
        except Exception as e:
            print(f"⚠️  Échec avec {modele} : {str(e)[:100]}")
            if essai < 2:
                print("⏳ Attente de 5 secondes avant de réessayer...")
                time.sleep(5)
    if arbre:
        break

# 4. Sauvegarde
if arbre:
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(arbre, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Arbre sauvegardé dans {OUTPUT}")
    print("\n=== APERÇU DE L'ARBRE PROPOSÉ PAR GEMINI ===")
    print(f"Thème : {arbre.get('titre_theme')}")
    for u in arbre.get("unites", []):
        print(f"  - [{u.get('type')}] {u.get('titre')} ({u.get('nb_elements_estime')} éléments)")
else:
    print("❌ Tous les modèles ont échoué. Réessaie plus tard (les serveurs Google sont peut-être surchargés).")
