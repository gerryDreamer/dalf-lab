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

client = Groq(api_key=ENV.get("GROQ_API_KEY"))

INPUT = "data/edito-c1.final-images.json"
OUTPUT = "data/edito-c1.final-images.json" # On écrase le fichier pour corriger

with open(INPUT, encoding="utf-8") as f:
    data = json.load(f)

theme1 = next(t for t in data["themes"] if t["theme"] == 1)

# On demande à l'IA de reconstruire la structure du Cahier du Thème 1
# D'après tes captures, voici les sections qu'elle doit trouver :
prompt = """
Tu es un expert en ingénierie pédagogique pour le DALF C1.
Voici les sections qui DEVRAIENT se trouver dans le Cahier du Thème 1 (La justice) :
1. Vocabulaire (Les acteurs, Les infractions, La procédure)
2. Grammaire (La voix active et passive)
3. Compréhension orale (L'équithérapie)
4. Production orale (Débat sur la justice)
5. Compréhension écrite (La justice restaurative)
6. Production écrite (Compte rendu)

Génère un tableau JSON strict avec ces sections, en leur donnant un type, un titre et un contenu factice (on remplira plus tard).
Format attendu :
[
  {"type": "vocabulaire", "titre": "Le lexique de la justice"},
  {"type": "grammaire", "titre": "Voix active et passive"},
  {"type": "comprehension_orale", "titre": "L'équithérapie"},
  {"type": "production_orale", "titre": "Débat"},
  {"type": "comprehension_ecrite", "titre": "Justice restaurative"},
  {"type": "production_ecrite", "titre": "Compte rendu"}
]
"""

response = client.chat.completions.create(
    messages=[{"role": "user", "content": prompt}],
    model="llama3-70b-8192",
    temperature=0.1,
)

result_text = response.choices[0].message.content.strip()
if result_text.startswith("```json"):
    result_text = result_text[7:-3].strip()
elif result_text.startswith("```"):
    result_text = result_text[3:-3].strip()

nouvelle_structure = json.loads(result_text)

# On injecte cette nouvelle structure dans le Thème 1
theme1["parties"]["cahier"]["sections"] = nouvelle_structure

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ Le Cahier du Thème 1 a été restructuré avec toutes ses sections !")
