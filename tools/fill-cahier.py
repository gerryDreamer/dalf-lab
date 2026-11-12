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

# --- 1. Récupérer les 10 QCM existants pour "À bâtons rompus" ---
with open("data/edito-c1.structured.json", encoding="utf-8") as f:
    old_data = json.load(f)

old_sections = old_data["themes"][0]["parties"]["cahier"]["sections"]
abr_questions = []
for s in old_sections:
    if s.get("type") == "a_batons_rompus" and s.get("questions"):
        abr_questions = s["questions"]
        break

print(f"📚 {len(abr_questions)} questions récupérées pour 'À bâtons rompus'.")

# --- 2. On remplit chaque section vide ---
for section in cahier:
    type_s = section.get("type")
    
    if type_s == "a_batons_rompus":
        section["questions"] = abr_questions
        print(f"✅ À bâtons rompus : {len(abr_questions)} questions")
    
    elif type_s == "grammaire" and not section.get("questions"):
        print("🧠 Génération des QCM de Grammaire...")
        prompt = """
        Tu es un professeur de français expert en DALF C1. Génère 5 questions à choix multiples (QCM) sur la règle de grammaire : "La voix active et la voix passive".
        Format attendu : un tableau JSON strict.
        [{"texte": "Question ?", "choix": ["A", "B", "C", "D"], "bonne": 0}]
        """
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="openai/gpt-oss-120b",
                temperature=0.3,
                max_completion_tokens=2000
            )
            txt = response.choices[0].message.content.strip()
            if txt.startswith("```json"): txt = txt[7:-3].strip()
            elif txt.startswith("```"): txt = txt[3:-3].strip()
            section["questions"] = json.loads(txt)
            print(f"✅ Grammaire : {len(section['questions'])} QCM")
        except Exception as e:
            print(f"❌ Erreur Grammaire : {e}")
    
    elif type_s == "comprehension_orale" and not section.get("questions"):
        print("🧠 Génération des QCM de Compréhension orale...")
        prompt = """
        Tu es un professeur de français expert en DALF C1. Génère 5 questions à choix multiples (QCM) sur la compréhension orale du film "Je verrai toujours vos visages" (justice restaurative) et sur l'équithérapie en prison.
        Format attendu : un tableau JSON strict.
        [{"texte": "Question ?", "choix": ["A", "B", "C", "D"], "bonne": 0}]
        """
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="openai/gpt-oss-120b",
                temperature=0.3,
                max_completion_tokens=2000
            )
            txt = response.choices[0].message.content.strip()
            if txt.startswith("```json"): txt = txt[7:-3].strip()
            elif txt.startswith("```"): txt = txt[3:-3].strip()
            section["questions"] = json.loads(txt)
            print(f"✅ Compréhension orale : {len(section['questions'])} QCM")
        except Exception as e:
            print(f"❌ Erreur Compréhension orale : {e}")
    
    elif type_s == "comprehension_ecrite" and not section.get("questions"):
        print("🧠 Génération des QCM de Compréhension écrite...")
        prompt = """
        Tu es un professeur de français expert en DALF C1. Génère 5 questions à choix multiples (QCM) sur la compréhension écrite de la tribune sur la justice restaurative.
        Format attendu : un tableau JSON strict.
        [{"texte": "Question ?", "choix": ["A", "B", "C", "D"], "bonne": 0}]
        """
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="openai/gpt-oss-120b",
                temperature=0.3,
                max_completion_tokens=2000
            )
            txt = response.choices[0].message.content.strip()
            if txt.startswith("```json"): txt = txt[7:-3].strip()
            elif txt.startswith("```"): txt = txt[3:-3].strip()
            section["questions"] = json.loads(txt)
            print(f"✅ Compréhension écrite : {len(section['questions'])} QCM")
        except Exception as e:
            print(f"❌ Erreur Compréhension écrite : {e}")
    
    elif type_s == "quiz_revision" and not section.get("questions"):
        print("🧠 Génération du Quiz de révision...")
        prompt = """
        Tu es un professeur de français expert en DALF C1. Génère 10 questions à choix multiples (QCM) pour réviser tout le Thème 1 (La Justice) : vocabulaire, grammaire, compréhension.
        Format attendu : un tableau JSON strict.
        [{"texte": "Question ?", "choix": ["A", "B", "C", "D"], "bonne": 0}]
        """
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="openai/gpt-oss-120b",
                temperature=0.3,
                max_completion_tokens=3000
            )
            txt = response.choices[0].message.content.strip()
            if txt.startswith("```json"): txt = txt[7:-3].strip()
            elif txt.startswith("```"): txt = txt[3:-3].strip()
            section["questions"] = json.loads(txt)
            print(f"✅ Quiz de révision : {len(section['questions'])} QCM")
        except Exception as e:
            print(f"❌ Erreur Quiz de révision : {e}")

# --- 3. Sauvegarde ---
with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n✅ Fichier mis à jour : {OUTPUT}")
print("\n=== BILAN DU REMPLISSAGE ===")
for s in cahier:
    t = s.get("type")
    nb = len(s.get("questions", s.get("flashcards", [])))
    print(f"  - [{t}] {nb} éléments")
