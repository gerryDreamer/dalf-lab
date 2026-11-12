# DALF Lab

Application web (PWA) pour préparer le DALF C1/C2 à partir de manuels
(Édito C1, Cosmopolite 5…). Transforme un manuel en exercices
interactifs, relie automatiquement les ressources (transcriptions,
corrigés) et permet de s'entraîner hors ligne.

## État actuel

**Pipeline d'extraction TXT fonctionnel** ✅

- 12 thèmes structurés (conteneurs, sections, questions)
- 34 transcriptions (audio + vidéo)
- 48 corrigés
- 475 questions brutes (à transformer en QCM)
- Squelette `lecons.json` généré

**Application web** (prototype statique) :
- 4 leçons interactives (QCM + textes à trous) sur Édito C1, thème 1
- Lecteur de texte avec surlignage
- Production écrite avec compteur de mots
- Import PDF (pdf.js) : détection des transcriptions/corrigés
- Études extra avec l'IA (Gemini, Mistral, Groq, OpenRouter, DeepSeek)
- PWA installable, fonctionne hors ligne

## Lancer en local

```bash
cd ~/dalf-lab
python3 -m http.server 8000
# puis http://localhost:8000 dans le navigateur

## État actuel
- ✅ **Extraction** : 12 thèmes, 53 conteneurs, 337 questions extraites.
- ✅ **QCM** : 335 questions enrichies avec 4 choix par l'IA.
- ✅ **Cahier Thème 1** : Restructuré par l'IA (54 flashcards avec images + 10 QCM).
- ✅ **UI** : Arbre de compétences style Duolingo, Moteurs de leçons (Flashcards, Grammaire, Production Écrite, QCM), Flashcard 3D avec images.
- 🚧 **Pipeline** : En cours pour les Thèmes 2 à 12.
# DALF Lab — L'apprentissage du DALF C1 façon Duolingo

DALF Lab transforme vos manuels (Édito C1) en une application interactive. 
Fini les blocs de texte illisibles : l'IA reclassifie le contenu pour créer des QCM, des textes de lecture, et des tâches d'écriture.

## État actuel
- ✅ **Extraction** : 12 thèmes, 53 conteneurs, 337 questions extraites.
- ✅ **QCM** : 335 questions enrichies avec 4 choix par l'IA.
- ✅ **Nettoyage** : Le bruit (titres, pages) a été supprimé.
- 🚧 **UI** : Refonte en cours pour un parcours type "Arbre de compétences".

## Installation (Pour les développeurs)

```bash
git clone https://github.com/gerryDreamer/dalf-lab.git
cd dalf-lab
pip install -r requirements.txt # requests, groq, pdfplumber
