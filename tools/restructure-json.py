import json
from collections import defaultdict

INPUT = "data/edito-c1.structured.json"
OUTPUT = "data/edito-c1.tree.json"

with open(INPUT, encoding="utf-8") as f:
    data = json.load(f)

theme1 = next(t for t in data["themes"] if t["theme"] == 1)

# --- 1. RÉORGANISER LE MANUEL (A, B, C) ---
manuel_actuel = theme1["parties"].get("manuel", {}).get("conteneurs", [])
conteneurs_reorganises = []

for conteneur in manuel_actuel:
    lettre = conteneur.get("lettre", "?")
    sections = conteneur.get("sections", [])
    
    # On regroupe les sections par "type" pour chaque conteneur
    sections_groupees = defaultdict(list)
    for s in sections:
        type_s = s.get("type", "leçon")
        sections_groupees[type_s].append({
            "type": type_s,
            "questions": s.get("questions", []),
            "texte_lecture": s.get("texte_lecture", ""),
            "audio": s.get("audio", ""),
        })
    
    conteneurs_reorganises.append({
        "lettre": lettre,
        "titre": f"Conteneur {lettre}",
        "sections": [
            {"type": t, "questions": qs[0]["questions"] if qs else [], "titre": t.replace("_", " ").capitalize()}
            for t, qs in sections_groupees.items()
        ]
    })

# --- 2. RÉORGANISER LE CAHIER ---
cahier_actuel = theme1["parties"].get("cahier", {}).get("sections", [])
vocab = None
gram = None
abr = None

for s in cahier_actuel:
    if s.get("type") == "vocabulaire":
        vocab = s
    elif s.get("type") == "grammaire":
        gram = s
    elif s.get("type") == "a_batons_rompus":
        abr = s

# --- 2a. Découper les 60 flashcards en 8 niveaux (par catégorie) ---
niveaux_vocab = []
if vocab and vocab.get("flashcards"):
    # Grouper les cartes par catégorie
    groupes = defaultdict(list)
    for card in vocab["flashcards"]:
        cat = card.get("categorie", "Autres")
        groupes[cat].append(card)
    
    # Créer un niveau par catégorie
    for cat, cards in groupes.items():
        niveaux_vocab.append({
            "type": "vocabulaire",
            "titre": cat,
            "flashcards": cards,
        })
    
    print(f"📚 {len(niveaux_vocab)} niveaux de vocabulaire créés :")
    for n in niveaux_vocab:
        print(f"   - {n['titre']} ({len(n['flashcards'])} cartes)")

# --- 2b. Structure du cahier ---
cahier_reorganise = {
    "sections": niveaux_vocab + [
        {"type": "grammaire", "titre": "Grammaire", "questions": gram.get("questions", []) if gram else []},
        {"type": "a_batons_rompus", "titre": "À bâtons rompus", "questions": abr.get("questions", []) if abr else []},
    ]
}

# --- 3. RECONSTRUIRE LE THÈME ---
theme1["parties"] = {
    "manuel": {"conteneurs": conteneurs_reorganises},
    "cahier": cahier_reorganise,
}

# --- 4. SAUVEGARDER ---
with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump({"themes": [theme1]}, f, ensure_ascii=False, indent=2)

print(f"\n✅ Fichier généré : {OUTPUT}")
print(f"   - Manuel : {len(conteneurs_reorganises)} conteneurs")
print(f"   - Cahier : {len(cahier_reorganise['sections'])} sections")
