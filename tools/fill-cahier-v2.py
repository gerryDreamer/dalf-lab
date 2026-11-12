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

client = Groq(api_key=ENV.get("GROQ_API_KEY") or ENV.get("GROK_API_KEY"))

INPUT = "data/edito-c1.final-tree.json"
OUTPUT = "data/edito-c1.final-tree.json"

with open(INPUT, encoding="utf-8") as f:
    data = json.load(f)

theme1 = data["themes"][0]
cahier = theme1["parties"]["cahier"]["sections"]

# --- 1. On récupère les 10 QCM existants (depuis structured.json) ---
abr_questions = []
try:
    with open("data/edito-c1.structured.json", encoding="utf-8") as f:
        old_data = json.load(f)
    old_sections = old_data["themes"][0]["parties"]["cahier"]["sections"]
    for s in old_sections:
        if s.get("type") == "a_batons_rompus" and s.get("questions"):
            abr_questions = s["questions"]
            break
    print(f"📚 {len(abr_questions)} questions récupérées depuis structured.json.")
except Exception as e:
    print(f"⚠️ Impossible de charger structured.json : {e}")

# --- 2. On remplit chaque section vide ---
for section in cahier:
    type_s = section.get("type")
    
    if type_s == "a_batons_rompus":
        section["questions"] = abr_questions
        print(f"✅ À bâtons rompus : {len(abr_questions)} questions (récupérées).")
    
    elif type_s == "quiz_revision" and not section.get("questions"):
        print("🧠 Génération du Quiz de révision (avec prompt robuste)...")
        prompt = """
        Génère 10 questions à choix multiples (QCM) pour réviser le Thème 1 (La Justice).
        Réponds UNIQUEMENT avec un tableau JSON valide, sans aucun texte avant ou après.
        Format STRICT :
        [
          {"texte": "Question 1 ?", "choix": ["A", "B", "C", "D"], "bonne": 0},
          {"texte": "Question 2 ?", "choix": ["A", "B", "C", "D"], "bonne": 1}
        ]
        """
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="openai/gpt-oss-120b",
                temperature=0.1,
                max_completion_tokens=3000
            )
            txt = response.choices[0].message.content.strip()
            # Nettoyage agressif
            if "```json" in txt:
                txt = txt.split("```json")[1].split("```")[0].strip()
            elif "```" in txt:
                txt = txt.split("```")[1].split("```")[0].strip()
            
            # On essaie de parser
            try:
                section["questions"] = json.loads(txt)
                print(f"✅ Quiz de révision : {len(section['questions'])} QCM")
            except json.JSONDecodeError as e:
                print(f"❌ Erreur JSON : {e}")
                print(f"   Texte brut reçu : {txt[:200]}...")
                section["questions"] = []
        except Exception as e:
            print(f"❌ Erreur Quiz : {e}")

# --- 3. Sauvegarde ---
with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n✅ Fichier mis à jour : {OUTPUT}")
print("\n=== BILAN FINAL ===")
for s in cahier:
    t = s.get("type")
    nb = len(s.get("questions", s.get("flashcards", [])))
    print(f"  - [{t}] {nb} éléments")
