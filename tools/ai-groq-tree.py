import json
import os
from pathlib import Path
import pdfplumber
from groq import Groq

# --- Chargement .env ---
ENV = {}
if Path(".env").exists():
    with open(".env", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                ENV[k.strip()] = v.strip().strip('"').strip("'")

GROQ_API_KEY = ENV.get("GROQ_API_KEY") or ENV.get("GROK_API_KEY")
if not GROQ_API_KEY:
    print("❌ Ajoute GROQ_API_KEY ou GROK_API_KEY dans .env")
    raise SystemExit(1)

client = Groq(api_key=GROQ_API_KEY)

PDF_PATH = "themes/T1.pdf"
OUTPUT = "data/ai-groq-tree.json"

# 1. Extraction du texte du PDF
print(f"📄 Extraction du texte de {PDF_PATH}...")
texte_complet = ""
with pdfplumber.open(PDF_PATH) as pdf:
    for i, page in enumerate(pdf.pages):
        t = page.extract_text()
        if t:
            texte_complet += f"\n--- PAGE {i+1} ---\n{t}\n"

print(f"✅ {len(texte_complet)} caractères extraits.")
texte_complet = texte_complet[:20000]

# 2. Préparation du prompt (volontairement identique à Gemini pour comparer)
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

Format de sortie attendu : Un objet JSON strict, sans texte autour.
{{
  "titre_theme": "La Justice",
  "unites": [
    {{"titre": "...", "type": "...", "description": "...", "nb_elements_estime": 0}}
  ]
}}
"""

# 3. Appel à Groq
print("🧠 Groq analyse le texte et propose un arbre...")

try:
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="openai/gpt-oss-120b",
        temperature=0.2,
        max_completion_tokens=4000,
        top_p=1,
        reasoning_effort="medium"
    )
    
    result_text = response.choices[0].message.content.strip()
    if result_text.startswith("```json"): result_text = result_text[7:-3].strip()
    elif result_text.startswith("```"): result_text = result_text[3:-3].strip()
    
    arbre = json.loads(result_text)
    
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(arbre, f, ensure_ascii=False, indent=2)
        
    print(f"\n✅ Arbre proposé par Groq sauvegardé dans {OUTPUT}")
    print("\n=== APERÇU DE L'ARBRE PROPOSÉ PAR GROQ ===")
    print(f"Thème : {arbre.get('titre_theme')}")
    for u in arbre.get("unites", []):
        print(f"  - [{u.get('type')}] {u.get('titre')} ({u.get('nb_elements_estime')} éléments)")

except Exception as e:
    print(f"❌ Erreur Groq : {e}")
