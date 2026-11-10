#!/usr/bin/env python3
"""
tools/compare-sources.py — Compare les sources PDF et TXT.

Analyse les deux sources et génère un rapport de comparaison :
- Nombre de pages
- Nombre de conteneurs détectés
- Nombre de sections
- Nombre de questions
- Nombre de transcriptions/corrigés
- Facilité de parsing

Usage :
    python3 tools/compare-sources.py
"""
import json
import re
import os
import sys
import unicodedata
from collections import Counter

# ─── Profil ───
CONTAINERS = {
    1: ["Je verrai toujours vos visages", "Vers un horizon d'apaisement", "L'équithérapie en prison"],
    2: ["Tu voteras oui ou oui au référendum", "Comment les populistes", "La crise démocratique", "Quand les jeunes se mêlent", "Tu sais pour qui"],
    3: ["Change toujours", "Changer de métier", "Le changement, ça s'accompagne"],
    4: ["Que faire contre le gaspi", "Mourir de chaud", "Petite et grande histoire du chauffage", "Kumulus", "Tahiti", "Ça nous paraît aberrant"],
    5: ["Les jeunes et la culture", "Les publics des musées", "Liseuse versus livre"],
    6: ["Les jouets ont-ils un genre", "C'est quoi, le féminisme", "Une bibliothèque féministe", "Être un homme aujourd'hui", "Vie commune", "On ne peut plus rien dire"],
    7: ["Requiem pour un joueur", "Jouer pour guérir", "Le jeu des 1 000 euros"],
    8: ["Mode d'emploi pour les grands-parents", "Alors, cette rentrée", "Ils ont un enfant à trois", "Belles-mères, les grandes invisibles", "Belles-mères au bord de la crise", "Sous contrôle parental"],
    9: ["Vieillir sans en avoir le droit", "Le sentiment de l'âge", "C'est pas tous les jours"],
    10: ["Science friction", "Résistance 2050", "SonarVision", "Quand marcher redevient possible", "Les technologies de la santé", "Je n'arrive pas à faire mon choix"],
    11: ["Les bienfaits des comportements de solidarité", "Poursuivi pour délit de solidarité", "Tu souhaites t'engager"],
    12: ["Le vivant entre dans le champ politique", "Pour une nouvelle conception des animaux", "Loup, comment vivre avec", "Madagascar : à la découverte", "Une forêt primaire", "Je m'émerveille de voir un animal sauvage"],
}

def nz(s):
    s = s.lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9' ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

# ─── Analyse du TXT ───
def analyze_txt(txt_path):
    with open(txt_path, encoding="utf-8") as f:
        raw = f.read()
    raw = raw.replace("\u00a0", " ").replace("\u202f", " ").replace("\u200b", " ")
    raw = raw.replace("ﬁ", "fi").replace("ﬂ", "fl")
    raw = raw.replace("’", "'").replace("–", "-").replace("—", "-")
    
    pages = re.split(r"-{10,}", raw.replace("\f", "\n--------PAGE--------\n"))
    pages = [p for p in pages if p.strip()]
    
    results = {
        "source": "TXT",
        "fichier": txt_path,
        "pages": len(pages),
        "conteneurs": 0,
        "sections": 0,
        "questions": 0,
        "transcriptions": 0,
        "corriges": 0,
        "details": {},
    }
    
    for theme_n, titres in CONTAINERS.items():
        theme_found = []
        for titre in titres:
            titre_nz = nz(titre)
            found = False
            for page in pages:
                if titre_nz in nz(page):
                    found = True
                    break
            if found:
                theme_found.append(titre)
        results["details"][f"T{theme_n}"] = {
            "attendu": len(titres),
            "trouve": len(theme_found),
            "manquants": [t for t in titres if t not in theme_found],
        }
    
    results["conteneurs"] = sum(d["trouve"] for d in results["details"].values())
    
    # Compter les questions
    results["questions"] = sum(1 for l in raw.split("\n") if re.match(r"^\s*(\d{1,2})\s+[A-ZÀ-Ý].{5,}$", l))
    
    # Compter les sections
    section_types = ["Compréhension audiovisuelle", "Compréhension orale", "Compréhension écrite",
                     "Production orale", "Production écrite", "Grammaire", "Vocabulaire", "Francophonie"]
    results["sections"] = sum(1 for l in raw.split("\n") if any(s in l for s in section_types))
    
    # Compter les transcriptions/corrigés
    results["transcriptions"] = sum(1 for l in raw.split("\n") if re.search(r"Page\s+\d+,\s*[A-Z]\s*[–\-]", l))
    results["corriges"] = sum(1 for l in raw.split("\n") if re.search(r"Page\s+\d+,\s*(Vocabulaire|Grammaire|À bâtons rompus|Produire)", l, re.I))
    
    return results

# ─── Analyse du PDF ───
def analyze_pdf(pdf_path):
    try:
        import pdfplumber
    except ImportError:
        print("⚠️ pdfplumber non installé. Lance : pip install pdfplumber")
        return None
    
    results = {
        "source": "PDF",
        "fichier": pdf_path,
        "pages": 0,
        "conteneurs": 0,
        "sections": 0,
        "questions": 0,
        "transcriptions": 0,
        "corriges": 0,
        "details": {},
    }
    
    with pdfplumber.open(pdf_path) as pdf:
        results["pages"] = len(pdf.pages)
        
        all_text = ""
        for page in pdf.pages:
            text = page.extract_text() or ""
            all_text += text + "\n"
    
    # Compter les conteneurs (matching par titre)
    for theme_n, titres in CONTAINERS.items():
        theme_found = []
        for titre in titres:
            titre_nz = nz(titre)
            if titre_nz in nz(all_text):
                theme_found.append(titre)
        results["details"][f"T{theme_n}"] = {
            "attendu": len(titres),
            "trouve": len(theme_found),
            "manquants": [t for t in titres if t not in theme_found],
        }
    results["conteneurs"] = sum(d["trouve"] for d in results["details"].values())
    
    # Compter les questions
    results["questions"] = sum(1 for l in all_text.split("\n") if re.match(r"^\s*(\d{1,2})\s+[A-ZÀ-Ý].{5,}$", l))
    
    # Compter les sections
    section_types = ["Compréhension audiovisuelle", "Compréhension orale", "Compréhension écrite",
                     "Production orale", "Production écrite", "Grammaire", "Vocabulaire", "Francophonie"]
    results["sections"] = sum(1 for l in all_text.split("\n") if any(s in l for s in section_types))
    
    # Compter les transcriptions/corrigés
    results["transcriptions"] = sum(1 for l in all_text.split("\n") if re.search(r"Page\s+\d+,\s*[A-Z]\s*[–\-]", l))
    results["corriges"] = sum(1 for l in all_text.split("\n") if re.search(r"Page\s+\d+,\s*(Vocabulaire|Grammaire|À bâtons rompus|Produire)", l, re.I))
    
    return results

# ─── Rapport ───
def print_report(txt_results, pdf_results):
    print("\n" + "=" * 70)
    print("📊 COMPARAISON DES SOURCES")
    print("=" * 70)
    
    print(f"\n{'Métrique':<30} {'TXT':<20} {'PDF':<20}")
    print("-" * 70)
    
    metrics = [
        ("Pages", "pages"),
        ("Conteneurs (sur 53)", "conteneurs"),
        ("Sections", "sections"),
        ("Questions", "questions"),
        ("Transcriptions (sur 34)", "transcriptions"),
        ("Corrigés (sur 48)", "corriges"),
    ]
    
    for label, key in metrics:
        txt_val = txt_results.get(key, "?")
        pdf_val = pdf_results.get(key, "?") if pdf_results else "N/A"
        print(f"{label:<30} {str(txt_val):<20} {str(pdf_val):<20}")
    
    print("\n" + "=" * 70)
    print("📋 DÉTAIL PAR THÈME")
    print("=" * 70)
    
    for theme_n in CONTAINERS.keys():
        txt_d = txt_results["details"].get(f"T{theme_n}", {})
        pdf_d = pdf_results["details"].get(f"T{theme_n}", {}) if pdf_results else {}
        
        txt_status = f"{txt_d.get('trouve', '?')}/{txt_d.get('attendu', '?')}"
        pdf_status = f"{pdf_d.get('trouve', '?')}/{pdf_d.get('attendu', '?')}" if pdf_results else "N/A"
        
        print(f"T{theme_n:2} : TXT={txt_status:<10} PDF={pdf_status:<10} ", end="")
        
        if txt_d.get("manquants"):
            print(f"❌ TXT manque: {', '.join(txt_d['manquants'][:2])}")
        elif pdf_d.get("manquants"):
            print(f"❌ PDF manque: {', '.join(pdf_d['manquants'][:2])}")
        else:
            print("✅")
    
    print("\n" + "=" * 70)
    print("💡 VERDICT")
    print("=" * 70)
    
    if txt_results["conteneurs"] >= 50:
        print("✅ TXT : excellent (50+ conteneurs trouvés)")
    elif txt_results["conteneurs"] >= 40:
        print("⚠️ TXT : bon (40-50 conteneurs)")
    else:
        print("❌ TXT : insuffisant (<40 conteneurs)")
    
    if pdf_results:
        if pdf_results["conteneurs"] >= 50:
            print("✅ PDF : excellent (50+ conteneurs trouvés)")
        elif pdf_results["conteneurs"] >= 40:
            print("⚠️ PDF : bon (40-50 conteneurs)")
        else:
            print("❌ PDF : insuffisant (<40 conteneurs)")
    else:
        print("⚠️ PDF : non analysé (pdfplumber non installé)")
    
    print("\n💡 Recommandation :")
    if txt_results["conteneurs"] >= (pdf_results["conteneurs"] if pdf_results else 0):
        print("   → Utiliser le TXT (meilleur matching)")
    else:
        print("   → Utiliser le PDF (meilleur matching)")

# ─── Main ───
def main():
    txt_path = "text-edito.txt"
    pdf_path = "edito.pdf"
    
    if not os.path.exists(txt_path):
        print(f"❌ TXT introuvable : {txt_path}")
        return
    
    print(f"📖 Analyse du TXT : {txt_path}")
    txt_results = analyze_txt(txt_path)
    
    pdf_results = None
    if os.path.exists(pdf_path):
        print(f"📖 Analyse du PDF : {pdf_path}")
        pdf_results = analyze_pdf(pdf_path)
    else:
        print(f"⚠️ PDF introuvable : {pdf_path} (analyse TXT uniquement)")
    
    print_report(txt_results, pdf_results)
    
    # Sauvegarde
    with open("tools/out/compare-sources.json", "w", encoding="utf-8") as f:
        json.dump({"txt": txt_results, "pdf": pdf_results}, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Rapport sauvegardé : tools/out/compare-sources.json")

if __name__ == "__main__":
    os.makedirs("tools/out", exist_ok=True)
    main()
