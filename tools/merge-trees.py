import json

# --- Chargement des fichiers ---
with open("data/edito-c1.tree.json", encoding="utf-8") as f:
    base = json.load(f)

theme1 = base["themes"][0]

# --- 1. On garde les sections existantes du Cahier ---
cahier_actuel = theme1["parties"]["cahier"]["sections"]

# On sépare par type
vocab_niveaux = [s for s in cahier_actuel if s.get("type") == "vocabulaire"]
grammaire = next((s for s in cahier_actuel if s.get("type") == "grammaire"), None)
abr = next((s for s in cahier_actuel if s.get("type") == "a_batons_rompus"), None)

# --- 2. On crée les nouvelles sections manquantes ---
comp_orale = {
    "type": "comprehension_orale",
    "titre": "Compréhension orale - Film & Équithérapie",
    "questions": [] # À remplir plus tard
}

comp_ecrite = {
    "type": "comprehension_ecrite",
    "titre": "Compréhension écrite - Justice restaurative",
    "questions": [] # À remplir plus tard
}

prod_orale = {
    "type": "production_orale",
    "titre": "Production orale - Débat",
    "consigne": "Débattez sur la place de la médiation animale en prison. Argumentez et donnez votre point de vue en 10 minutes.",
    "questions": []
}

quiz_revision = {
    "type": "quiz_revision",
    "titre": "Quiz de révision - Thème 1",
    "questions": [] # À générer avec l'IA plus tard
}

# --- 3. On reconstruit le Cahier dans l'ordre logique ---
nouveau_cahier = {"sections": []}

# D'abord le vocabulaire (les 8 niveaux)
nouveau_cahier["sections"].extend(vocab_niveaux)

# Ensuite la grammaire
if grammaire:
    nouveau_cahier["sections"].append(grammaire)

# Puis les compréhensions et productions
nouveau_cahier["sections"].append(comp_orale)
nouveau_cahier["sections"].append(comp_ecrite)
nouveau_cahier["sections"].append(prod_orale)

# Enfin, "À bâtons rompus" et le quiz
if abr:
    nouveau_cahier["sections"].append(abr)
nouveau_cahier["sections"].append(quiz_revision)

# --- 4. On réinjecte dans le thème ---
theme1["parties"]["cahier"] = nouveau_cahier

# --- 5. Sauvegarde ---
with open("data/edito-c1.final-tree.json", "w", encoding="utf-8") as f:
    json.dump({"themes": [theme1]}, f, ensure_ascii=False, indent=2)

print("✅ Fusion terminée ! Fichier généré : data/edito-c1.final-tree.json")
print(f"\n=== NOUVELLE STRUCTURE DU CAHIER ({len(nouveau_cahier['sections'])} sections) ===")
for s in nouveau_cahier["sections"]:
    t = s.get("type", "?")
    titre = s.get("titre", t)
    nb = len(s.get("questions", s.get("flashcards", [])))
    print(f"  - [{t}] {titre} ({nb} éléments)")
