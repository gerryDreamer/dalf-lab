# Architecture — DALF Lab

Dernière mise à jour : Novembre 2026.

## 1. Vue d'ensemble

DALF Lab est une **PWA statique** (pas de backend) conçue pour transformer les manuels DALF (Édito C1) en une expérience d'apprentissage interactive de type "Duolingo".

Le projet s'articule autour de 3 piliers :
1. **Extraction des données** (Pipeline PDF/TXT).
2. **Enrichissement & Reclassification** (Scripts Python + IA).
3. **L'Application Web** (Interface élève).

## 2. Le Pipeline de Données (L'entrepôt)

L'application ne lit pas le PDF. Elle lit des fichiers JSON générés par nos scripts.

### Étape 1 : Extraction (`label-pdf.py`)
- Découpe les 12 thèmes en 12 fichiers PDF (`themes/T1.pdf` à `T12.pdf`).
- Extrait le texte et les questions via `pdfplumber`.
- Associe les conteneurs (A, B, C...) en fonction des titres fournis manuellement.

### Étape 2 : Génération des QCM (`gen-qcm.py`)
- Prend les questions brutes.
- Utilise des LLM (Groq, Gemini) pour générer 4 choix de réponse et identifier la bonne réponse.
- Sauvegarde dans `lecons-auto.json`.

### Étape 3 : Reclassification & Enrichissement (`reclassify.py`)
- **C'est le cerveau du projet.**
- Utilise Gemini pour donner un "type" à chaque question :
  - `qcm` : Question à choix multiple.
  - `texte` : Texte de lecture (Compréhension écrite).
  - `tache_ouverte` : Production écrite/orale (génère des indices).
  - `titre` / `a_supprimer` : Nettoie le bruit (numéros de page, consignes).
- Sauvegarde dans `lecons-v2.json`.

### Étape 4 : Reconstruction Thème par Thème (`reconstruct.py` - À venir)
- Prend le PDF original d'un thème et les données de `lecons-v2.json`.
- Demande à l'IA de reconstruire l'arbre pédagogique exact :
  - Sépare le **Manuel** (textes, audios) du **Cahier** (grammaire, vocabulaire).
  - Associe les audios (`editoc1_piste_XX.mp3`) aux bonnes sections.
  - Structure les activités (Canvas pour la prod écrite, Flashcards pour le vocab).

## 3. L'Interface Utilisateur (L'application)

### Philosophie de l'UI (Style Duolingo)
- **L'Arbre des Unités** : L'élève progresse sur un chemin avec des bulles (T1, T2, etc.).
- **Les Leçons** : Une leçon n'est pas limitée à 10 minutes, mais elle est découpée en **micro-tâches** (5 à 10 questions).
- **Les Formats d'activité** :
  - **Compréhension écrite** : Split-screen (Texte à gauche, Questions à droite).
  - **Compréhension orale/audiovisuelle** : Lecteur audio intégré (fichiers locaux) + QCM.
  - **Production écrite** : Éditeur de texte (Canvas) avec sauvegarde locale.
  - **Vocabulaire** : Flashcards interactives (retournement de carte).
  - **Grammaire** : Enchaînement Échauffement -> Règles -> Entraînement.

## 4. Sécurité et Règles
- **Zéro média dans Git** : Les `.mp3` et `.mp4` restent sur le disque de l'utilisateur.
- **Zéro clé API dans le code** : Toujours dans `.env` (ignoré par Git).
