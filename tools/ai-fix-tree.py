import json
import os
from pathlib import Path
from groq import Groq

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

# --- On ne traite QUE les sections vides du Cahier (on ignore les 60 flashcards) ---
cahier = theme1["parties"]["cahier"]["sections"]

for section in cahier:
    type_s = section.get("type")
    
    # On ne traite que les sections vides qui ne sont pas des flashcards
    if type_s in ["vocabulaire"]:
        continue  # On garde les flashcards telles quelles
    
    nb_questions = len(section.get("questions", []))
    if nb_questions > 0:
        continue  # Déjà rempli
    
    print(f"🧠 Réparation de : {type_s} ({section.get('titre', '')})")
    
    # On prépare une demande ciblée pour cette section
    if type_s == "grammaire":
        prompt = """
        Génère 5 questions QCM sur la voix active et passive en français.
        Réponds UNIQUEMENT avec ce format JSON (sans texte autour) :
        [{"texte": "Question ?", "choix": ["A", "B", "C", "D"], "bonne": 0}]
        """
    elif type_s == "comprehension_orale":
        prompt = """
        Génère 5 questions QCM sur la compréhension orale du film "Je verrai toujours vos visages" (justice restaurative) et sur l'équithérapie en prison.
        Réponds UNIQUEMENT avec ce format JSON (sans texte autour) :
        [{"texte": "Question ?", "choix": ["A", "B", "C", "D"], "bonne": 0}]
        """
    elif type_s == "comprehension_ecrite":
        prompt = """
        Génère 5 questions QCM sur la compréhension écrite d'une tribune sur la justice restaurative.
        Ajoute aussi un "texte_lecture" de 3-4 phrases.
        Réponds UNIQUEMENT avec ce format JSON (sans texte autour) :
        {"texte_lecture": "...", "questions": [{"texte": "Question ?", "choix": ["A", "B", "C", "D"], "bonne": 0}]}
        """
    elif type_s == "quiz_revision":
        prompt = """
        Génère 10 questions QCM de révision sur le thème "La Justice" (vocabulaire, grammaire, compréhension).
        Réponds UNIQUEMENT avec ce format JSON (sans texte autour) :
        [{"texte": "Question ?", "choix": ["A", "B", "C", "D"], "bonne": 0}]
        """
    else:
        continue
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-120b",
            temperature=0.2,
            max_completion_tokens=2500
        )
        
        txt = response.choices[0].message.content.strip()
        if txt.startswith("```json"): txt = txt[7:-3].strip()
        elif txt.startswith("```"): txt = txt[3:-3].strip()
        
        result = json.loads(txt)
        
        # Si c'est une compréhension écrite, on a un objet {texte_lecture, questions}
        if isinstance(result, dict) and "questions" in result:
            section["texte_lecture"] = result.get("texte_lecture", "")
            section["questions"] = result["questions"]
        else:
            section["questions"] = result
        
        print(f"   ✅ {len(section['questions'])} questions générées")
        
    except Exception as e:
        print(f"   ❌ Erreur : {e}")

# --- Sauvegarde ---
with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n✅ Arbre corrigé et sauvegardé !")
print("\n=== BILAN CAHIER ===")
for s in cahier:
    t = s.get("type")
    nb = len(s.get("questions", s.get("flashcards", [])))
    print(f"  - [{t}] {nb} éléments")
