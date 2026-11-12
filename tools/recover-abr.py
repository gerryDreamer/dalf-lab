import json

# 1. On charge notre arbre actuel
with open("data/edito-c1.final-tree.json", encoding="utf-8") as f:
    data = json.load(f)

# 2. On charge le fichier de Gemini (qui a les 10 questions du livre)
with open("data/edito-c1.theme1.json", encoding="utf-8") as f:
    gemini_data = json.load(f)

# 3. On cherche les questions de "À bâtons rompus" dans tous les fichiers possibles
questions_trouvees = []

# On fouille dans gemini_data
for section in gemini_data.get("parties", {}).get("cahier", {}).get("sections", []):
    if section.get("type") == "a_batons_rompus" and section.get("questions"):
        questions_trouvees = section["questions"]
        print(f"✅ {len(questions_trouvees)} questions trouvées dans edito-c1.theme1.json")
        break

# Si on n'a rien trouvé, on cherche dans le manuel
if not questions_trouvees:
    for conteneur in gemini_data.get("parties", {}).get("manuel", {}).get("conteneurs", []):
        for section in conteneur.get("sections", []):
            for q in section.get("questions", []):
                if isinstance(q, dict) and q.get("texte"):
                    questions_trouvees.append(q)
    if questions_trouvees:
        print(f"✅ {len(questions_trouvees)} questions trouvées dans le manuel de edito-c1.theme1.json")
        questions_trouvees = questions_trouvees[:10]  # On garde les 10 premières

# 4. On injecte dans la section "a_batons_rompus" de notre arbre
theme1 = data["themes"][0]
for section in theme1["parties"]["cahier"]["sections"]:
    if section.get("type") == "a_batons_rompus":
        section["questions"] = questions_trouvees
        print(f"✅ {len(questions_trouvees)} questions injectées dans 'À bâtons rompus'")
        break

# 5. Sauvegarde
with open("data/edito-c1.final-tree.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n=== BILAN FINAL ===")
for s in theme1["parties"]["cahier"]["sections"]:
    t = s.get("type")
    nb = len(s.get("questions", s.get("flashcards", [])))
    print(f"  - [{t}] {nb} éléments")
