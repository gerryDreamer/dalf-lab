
---

## 📄 2. `docs/ARCHITECTURE.md`

```markdown
# Architecture — DALF Lab

Documentation technique du projet. Dernière mise à jour : 2025-11-07.

## 1. Vue d'ensemble

DALF Lab est une **PWA statique** (pas de backend) qui transforme des
manuels DALF en exercices interactifs. Elle est servie par GitHub Pages
et fonctionne **hors ligne** grâce à un Service Worker.

### Principes directeurs

1. **Aucun contenu protégé dans le dépôt** — les manuels restent sur
   l'appareil de l'utilisateur (`text-edito.txt` est gitignored).
2. **Aucune clé API dans le code** — saisie dans l'appli, stockée en
   `localStorage`.
3. **Le corrigé du manuel prime sur l'IA** — un contenu généré est
   toujours marqué « à vérifier ».
4. **Offline-first** — le Service Worker cache tous les assets.

### Stack

| Couche | Techno | Version |
|---|---|---|
| UI | HTML/CSS/JS vanilla (modules ES) | — |
| Lecture PDF (navigateur) | pdf.js (CDN) | 3.11.174 |
| PWA | Service Worker + Manifest | — |
| IA (optionnelle) | API compatible OpenAI | — |
| Pipeline TXT | Python 3 | — |

---

## 2. Structure des fichiers

### Application web

- **`index.html`** : coquille (~30 lignes)
- **`app.js`** : logique (~600 lignes, 3 sections)
- **`app.css`** : styles (~200 lignes)
- **`sw.js`** : Service Worker (`dalf-v7`)

### Données

- **`data/edito-c1.manuel.json`** : contenu structuré du manuel
  (12 thèmes, conteneurs, sections, 329 questions brutes)
- **`data/edito-c1.ressources.json`** : 34 transcriptions + 48 corrigés
- **`data/edito-c1.lecons.json`** : squelette prêt pour l'atelier
  (12 thèmes, 475 questions, QCM vides)

### Pipeline TXT

- **`tools/label-txt.py`** (v8) : parse `text-edito.txt` → 2 JSON
- **`tools/gen-lecons.py`** : génère le squelette `lecons.json`
- **`tools/label.py`** et **`tools/extract.py`** : pipeline PDF (archivé)

### Documentation

- **`docs/ARCHITECTURE.md`** : ce fichier
- **`docs/CHANGELOG.md`** : historique
- **`docs/PIPELINE.md`** : pipeline d'extraction TXT

---

## 3. Pipeline TXT (actif)

### Entrée

`text-edito.txt` : contenu intégral du manuel en texte, avec :
- Pages séparées par `--------` (10+ tirets)
- Pied de page `NNN I mot` (ex. `198 I cent quatre-vingt-dix-huit`)
- Conteneurs `A`, `B`, `C`… (isolés ou collés au titre)
- Sections `Compréhension audiovisuelle`, etc.
- Questions `1  Quel est...`
- Transcriptions `Page 14, C – Titre`
- Corrigés `Page 17, Vocabulaire`

### Étapes

1. **`tools/label-txt.py`** :
   - Découpe par pages
   - Détecte `page_n` (pied de page, `n` sans `-1`)
   - Détecte les zones (transcriptions p.198–221, corrigés p.222–237)
   - Détecte les thèmes (p.11–22 pour T1, etc.)
   - Détecte les conteneurs (whitelist A-G)
   - Détecte les sections et les questions
   - Sortie : `manuel.json` + `ressources.json`

2. **`tools/gen-lecons.py`** :
   - Lit les 2 JSON
   - Rattache les ressources aux thèmes
   - Génère les 12 leçons avec conteneurs, sections, questions
   - Chaque question a un `id` unique (ex. `T1-A-comp_audio-q1`)
   - QCM vides (`"qcm": []`)
   - Sortie : `lecons.json`

### Sorties

- `manuel.json` : ~330 questions, ~36 conteneurs, ~150 sections
- `ressources.json` : 34 transcriptions, 48 corrigés
- `lecons.json` : squelette prêt pour l'atelier

### État actuel

| Élément | Attendu | Obtenu | Verdict |
|---|---|---|---|
| Transcriptions | 34 | 34 | ✅ 100% |
| Corrigés | 48 | 48 | ✅ 100% |
| Questions | ~329 | 475 | ⚠️ doublons |
| Conteneurs | ~36 | 23 | ⚠️ manquants |

**À corriger** : détection des conteneurs collés au titre (`B Vers un horizon...`), dédup par texte dans `gen-lecons.py`.

---

## 4. Modèle de données

### `manuel.json`

```json
{
  "themes": [
    {
      "n": 1,
      "titre": "Justice, quelles alternatives ?",
      "pages": [11, 22],
      "conteneurs": [
        {
          "etiquette": "A",
          "titre": "Je verrai toujours vos visages",
          "page": 12,
          "sections": [
            {
              "type": "compréhension_audiovisuelle",
              "page": 12,
              "questions": [
                {"n": 1, "texte": "Quel est le thème du film ?"},
                ...
              ]
            }
          ]
        }
      ],
      "sections_directes": []
    }
  ]
}

## 5. Le Pipeline de Reconstruction du Cahier (IA)

Le Cahier du manuel (Vocabulaire, Grammaire, Compréhension) a été extrait de manière incomplète par le parser PDF initial. Pour corriger cela, nous avons mis en place un pipeline de reconstruction assisté par IA :

### Étape 1 : Extraction par Gemini
- Le fichier `data/edito-c1.theme1.json` a été généré par Gemini. Il sert de base (notamment pour les images Pixabay déjà récupérées).

### Étape 2 : Restructuration par Groq (`tools/finalize-cahier.py`)
- On donne le texte brut du livre (capture d'écran retranscrite) à l'IA (`openai/gpt-oss-120b`).
- L'IA extrait **tous** les mots du lexique (ex: "Le greffier", "L'escroquerie") et rédige une définition pour chacun.
- L'IA génère aussi les **10 QCM** de la page vocabulaire.

### Étape 3 : Enrichissement Visuel (`tools/fetch_images.py`)
- Le script parcourt les flashcards et interroge l'API Pixabay pour chaque mot.
- Il associe l'URL de l'image (`image_url`) à la flashcard correspondante.
- Les cartes sans résultat (ex: "le prévenu") restent simplement sans image.

### Résultat
Le fichier `data/edito-c1.structured.json` est la **source de vérité** pour le Thème 1. Il contient la structure exacte attendue par l'interface.
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
