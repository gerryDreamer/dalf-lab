#!/usr/bin/env python3
import json, os, sys, re, time, requests, pdfplumber
from pathlib import Path

ENV = {}
if Path(".env").exists():
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                ENV[k.strip()] = v.strip().strip('"').strip("'")

GEMINI_KEY = ENV.get("GEMINI_API_KEY")
GROQ_KEY = ENV.get("GROQ_API_KEY") or ENV.get("GROK_API_KEY")

def extraire_texte_pdf(pdf_path):
    texte = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            texte.append(f"--- PAGE {i+1} ---\n{text}")
    return "\n".join(texte)

def construire_prompt(texte_pdf, questions_json, theme_n, taille_max):
    questions_reduites = [{"c": q["conteneur"], "t": q["texte"][:80]} for q in questions_json]
    return f"""Reconstruis le Thème {theme_n} d'Édito C1. Renvoie UNIQUEMENT du JSON.
Texte PDF :
{texte_pdf[:taille_max]}
Questions :
{json.dumps(questions_reduites, ensure_ascii=False)}
Format : {{ "theme": {theme_n}, "titre": "...", "parties": {{ "manuel": {{ "conteneurs": [...] }}, "cahier": {{ "sections": [...] }} }} }}"""

def appeler_groq(prompt):
    if not GROQ_KEY: return None
    print("🤖 [Groq] Essai...")
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
            json={
                "model": "openai/gpt-oss-120b",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "max_tokens": 4000,
                "response_format": {"type": "json_object"}
            },
            timeout=120
        )
        if not r.ok:
            print(f"   ❌ Erreur {r.status_code} : {r.text[:100]}")
            return None
        j = r.json()
        text = j["choices"][0]["message"]["content"]
        text = re.sub(r"```json\s*", "", text)
        text = re.sub(r"```\s*$", "", text)
        return json.loads(text.strip())
    except Exception as e:
        print(f"   ❌ Échec : {e}")
        return None

def main():
    theme_n = int(sys.argv[1])
    pdf_path = f"themes/T{theme_n}.pdf"
    with open("data/edito-c1.lecons-v2.json", encoding="utf-8") as f:
        lecons = json.load(f)
    
    theme_data = next((t for t in lecons["themes"] if t["n"] == theme_n), None)
    questions_aplaties = []
    for c in theme_data["conteneurs"]:
        for s in c["sections"]:
            for q in s["questions"]:
                questions_aplaties.append({"conteneur": c["etiquette"], "texte": q["texte"]})

    texte_pdf = extraire_texte_pdf(pdf_path)
    prompt = construire_prompt(texte_pdf, questions_aplaties, theme_n, 2500)
    
    print(f"🔧 Reconstruction Thème {theme_n}...")
    resultat = appeler_groq(prompt)

    if resultat:
        with open(f"data/edito-c1.theme{theme_n}.json", "w", encoding="utf-8") as f:
            json.dump(resultat, f, ensure_ascii=False, indent=2)
        print(f"✅ Succès Thème {theme_n} !")
    else:
        print(f"❌ Échec Thème {theme_n}.")

if __name__ == "__main__":
    main()
