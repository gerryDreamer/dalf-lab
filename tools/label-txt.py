#!/usr/bin/env python3
"""
tools/label-txt.py — Parsing du TXT Édito C1 (v5).

Version 5 : corrige les bugs de détection de pages/transcriptions/corrigés.

Structure du TXT :
- Pages séparées par des lignes de tirets (--------)
- Chaque page se termine par "NNN I mot" (ex. "198 I cent quatre-vingt-dix-huit")
- Transcriptions : "Page 14, C – Titre" (parfois fusionné avec d'autres colonnes)
- Corrigés : "Page 17, Vocabulaire" (parfois fusionné)

Usage :
    python3 tools/label-txt.py [txt_path]
"""
import json
import re
import sys
import os

# ─── Profil Édito C1 ───
THEMES = [
    {"n": 1,  "titre": "Justice, quelles alternatives ?",          "pages": [11, 22] },
    {"n": 2,  "titre": "SOS démocratie",                           "pages": [23, 38] },
    {"n": 3,  "titre": "Souffler le chaud et le froid",            "pages": [39, 50] },
    {"n": 4,  "titre": "Travail en cours",                         "pages": [51, 68] },
    {"n": 5,  "titre": "Les nouveaux visages de la culture",       "pages": [69, 80] },
    {"n": 6,  "titre": "La vie privée : un droit, une liberté ?",  "pages": [81, 98] },
    {"n": 7,  "titre": "Jouons cartes sur table !",                "pages": [99, 110] },
    {"n": 8,  "titre": "Ma belle famille !",                       "pages": [111, 126] },
    {"n": 9,  "titre": "Villes en mouvement, vies en transition",  "pages": [127, 144] },
    {"n": 10, "titre": "Santé 3.0",                                "pages": [145, 156] },
    {"n": 11, "titre": "Solidarité, un bel élan !",                "pages": [157, 168] },
    {"n": 12, "titre": "Protéger la terre, réparer le vivant",     "pages": [169, 188] },
]

RANGES = {
    "transcription_audio": (198, 217),
    "transcription_video": (218, 221),
    "corrige":             (222, 237),
}

# ─── Regex ───

# Marque de page : "12 I douze", "198 I cent quatre-vingt-dix-huit"
# Accepte "12 I douze" et "12 Idouze" et "12 I  douze"
RE_PAGE_MARK = re.compile(r"(\d{1,3})\s+I\s*\w+")

# Conteneur : ligne isolée "A", "B", "C" (pas "À", "É")
RE_CONTAINER = re.compile(r"^[A-Z]$")

# Section : avec préfixe numérique collé "1 Compréhension audiovisuelle"
RE_SECTION = re.compile(
    r"^\s*(?:\d+\s+)?(Compréhension audiovisuelle|Compréhension orale|Compréhension écrite|"
    r"Production orale|Production écrite|Grammaire|Vocabulaire|Francophonie|"
    r"Fiche méthodologique|Atelier médiation|Documents|Cahier d'activités|"
    r"Produire|À bâtons rompus)\s*$",
    re.I,
)

# Question : 1+ espaces après le numéro, commence par majuscule
RE_QUESTION = re.compile(r"^\s*(\d{1,2})\s+([A-ZÀ-Ý].{5,})$")

# Transcriptions : "Page 14, C – Titre" (search, pas match)
# Capture non-greedy jusqu'à 2+ espaces ou fin de ligne
RE_TRANSCRIPTION = re.compile(r"Page\s+(\d+),\s*([A-Z])\s*[–\-]\s*(.+?)(?:\s{2,}|$)")

# Corrigés : "Page 17, Vocabulaire" (search, pas match)
RE_CORRIGE = re.compile(r"Page\s+(\d+),\s*([A-Za-zÀ-ÿ][\w\s\-'’]*?)(?:\s{2,}|$)")

# Thème
RE_THEME = re.compile(r"^Th[eè]me\s+(\d+)\s+p\.\s*(\d+)", re.I)
RE_THEME_SIMPLE = re.compile(r"^Th[eè]me\s+(\d+)\s*$", re.I)


def normalize_line(line):
    """Nettoie une ligne : espaces insécables, ligatures, apostrophes."""
    line = line.replace("\u00a0", " ").replace("\u202f", " ").replace("\u200b", " ")
    line = line.replace("ﬁ", "fi").replace("ﬂ", "fl")
    line = line.replace("ﬀ", "ff").replace("ﬃ", "ffi").replace("ﬄ", "ffl")
    line = line.replace("’", "'").replace("‘", "'")
    line = line.replace("–", "-").replace("—", "-")
    line = re.sub(r"[ \t]+", " ", line)
    return line.strip()


def theme_of_page(page_n):
    if page_n is None:
        return None
    for t in THEMES:
        a, b = t["pages"]
        if a <= page_n <= b:
            return t["n"]
    return None


def detect_range_type(page_n):
    if page_n is None:
        return "livre"
    for rtype, (a, b) in RANGES.items():
        if a <= page_n <= b:
            return rtype
    return "livre"


def detect_rtype_by_content(page_lines):
    """Fallback : détecter le type de page par le contenu."""
    text = " ".join(page_lines).lower()
    if "documents audios" in text or ("transcriptions" in text and "audios" in text):
        return "transcription_audio"
    if "documents vidéos" in text or ("transcriptions" in text and "vidéos" in text):
        return "transcription_video"
    if "corrigés" in text:
        return "corrige"
    return "livre"


def parse_txt(txt_path):
    with open(txt_path, encoding="utf-8") as f:
        raw = f.read()

    # Normalisation globale
    raw = raw.replace("\u00a0", " ").replace("\u202f", " ").replace("\u200b", " ")
    raw = raw.replace("ﬁ", "fi").replace("ﬂ", "fl")
    raw = raw.replace("ﬀ", "ff").replace("ﬃ", "ffi").replace("ﬄ", "ffl")
    raw = raw.replace("’", "'").replace("‘", "'")
    raw = raw.replace("–", "-").replace("—", "-")

    # Debug
    n_trans_lines = sum(1 for l in raw.split("\n") if re.search(r"Page\s+\d+,\s*[A-Z]\s*[–\-]", l))
    n_corr_lines = sum(1 for l in raw.split("\n") if re.search(r"Page\s+\d+,\s*[A-Za-zÀ-ÿ]", l) and not re.search(r"Page\s+\d+,\s*[A-Z]\s*[–\-]", l))
    print(f"  Lignes 'Page XX, [A-Z] - ...' : {n_trans_lines}")
    print(f"  Lignes 'Page XX, Titre'       : {n_corr_lines}")

    # Découper par pages : séparateur = 10+ tirets
    pages_raw = re.split(r"-{10,}", raw.replace("\f", "\n--------PAGE--------\n"))
    print(f"  {len(pages_raw)} pages détectées")

    themes_data = {t["n"]: {
        "n": t["n"], "titre": t["titre"], "pages": t["pages"],
        "conteneurs": [], "sections_directes": [],
    } for t in THEMES}

    transcriptions = []
    corriges = []

    current_theme = None
    current_conteneur = None
    current_section = None
    pending_question = None

    def flush_question():
        nonlocal pending_question
        if pending_question and current_section is not None:
            current_section["questions"].append(pending_question)
        pending_question = None

    def flush_section():
        nonlocal current_section
        flush_question()
        current_section = None

    def flush_conteneur():
        nonlocal current_conteneur
        flush_section()
        if current_conteneur and current_conteneur["sections"]:
            if current_theme is not None:
                themes_data[current_theme]["conteneurs"].append(current_conteneur)
        current_conteneur = None

    for page_idx, page_raw in enumerate(pages_raw):
        page_lines = [normalize_line(l) for l in page_raw.split("\n")]
        page_lines = [l for l in page_lines if l]

        if not page_lines:
            continue

        # Détecter le numéro de page : chercher dans TOUTE la page, prendre le dernier
        page_n = None
        for line in page_lines:
            m = RE_PAGE_MARK.search(line)
            if m:
                n = int(m.group(1))
                if 1 <= n <= 250:
                    page_n = n

        # Détecter le type : par page_n si trouvé, sinon par le contenu
        if page_n is not None:
            rtype = detect_range_type(page_n)
        else:
            rtype = detect_rtype_by_content(page_lines)

        page_theme = theme_of_page(page_n)

        if page_theme is not None and current_theme != page_theme:
            flush_conteneur()
            current_theme = page_theme

        for line in page_lines:
            # Thème explicite
            m = RE_THEME.match(line) or RE_THEME_SIMPLE.match(line)
            if m:
                n = int(m.group(1))
                if n in themes_data:
                    flush_conteneur()
                    current_theme = n
                continue

            # ── Transcriptions ──
            if rtype in ("transcription_audio", "transcription_video"):
                m = RE_TRANSCRIPTION.search(line)
                if m:
                    # Vérifier qu'on n'a pas déjà cette transcription
                    page_livre = int(m.group(1))
                    titre = m.group(3).strip()
                    if not any(t["page_livre"] == page_livre and t["titre"] == titre for t in transcriptions):
                        transcriptions.append({
                            "page_livre": page_livre,
                            "document": m.group(2),
                            "titre": titre,
                            "page_pdf": page_n,
                            "source": "audio" if rtype == "transcription_audio" else "video",
                            "theme": theme_of_page(page_livre),
                            "texte": [],
                        })
                    continue
                if transcriptions and len(line) > 3 and not RE_PAGE_MARK.match(line):
                    transcriptions[-1]["texte"].append(line)
                    continue

            # ── Corrigés ──
            if rtype == "corrige":
                m = RE_CORRIGE.search(line)
                if m:
                    page_livre = int(m.group(1))
                    titre = m.group(2).strip()
                    if not any(c["page_livre"] == page_livre and c["titre"] == titre for c in corriges):
                        corriges.append({
                            "page_livre": page_livre,
                            "titre": titre,
                            "page_pdf": page_n,
                            "theme": theme_of_page(page_livre),
                            "texte": [],
                        })
                    continue
                if corriges and len(line) > 3 and not RE_PAGE_MARK.match(line):
                    corriges[-1]["texte"].append(line)
                    continue

            # ── Contenu du manuel ──
            if current_theme is None:
                continue

            # Conteneur ?
            if RE_CONTAINER.match(line):
                flush_conteneur()
                current_conteneur = {
                    "etiquette": line,
                    "titre": "",
                    "page": page_n,
                    "sections": [],
                }
                continue

            # Titre du conteneur en attente
            if current_conteneur and not current_conteneur["titre"]:
                if line in ("À", "[]", "Documents", "A", "B", "C") or len(line) < 5:
                    continue
                if RE_PAGE_MARK.match(line):
                    continue
                if not RE_SECTION.match(line) and not RE_QUESTION.match(line):
                    current_conteneur["titre"] = line
                    continue

            # Section ?
            m = RE_SECTION.match(line)
            if m:
                flush_section()
                sec_name = m.group(1).lower().replace(" ", "_")
                target = (current_conteneur["sections"]
                          if current_conteneur
                          else themes_data[current_theme]["sections_directes"])
                target.append({
                    "type": sec_name,
                    "page": page_n,
                    "questions": [],
                })
                current_section = target[-1]
                continue

            # Question ?
            m = RE_QUESTION.match(line)
            if m and current_section is not None:
                flush_question()
                pending_question = {"n": int(m.group(1)), "texte": m.group(2).strip()}
                continue

            # Continuation
            if pending_question is not None:
                pending_question["texte"] += " " + line

    flush_conteneur()

    for t in transcriptions + corriges:
        t["texte"] = "\n".join(t["texte"]).strip()

    return themes_data, transcriptions, corriges


def main(txt_path, out_dir="data"):
    if not os.path.exists(txt_path):
        print(f"❌ Fichier introuvable : {txt_path}", file=sys.stderr)
        sys.exit(1)

    print(f"📖 Parsing : {txt_path}")
    themes_data, transcriptions, corriges = parse_txt(txt_path)

    os.makedirs(out_dir, exist_ok=True)

    manuel = {"themes": [themes_data[t["n"]] for t in THEMES]}
    with open(os.path.join(out_dir, "edito-c1.manuel.json"), "w", encoding="utf-8") as f:
        json.dump(manuel, f, ensure_ascii=False, indent=2)

    ressources = {"transcriptions": transcriptions, "corriges": corriges}
    with open(os.path.join(out_dir, "edito-c1.ressources.json"), "w", encoding="utf-8") as f:
        json.dump(ressources, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Écrit dans {out_dir}/")
    print(f"\n📊 Statistiques :")
    for t in manuel["themes"]:
        nq = sum(len(s["questions"]) for c in t["conteneurs"] for s in c["sections"])
        ns = sum(len(c["sections"]) for c in t["conteneurs"])
        nd = len(t["sections_directes"])
        print(f"  Thème {t['n']:2} : {len(t['conteneurs'])} conteneurs, {ns} sections, {nq} questions, {nd} sections directes")

    print(f"\n  Transcriptions : {len(transcriptions)}")
    print(f"  Corrigés       : {len(corriges)}")


if __name__ == "__main__":
    txt_path = sys.argv[1] if len(sys.argv) > 1 else "text-edito.txt"
    main(txt_path)
