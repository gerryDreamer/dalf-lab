#!/usr/bin/env python3
"""
tools/label-pdf.py — Parsing des PDF de thèmes Édito C1.

Version 1 :
- 1 PDF = 1 thème (T1.pdf à T12.pdf)
- Extraction native avec pdfplumber (layout=True)
- Séparation manuel/cahier par page
- Détection des conteneurs (A, B, C...) par titre
- Détection des sections et questions
- Fallback OCR (optionnel, si pages vides)

Usage :
    python3 tools/label-pdf.py [themes_dir]
"""
import json
import re
import sys
import os
import unicodedata

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

# ─── Conteneurs par thème (fournis manuellement) ───
CONTAINERS = {
    1: [
        {"lettre": "A", "titre": "Je verrai toujours vos visages"},
        {"lettre": "B", "titre": "Vers un horizon d'apaisement"},
        {"lettre": "C", "titre": "L'équithérapie en prison"},
    ],
    2: [
        {"lettre": "A", "titre": "Tu voteras oui ou oui au référendum"},
        {"lettre": "B", "titre": "Comment les populistes s'introduisent dans les démocraties"},
        {"lettre": "C", "titre": "La crise démocratique est devenue structurelle"},
        {"lettre": "D", "titre": "Quand les jeunes se mêlent de politique"},
        {"lettre": "E", "titre": "Tu sais pour qui tu vas voter"},
    ],
    3: [
        {"lettre": "A", "titre": "Change toujours, tu m'intéresses"},
        {"lettre": "B", "titre": "Changer de métier, oui"},
        {"lettre": "C", "titre": "Le changement, ça s'accompagne"},
    ],
    4: [
        {"lettre": "A", "titre": "Que faire contre le gaspi"},
        {"lettre": "B", "titre": "Mourir de chaud"},
        {"lettre": "C", "titre": "Petite et grande histoire du chauffage"},
        {"lettre": "D", "titre": "Kumulus, le générateur d'eau atmosphérique et solaire"},
        {"lettre": "E", "titre": "Tahiti, l'hôpital climatisé grâce à l'eau de mer"},
        {"lettre": "F", "titre": "Ça nous paraît aberrant d'arroser l'hiver"},
    ],
    5: [
        {"lettre": "A", "titre": "Les jeunes et la culture"},
        {"lettre": "B", "titre": "Les publics des musées, visiteurs ou acteurs"},
        {"lettre": "C", "titre": "Liseuse versus livre, le match"},
    ],
    6: [
        {"lettre": "A", "titre": "Les jouets ont-ils un genre"},
        {"lettre": "B", "titre": "C'est quoi, le féminisme"},
        {"lettre": "C", "titre": "Une bibliothèque féministe"},
        {"lettre": "D", "titre": "Être un homme aujourd'hui"},
        {"lettre": "E", "titre": "Vie commune"},
        {"lettre": "F", "titre": "On ne peut plus rien dire"},
    ],
    7: [
        {"lettre": "A", "titre": "Requiem pour un joueur"},
        {"lettre": "B", "titre": "Jouer pour guérir"},
        {"lettre": "C", "titre": "Le jeu des 1 000 euros"},
    ],
    8: [
        {"lettre": "A", "titre": "Mode d'emploi pour les grands-parents"},
        {"lettre": "B", "titre": "Alors, cette rentrée"},
        {"lettre": "C", "titre": "Ils ont un enfant à trois et ne vivent pas ensemble"},
        {"lettre": "D", "titre": "Belles-mères, les grandes invisibles"},
        {"lettre": "E", "titre": "Belles-mères au bord de la crise de nerfs"},
        {"lettre": "F", "titre": "Sous contrôle parental"},
    ],
    9: [
        {"lettre": "A", "titre": "Vieillir sans en avoir le droit"},
        {"lettre": "B", "titre": "Le sentiment de l'âge"},
        {"lettre": "C", "titre": "C'est pas tous les jours qu'on prend sa retraite"},
    ],
    10: [
        {"lettre": "A", "titre": "Science friction"},
        {"lettre": "B", "titre": "Résistance 2050"},
        {"lettre": "C", "titre": "SonarVision, un guide pour les personnes déficientes visuelles"},
        {"lettre": "D", "titre": "Quand marcher redevient possible"},
        {"lettre": "E", "titre": "Les technologies de la santé au service des soins à domicile"},
        {"lettre": "F", "titre": "Je n'arrive pas à faire mon choix"},
    ],
    11: [
        {"lettre": "A", "titre": "Les bienfaits des comportements de solidarité"},
        {"lettre": "B", "titre": "Poursuivi pour délit de solidarité"},
        {"lettre": "C", "titre": "Tu souhaites t'engager toi aussi"},
    ],
    12: [
        {"lettre": "A", "titre": "Le vivant entre dans le champ politique"},
        {"lettre": "B", "titre": "Pour une nouvelle conception des animaux"},
        {"lettre": "C", "titre": "Loup, comment vivre avec"},
        {"lettre": "D", "titre": "Madagascar : à la découverte du parc d'Andasibe-Mantadia"},
        {"lettre": "E", "titre": "Une forêt primaire en Europe de l'Ouest"},
        {"lettre": "F", "titre": "Je m'émerveille de voir un animal sauvage, mais"},
    ],
}

# ─── Regex ───
RE_SECTION = re.compile(
    r"^\s*(?:\d+\s+)?(Compréhension audiovisuelle|Compréhension orale|Compréhension écrite|"
    r"Production orale|Production écrite|Grammaire|Vocabulaire|Francophonie|"
    r"Fiche méthodologique|Atelier médiation|Documents|Cahier d'activités|"
    r"Produire|À bâtons rompus)\s*$",
    re.I,
)
RE_QUESTION = re.compile(r"^\s*(\d{1,2})\s+([A-ZÀ-Ý].{5,})$")
RE_CAHIER = re.compile(r"^\s*Cahier\s*$", re.I)


def nz(s):
    s = s.lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("œ", "oe").replace("æ", "ae")
    s = s.replace("’", "'").replace("‘", "'")
    s = s.replace("–", "-").replace("—", "-")
    s = re.sub(r"[^a-z0-9' ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def normalize_line(line):
    line = line.replace("\u00a0", " ").replace("\u202f", " ").replace("\u200b", " ")
    line = line.replace("ﬁ", "fi").replace("ﬂ", "fl")
    line = line.replace("ﬀ", "ff").replace("ﬃ", "ffi").replace("ﬄ", "ffl")
    line = line.replace("’", "'").replace("‘", "'")
    line = line.replace("–", "-").replace("—", "-")
    line = re.sub(r"[ \t]+", " ", line)
    return line.strip()


def match_container(text, theme_n):
    if theme_n is None or theme_n not in CONTAINERS:
        return None
    text_stripped = text.strip()
    text_nz = nz(text_stripped)
    if len(text_nz) < 5:
        return None

    for c in CONTAINERS[theme_n]:
        titre_nz = nz(c["titre"])
        # 1. Match exact en début de ligne
        if text_nz.startswith(titre_nz):
            return (c["lettre"], c["titre"])
        # 2. Match avec lettre devant (A, B, C... même avec espaces multiples)
        if re.match(rf"^[a-g]\s+{re.escape(titre_nz)}", text_nz):
            return (c["lettre"], c["titre"])
        # 3. Match partiel : 3 premiers mots du titre dans le texte
        mots = titre_nz.split()
        if len(mots) >= 3:
            prefix = " ".join(mots[:3])
            if len(prefix) >= 10 and prefix in text_nz:
                return (c["lettre"], c["titre"])
        # 4. Match partiel : 3 premiers mots du texte (après la lettre) dans le titre
        m = re.match(r"^[a-g]\s+(.{10,})", text_nz)
        if m:
            debut = m.group(1)
            mots_debut = debut.split()[:3]
            if len(mots_debut) >= 3:
                prefix_debut = " ".join(mots_debut)
                if titre_nz.startswith(prefix_debut):
                    return (c["lettre"], c["titre"])
    return None


def split_segments(line, min_gap=5):
    """Découpe une ligne en segments séparés par >= min_gap espaces."""
    segments = []
    current = ""
    spaces = 0
    for c in line:
        if c == " ":
            spaces += 1
        else:
            if spaces >= min_gap and current:
                segments.append(current.strip())
                current = ""
            elif spaces > 0 and current:
                current += " "
            spaces = 0
            current += c
    if current.strip():
        segments.append(current.strip())
    return segments

def parse_theme_pdf(pdf_path, theme_n):
    """Parse un PDF de thème et retourne les données structurées."""
    import pdfplumber

    theme_data = {
        "n": theme_n,
        "titre": THEMES[theme_n - 1]["titre"],
        "pages": THEMES[theme_n - 1]["pages"],
        "conteneurs": [],
        "sections_directes": [],
    }

    # 1. Créer TOUS les conteneurs (forcés)
    conteneurs_map = {}
    for c in CONTAINERS[theme_n]:
        conteneur = {
            "etiquette": c["lettre"],
            "titre": c["titre"],
            "page": None,
            "sections": [],
        }
        conteneurs_map[c["lettre"]] = conteneur

    current_conteneur = conteneurs_map[CONTAINERS[theme_n][0]["lettre"]]  # A par défaut
    current_section = None
    pending_question = None
    in_cahier = False

    def flush_question():
        nonlocal pending_question
        if pending_question and current_section is not None:
            current_section["questions"].append(pending_question)
        pending_question = None

    def flush_section():
        nonlocal current_section
        flush_question()
        current_section = None

    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages, start=1):
            text = page.extract_text(layout=True) or ""
            if not text.strip():
                continue

            text_nz = nz(text)
            page_lines = [normalize_line(l) for l in text.split("\n")]
            page_lines = [l for l in page_lines if l]

            # 1. Détecter les conteneurs présents sur cette page
            for c in CONTAINERS[theme_n]:
                titre_nz = nz(c["titre"])
                if titre_nz in text_nz:
                    if conteneurs_map[c["lettre"]]["page"] is None:
                        conteneurs_map[c["lettre"]]["page"] = page_idx

            # 2. Traiter les lignes
            for line in page_lines:
                segments = split_segments(line, min_gap=5)
                for seg in segments:
                    if not seg:
                        continue

                    # Cahier
                    if RE_CAHIER.match(seg):
                        flush_section()
                        in_cahier = True
                        continue

                    if in_cahier:
                        continue

                    # Conteneur ? (détection par titre)
                    matched = match_container(seg, theme_n)
                    if matched:
                        lettre, titre = matched
                        flush_section()
                        current_conteneur = conteneurs_map[lettre]
                        if current_conteneur["page"] is None:
                            current_conteneur["page"] = page_idx
                        continue

                    # Section
                    m = RE_SECTION.match(seg)
                    if m:
                        flush_section()
                        sec_name = m.group(1).lower().replace(" ", "_")
                        target = current_conteneur["sections"]
                        existing = None
                        for s in target:
                            if s["type"] == sec_name:
                                existing = s
                                break
                        if existing:
                            current_section = existing
                        else:
                            target.append({"type": sec_name, "page": page_idx, "questions": []})
                            current_section = target[-1]
                        continue

                    # Question
                    m = RE_QUESTION.match(seg)
                    if m and current_section is not None:
                        flush_question()
                        n = len(current_section["questions"]) + 1
                        pending_question = {"n": n, "texte": m.group(2).strip()}
                        continue

                    if pending_question is not None:
                        pending_question["texte"] += " " + seg

    flush_question()

    # 3. Ajouter TOUS les conteneurs (même vides)
    for c in CONTAINERS[theme_n]:
        theme_data["conteneurs"].append(conteneurs_map[c["lettre"]])

    return theme_data    
    
def main(themes_dir="themes", out_dir="data"):
    if not os.path.exists(themes_dir):
        print(f"❌ Dossier introuvable : {themes_dir}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(out_dir, exist_ok=True)

    all_themes = []
    total_q = 0
    total_c = 0

    for n in range(1, 13):
        pdf_path = os.path.join(themes_dir, f"T{n}.pdf")
        if not os.path.exists(pdf_path):
            print(f"⚠️ T{n} : PDF introuvable ({pdf_path})")
            continue

        print(f"📖 Parsing T{n}.pdf…")
        theme_data = parse_theme_pdf(pdf_path, n)
        all_themes.append(theme_data)

        nq = sum(len(s["questions"]) for c in theme_data["conteneurs"] for s in c["sections"])
        nc = len(theme_data["conteneurs"])
        attendu = len(CONTAINERS[n])
        total_q += nq
        total_c += nc
        check = "✅" if nc == attendu else f"⚠️ (attendu {attendu})"
        print(f"   T{n:2} : {nc} conteneurs {check}, {nq} questions")

    # Écriture
    manuel = {"themes": all_themes}
    with open(os.path.join(out_dir, "edito-c1.manuel.json"), "w", encoding="utf-8") as f:
        json.dump(manuel, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Écrit : {out_dir}/edito-c1.manuel.json")
    print(f"\n📊 Total : {total_c} conteneurs, {total_q} questions")


if __name__ == "__main__":
    themes_dir = sys.argv[1] if len(sys.argv) > 1 else "themes"
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "data"
    main(themes_dir, out_dir)
