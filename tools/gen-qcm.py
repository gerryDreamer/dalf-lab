#!/usr/bin/env python3
"""
tools/gen-qcm.py — Génération automatique de QCM (Groq + Gemini).
"""
import json
import os
import sys
import time
import re
import requests
from pathlib import Path

# ─── Chargement des clés .env ───
ENV = {}
env_path = Path(".env")
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                ENV[k.strip()] = v.strip().strip('"').strip("'")

GROQ_KEY = ENV.get("GROQ_API_KEY") or ENV.get("GROK_API_KEY")
GEMINI_KEY = ENV.get("GEMINI_API_KEY")

if not GROQ_KEY and not GEMINI_KEY:
    print("❌ Aucune clé API trouvée dans .env")
    sys.exit(1)

if GROQ_KEY:
    print("✅ Clé Groq chargée")
if GEMINI_KEY:
    print("✅ Clé Gemini chargée")

# ─── Clients ───
try:
    from groq import Groq
    groq_client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None
except ImportError:
    groq_client = None

INPUT_PATH = "data/edito-c1.lecons.json"
OUTPUT_PATH = "tools/out/lecons-auto.json"

PROMPT_TEMPLATE = """Tu es un professeur de FLE préparant au DALF C1.
Voici une question issue d'un manuel de français :

Question : "{question}"
{contexte}

Génère un QCM (Question à Choix Multiples) de 4 propositions pour cette question.
La question doit être claire et la bonne réponse doit être indiscutable.

Réponds UNIQUEMENT par un objet JSON valide, sans texte autour, au format exact :
{{
  "choix": ["proposition 1", "proposition 2", "proposition 3", "proposition 4"],
  "bonne": 0
}}
"""

def valider_qcm(qcm):
    if "choix" not in qcm or "bonne" not in qcm: return "Structure JSON invalide"
    if len(qcm["choix"]) != 4: return f"Attendu 4 choix, reçu {len(qcm['choix'])}"
    if not (0 <= qcm["bonne"] <= 3): return f"Index 'bonne' invalide"
    return None

def appeler_groq(question, contexte):
    if not groq_client: return None, "Client Groq non initialisé"
    prompt = PROMPT_TEMPLATE.format(question=question, contexte=contexte)
    try:
        res = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-120b",
            temperature=0.2,
            max_tokens=1024,
            response_format={"type": "json_object"}
        )
        qcm = json.loads(res.choices[0].message.content)
        err = valider_qcm(qcm)
        return (qcm, None) if not err else (None, err)
    except Exception as e:
        return None, str(e)

def appeler_gemini(question, contexte):
    if not GEMINI_KEY: 
        return None, "Pas de clé Gemini"
    
    # 1. Tronquer la question si elle est trop longue
    question_courte = question[:500] if len(question) > 500 else question
    prompt = PROMPT_TEMPLATE.format(question=question_courte, contexte=contexte)
    
    modeles = [
        "gemini-3.8-flash",
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite"
    ]

    headers = {"Content-Type": "application/json", "x-goog-api-key": GEMINI_KEY}
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}
    }

    derniere_erreur = "Aucun modèle n'a fonctionné"

    for modele in modeles:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{modele}:generateContent"
        try:
            print(f"[essai {modele}] ", end="", flush=True)
            # 2. Timeout réduit à 15 secondes
            r = requests.post(url, headers=headers, json=data, timeout=15)
            
            if r.status_code == 404:
                continue
            
            if not r.ok:
                derniere_erreur = f"HTTP {r.status_code}"
                continue

            j = r.json()
            if "candidates" not in j or not j["candidates"]:
                derniere_erreur = "Réponse vide Gemini"
                continue

            text = j["candidates"][0]["content"]["parts"][0]["text"]
            text = re.sub(r"```json\s*", "", text)
            text = re.sub(r"```\s*$", "", text)
            
            qcm = json.loads(text.strip())
            err = valider_qcm(qcm)
            
            if not err:
                return qcm, None
            else:
                derniere_erreur = err

        except requests.exceptions.Timeout:
            derniere_erreur = "Timeout (trop long)"
            continue # On passe au modèle suivant ou on abandonne
        except Exception as e:
            derniere_erreur = str(e)
            continue

    return None, derniere_erreur
def main():
    if not os.path.exists(INPUT_PATH):
        print(f"❌ Fichier introuvable : {INPUT_PATH}")
        sys.exit(1)
        
    with open(INPUT_PATH, encoding="utf-8") as f:
        lecons = json.load(f)

    os.makedirs("tools/out", exist_ok=True)
    progress = {}
    if os.path.exists(OUTPUT_PATH):
        with open(OUTPUT_PATH, encoding="utf-8") as f:
            progress = json.load(f)
        print(f"🔄 Reprise : {len(progress)} QCM déjà générés.")

    total = sum(len(q) for t in lecons["themes"] for c in t["conteneurs"] for s in c["sections"] for q in [s["questions"]])
    # Correction du calcul total :
    total = sum(len(s["questions"]) for t in lecons["themes"] for c in t["conteneurs"] for s in c["sections"])
    
    print(f"📖 {total} questions à traiter.\n")

    count = 0
    for theme in lecons["themes"]:
        for conteneur in theme["conteneurs"]:
            for section in conteneur["sections"]:
                for q in section["questions"]:
                    count += 1
                    qid = q["id"]
                    
                    if qid in progress: continue
                    if len(q["texte"]) < 10: continue
                    
                    contexte = f"Thème : {theme['titre']}. Conteneur : {conteneur['titre']}."
                    print(f"[{count}/{total}] {qid} : {q['texte'][:40]}...", end=" ", flush=True)
                    
                    # 1. On essaie Gemini
                    qcm, err = appeler_gemini(q["texte"], contexte)
                    
                    # 2. Si Gemini échoue (rate limit, etc.), on bascule sur Groq
                    if not qcm and groq_client:
                        print("(Gemini HS, essai Groq) ", end="", flush=True)
                        qcm, err = appeler_groq(q["texte"], contexte)
                    
                    if qcm:
                        progress[qid] = qcm
                        print("✅")
                        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
                            json.dump(progress, f, ensure_ascii=False, indent=2)
                    else:
                        print(f"❌ ({err})")
                        time.sleep(2)

                    time.sleep(0.5) # Pause entre les requêtes

    print(f"\n✅ Terminé. {len(progress)} QCM générés.")
    print(f"📁 Résultat : {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
