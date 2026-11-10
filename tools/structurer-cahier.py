import json
import os
from pathlib import Path
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
client = Groq(api_key=GROQ_API_KEY)

INPUT = "data/edito-c1.final-images.json"
OUTPUT = "data/edito-c1.structured.json"

with open(INPUT, encoding="utf-8") as f:
    data = json.load(f)

theme1 = next(t for t in data["themes"] if t["theme"] == 1)
cahier_actuel = theme1["parties"]["cahier"]["sections"]
texte_brut = json.dumps(cahier_actuel, ensure_ascii=False, indent=2)

print("🧠 L'IA analyse le contenu et crée son propre parcours...")

prompt = f"""
Tu es un ingénieur pédagogique expert en DALF C1. 
Voici les données brutes du Cahier du Thème 1 (La Justice) extraites d'un manuel.
{texte_brut}

Ta mission : Analyser ces données et les transformer en un parcours d'apprentissage clair (style Duolingo).
1. Détecte les grands thèmes abordés (vocabulaire, grammaire, compréhension, production).
2. Crée une liste de sections pertinentes basées UNIQUEMENT sur ce qui est présent.
3. Si tu vois des questions sans choix multiples, génère 4 options pertinentes (QCM) et indique la bonne réponse (index 0-3).
4. Si c'est une section de production (écrite ou orale), garde la consigne et laisse "questions" vide.

Format de sortie attendu : Un tableau JSON strict (sans texte autour, sans balises markdown).
[
  {{
    "type": "comprehension_ecrite",
    "titre": "La justice restaurative",
    "questions": [
      {{
        "texte": "Quel est le but de la justice restaurative ?",
        "choix": ["Punir", "Réparer", "Ignorer", "Venger"],
        "bonne": 1
      }}
    ]
  }}
]
"""

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
        
    nouvelle_structure = json.loads(result_text)
    
    theme1["parties"]["cahier"]["sections"] = nouvelle_structure
    
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"✅ Succès ! L'IA a créé {len(nouvelle_structure)} sections sur mesure :")
    for s in nouvelle_structure:
        print(f"   - [{s.get('type')}] {s.get('titre')} ({len(s.get('questions', []))} questions)")

except Exception as e:
    print(f"❌ Erreur : {e}")
