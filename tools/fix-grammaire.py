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

with open("data/edito-c1.final-tree.json", encoding="utf-8") as f:
    data = json.load(f)

theme1 = data["themes"][0]

for section in theme1["parties"]["cahier"]["sections"]:
    if section.get("type") == "grammaire":
        print("🧠 Génération de l'échauffement et de la règle...")
        
        prompt = """
        Tu es un professeur de français expert en DALF C1.
        Génère le contenu pour une leçon de grammaire sur "La voix active et la voix passive".
        
        Format de sortie JSON strict :
        {
          "echauffement": "Un court texte d'introduction (2-3 phrases) qui présente la notion.",
          "fonctionnement": "La règle de grammaire expliquée clairement (4-5 phrases).",
          "exercices_qcm": [
            {"texte": "Question ?", "choix": ["A", "B", "C", "D"], "bonne": 0}
          ]
        }
        """
        
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="openai/gpt-oss-120b",
                temperature=0.2,
                max_completion_tokens=3000
            )
            txt = response.choices[0].message.content.strip()
            if txt.startswith("```json"): txt = txt[7:-3].strip()
            elif txt.startswith("```"): txt = txt[3:-3].strip()
            
            contenu = json.loads(txt)
            section["echauffement"] = contenu.get("echauffement", "")
            section["fonctionnement"] = contenu.get("fonctionnement", "")
            section["exercices_qcm"] = contenu.get("exercices_qcm", [])
            
            print(f"✅ Échauffement : {len(section['echauffement'])} caractères")
            print(f"✅ Règle : {len(section['fonctionnement'])} caractères")
            print(f"✅ QCM : {len(section['exercices_qcm'])} questions")
            
        except Exception as e:
            print(f"❌ Erreur : {e}")

with open("data/edito-c1.final-tree.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n✅ Sauvegardé !")
