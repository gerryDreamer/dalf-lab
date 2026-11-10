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

with open("data/edito-c1.theme1.json", encoding="utf-8") as f:
    gemini = json.load(f)
flashcards_gemini = gemini["parties"]["cahier"]["sections"][0].get("flashcards", [])
images = {}
for card in flashcards_gemini:
    if card.get("image_url"):
        mot = card.get("recto", "").replace("Le/la ", "").replace("L'", "").split("(")[0].strip()
        if mot: images[mot] = card["image_url"]

print("🧠 L'IA extrait TOUT le vocabulaire de la page...")

prompt = """
Tu es un professeur de français expert en DALF C1. 
Voici le texte EXACT d'une page de vocabulaire du livre Édito C1 (Thème 1 : La Justice).

--- EXTRAIT ---
Lexique : 
- Les acteurs : l'administration pénitentiaire, l'auteur, le criminel(le), la défense, le délinquant(e), la maltraitance, la victime, l'autorité judiciaire, le complice, la cour d'appel, le juge d'application des peines, le détenu, l'enquêteur, les services de police, la garde des Sceaux, le greffier, le juge, les jurés, le magistrat du parquet, le procureur, le ministère public, l'avocat, le prévenu, la protection judiciaire de la jeunesse.
- Les faits : attaquer, un attentat, le blanchiment d'argent, braquer, la corruption, enfreindre, l'enlèvement, l'escroquerie, être impliqué(e) dans une affaire, l'évasion fiscale, la fraude, le meurtre avec préméditation, le passible, la violence conjugale, le vol.
- Les lieux : le cabinet d'avocats, la cellule, la cour d'appel, l'établissement pénitentiaire, la maison d'arrêt, le palais de justice, la salle d'audience, le tribunal administratif.
- La procédure pénale : accorder, un arrangement de peine, délibérer, déposer, juger, un procès, être acquitté(e), être condamné(e).
- Les effets : accéder à la restauration, l'apaisement, comprendre la répercussion, entreprendre une démarche thérapeutique, la médiation, prévenir la récidive.
--- FIN EXTRAIT ---

Ta mission : Génère un maximum de flashcards (Recto = le mot, Verso = une définition courte et claire que tu rédiges, Categorie = le nom du groupe). 
Ne t'arrête pas à 8, extrais TOUS les mots listés ci-dessus.

Format de sortie attendu : Un objet JSON strict.
{
  "vocabulaire": [{"recto": "Le greffier", "verso": "Assiste le magistrat et dresse les procès-verbaux.", "categorie": "Les acteurs"}]
}
"""

try:
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="openai/gpt-oss-120b",
        temperature=0.1,
        max_completion_tokens=4000
    )
    result_text = response.choices[0].message.content.strip()
    if result_text.startswith("```json"): result_text = result_text[7:-3].strip()
    elif result_text.startswith("```"): result_text = result_text[3:-3].strip()
    
    contenu = json.loads(result_text)
    
    # On réinjecte les images existantes (si Pixabay les a trouvées)
    for card in contenu["vocabulaire"]:
        mot = card["recto"].replace("Le/la ", "").replace("L'", "").split("(")[0].strip()
        if mot in images:
            card["image_url"] = images[mot]

    # On reconstruit le fichier final
    gemini["parties"]["cahier"]["sections"] = [
        {"type": "vocabulaire", "titre": "Vocabulaire", "flashcards": contenu["vocabulaire"]},
        {"type": "grammaire", "titre": "Grammaire", "questions": []},
        # On garde les 10 questions de l'étape précédente si elles existent
        {"type": "a_batons_rompus", "titre": "À bâtons rompus", "questions": gemini["parties"]["cahier"]["sections"][2].get("questions", []) if len(gemini["parties"]["cahier"]["sections"]) > 2 else []}
    ]

    with open("data/edito-c1.structured.json", "w", encoding="utf-8") as f:
        json.dump({"themes": [gemini]}, f, ensure_ascii=False, indent=2)
        
    print("✅ Succès !")
    print(f"   - Vocabulaire : {len(contenu['vocabulaire'])} flashcards générées.")

except Exception as e:
    print(f"❌ Erreur IA : {e}")
