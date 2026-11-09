#!/usr/bin/env python3
"""
tools/reclassify.py — Reclassifie et enrichit les questions avec Gemini.

Lit data/edito-c1.lecons.json, attribue un type à chaque question
(qcm, texte, tache_ouverte, titre, a_supprimer) et génère des indices
pour les tâches ouvertes.
Écrit le résultat dans data/edito-c1.lecons-v2.json.
"""
import json
import os
import sys
import time
import re
import requests
from pathlib import Path

# Chargement de la clé Gemini
GEMINI_KEY = None
env_path = Path(".env")
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                GEMINI_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
                break

if not GEMINI_KEY:
    print("❌ Clé GEMINI_API_KEY introuvable dans .env")
    sys.exit(1)

INPUT_PATH = "data/edito-c1.lecons.json"
OUTPUT_PATH = "data/edito-c1.lecons-v2.json"

MODELES = [
    "gemini-3.8-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite"
]

PROMPT = """Tu es un expert en ingénierie pédagogique pour le DALF C1.
Voici une question extraite d'un manuel de français :

QUESTION : "{texte}"

Analyse cette question et classe-la dans UNE SEULE des catégories suivantes :
- "qcm" : C'est une vraie question à choix multiple (elle appelle une réponse courte et précise).
- "texte" : C'est un long passage à lire (article, tribune, extrait littéraire) servant de base à des questions.
- "tache_ouverte" : C'est une consigne de production écrite ou orale (ex: "Rédigez un essai", "Débattez en groupe").
- "titre" : C'est un titre de section, un en-tête ou une consigne de lecture (ex: "Compréhension orale", "Lisez le texte").
- "a_supprimer" : C'est du bruit (numéro de page, "Cahier p. 18", des caractères aléatoires).

Réponds UNIQUEMENT par un objet JSON valide au format exact :
{{
  "type": "qcm" | "texte" | "tache_ouverte" | "titre" | "a_supprimer",
  "indices": ["indice 1", "indice 2", "indice 3"]
}}
(Si le type n'est pas "tache_ouverte", le champ "indices" doit être un tableau vide []).
"""


def appeler_gemini(texte):
    prompt = PROMPT.format(texte=texte[:800])
    headers = {"Content-Type": "application/json", "x-goog-api-key": GEMINI_KEY}
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}
    }

    for modele in MODELES:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{modele}:generateContent"
        try:
            r = requests.post(url, headers=headers, json=data, timeout=15)
            if r.status_code == 404:
                continue
            if not r.ok:
                continue

            j = r.json()
            if "candidates" not in j or not j["candidates"]:
                continue

            text = j["candidates"][0]["content"]["parts"][0]["text"]
            text = re.sub(r"```json\s*", "", text)
            text = re.sub(r"```\s*$", "", text)
            
            res = json.loads(text.strip())
            if "type" in res:
                return res
        except Exception:
            continue

    return None


def main():
    if not os.path.exists(INPUT_PATH):
        print(f"❌ Fichier introuvable : {INPUT_PATH}")
        sys.exit(1)

    with open(INPUT_PATH, encoding="utf-8") as f:
        lecons = json.load(f)

    total = sum(len(s["questions"]) for t in lecons["themes"] for c in t["conteneurs"] for s in c["sections"])
    print(f"📖 {total} questions à reclassifier.\n")

    count = 0
    for theme in lecons["themes"]:
        for conteneur in theme["conteneurs"]:
            for section in conteneur["sections"]:
                questions_valides = []
                for q in section["questions"]:
                    count += 1
                    print(f"[{count}/{total}] {q['id']} : {q['texte'][:40]}...", end=" ", flush=True)
                    
                    # On passe les questions trop courtes
                    if len(q["texte"]) < 10:
                        print("⏭️ (trop court, ignoré)")
                        continue

                    res = appeler_gemini(q["texte"])
                    
                    if res:
                        q["type"] = res["type"]
                        q["indices"] = res.get("indices", [])
                        
                        if res["type"] in ("titre", "a_supprimer"):
                            print(f"🗑️ ({res['type']})")
                            continue # On ne garde pas ces questions
                        elif res["type"] == "texte":
                            print("📄 (texte)")
                        elif res["type"] == "tache_ouverte":
                            print("✍️ (tâche ouverte)")
                        else:
                            print("✅ (QCM)")
                        
                        questions_valides.append(q)
                    else:
                        print("⚠️ (échec IA, on garde par défaut)")
                        q["type"] = "qcm"
                        q["indices"] = []
                        questions_valides.append(q)
                    
                    time.sleep(0.5)

                section["questions"] = questions_valides

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(lecons, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Terminé. Fichier écrit : {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
