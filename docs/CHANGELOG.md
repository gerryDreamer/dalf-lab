## [0.6.0] — 2026-11-12 — `feat: Arbre complet Thème 1 + sections IA + minuteur oral`

### Ajouté
- **Arbre complet du Thème 1** (`data/edito-c1.final-tree.json`) : 
  - Manuel divisé en 3 cartes (Conteneur A, B, C).
  - Cahier divisé en 11 sections : 5 niveaux de vocabulaire + Grammaire + Compréhension orale + Compréhension écrite + Production orale + À bâtons rompus + Quiz de révision.
- **Moteur `renderProductionOrale`** : Écran dédié avec minuteur interactif (bouton Démarrer / Pause / Reprendre).
- **Scripts de fusion IA** :
  - `tools/ai-gemini-tree.py` : Analyse le PDF T1.pdf avec Gemini pour proposer un arbre.
  - `tools/ai-groq-tree.py` : Analyse le PDF T1.pdf avec Groq pour proposer un arbre alternatif.
  - `tools/merge-trees.py` : Fusionne les propositions Gemini/Groq avec notre structure.
  - `tools/fill-cahier-v2.py` : Génère les QCM manquants (Grammaire, Compréhension orale, Compréhension écrite, Quiz de révision).
  - `tools/recover-abr.py` : Récupère les 10 QCM de "À bâtons rompus" depuis `edito-c1.theme1.json`.
  - `tools/restore-images.py` : Réinjecte les images Pixabay dans les flashcards.
  - `tools/fix-grammaire.py` : Génère l'échauffement et la règle de grammaire.
  - `tools/fix-comp-ecrite.py` : Génère le texte de compréhension écrite.
  - `tools/ai-fix-tree.py` : Répare automatiquement les sections vides.

### Modifié
- **`app.js`** :
  - `startLesson` : Routeur défensif (détecte `flashcards` avant le type, `toLowerCase().trim()` pour éviter les erreurs de casse).
  - `renderQuestion` : Affiche `texte_lecture` dès qu'il existe (plus besoin de `type === "comprehension_ecrite"`).
  - `showHome` : Icônes complètes pour les nouveaux types (🎧, 📖, 🗣️, 🏆).
  - `completeLesson` : Ajout de `production_orale` dans les sections non-QCM.
- **`data/edito-c1.final-tree.json`** : Fichier de référence pour l'UI (100 éléments interactifs).

### Résultat
- **Thème 1 complet** : 60 flashcards (avec images) + 5 QCM Grammaire + 5 QCM Compréhension orale + 5 QCM Compréhension écrite + 10 QCM À bâtons rompus + 10 QCM Quiz de révision = **95 QCM + 60 flashcards**.

### 🚧 TODO (Prochaine session)
- [ ] **Corriger l'affichage des flashcards** (données OK dans le JSON, problème dans `renderFlashcards`).
- [ ] **Corriger l'affichage du texte de compréhension écrite** (données OK, problème dans `renderQuestion`).
- [ ] **Ajouter les fichiers audio** dans l'arbre (associer les `.mp3` aux sections de compréhension orale).
- [ ] **Tester le minuteur de production orale**.
- [ ] **Passer au Thème 2** avec le pipeline validé.

# Changelog — DALF Lab

Toutes les évolutions notables de ce projet sont documentées dans ce fichier.
Le format suit une chronologie basée sur l'historique Git (branches `main` et `dev`).

---

## 🏛️ Phase 1 : Les Fondations (Branche `main`)

Cette phase correspond au prototype initial, à la mise en place de la PWA et à l'extraction manuelle des premières ressources.

### [0.1.0] - Commit `02addd5` — `commit initial`
- Création du dépôt et des premiers fichiers de base.

### [0.1.1] - Commit `1158b1e` — `PWA (installation, hors ligne) et profils de manuel`
- Mise en place du Manifest et du Service Worker (`sw.js`).
- Création des premiers profils de manuels (Édito C1, Cosmopolite 5).

### [0.1.2] - Commit `74a1b85` — `Import : détection plus tolérante et diagnostic`
- Ajout d'une fonction d'import de fichiers plus robuste.

### [0.1.3] - Commit `fd3bd45` — `Import : reconstitution des lignes`
- Amélioration du parser pour reconstituer les lignes à partir des morceaux de texte extraits.

### [0.1.4] - Commit `6e3edc4` — `Ajout de ressources à la main`
- Ajout manuel de transcriptions, corrigés et textes par étape.

### [0.1.5] - Commit `1201684` — `Ajout d'une option IA pour générer du contenu`
- Première intégration de l'IA (Gemini) pour générer du contenu d'après les sujets du livre.

### [0.2.0] - Commit `99a47fb` — `refactor: découpage index.html en app.js/app.css`
- **Refactoring majeur** : Le fichier monolithique `index.html` est découpé en `app.js`, `app.css` et un dossier `data/`.
- Amélioration de la robustesse (`esc()`, `nz()`, garde-fous).

### Merge - Commit `edcfb99` — `Merge pull request #1 from gerryDreamer/dev`
- Première fusion de la branche `dev` dans `main`. Le prototype est officiellement stable.

---

## 🚀 Phase 2 : L'Industrialisation (Branche `dev`)

Cette phase correspond à la création du pipeline de données complet (PDF, TXT, IA) et à la reconstruction des 12 thèmes.

### [0.3.0] - Commit `046d744` — `feat(tools): extraction PDF fiable`
- Intégration de `pdfplumber` pour une extraction fiable du PDF.

### [0.3.1] - Commit `7e9c31f` — `feat(tools): rattachement des ressources aux 12 thèmes`
- Les transcriptions et corrigés sont désormais rattachés aux bons thèmes.

### [0.3.2] - Commits `d53cfec`, `3d3d4d7`, `06be258` — `Parser TXT Édito C1 (v4 à v7)`
- Création de `label-txt.py` pour parser les fichiers TXT.
- Version 7 : **34 transcriptions** et **48 corrigés** (100% de réussite).

### [0.3.3] - Commit `4190061` — `feat(tools): gen-lecons.py`
- Création du script `gen-lecons.py` qui génère un squelette de `lecons.json` à partir du manuel.

### [0.4.0] - Commit `38cc48b` — `docs: mise à jour complète`
- Mise à jour du `README.md`, `ARCHITECTURE.md`, `PIPELINE.md` et `CHANGELOG.md`.

### [0.4.1] - Commit `19e5979` — `chore: gitignore les outils archivés`
- Nettoyage du dépôt en ignorant les anciens scripts et les fichiers `.old`.

### [0.4.2] - Commit `1157060` — `feat(tools): parser PDF par thème`
- Découpage du parser pour traiter les **12 thèmes** individuellement (**53 conteneurs**, **337 questions** extraites).

### [0.4.3] - Commit `8243827` — `docs: mise à jour de l'architecture`
- Documentation de la refonte UI "Duolingo" et du pipeline IA.

### [0.4.4] - Commit `3286cc3` — `chore: ajout de l'atelier et scripts de comparaison`
- Ajout de l'atelier de test HTML et des scripts de comparaison de sources.

### [0.4.5] - Commit `5b24f2f` — `feat(data): 12 thèmes reconstruits par l'IA`
- L'IA (Gemini) reconstruit les 12 thèmes et fusionne tout dans `final.json`.

---

## 🎨 Phase 3 : L'Expérience Utilisateur (Branche `dev`, session actuelle)

Cette phase marque la refonte totale de l'interface (style Duolingo) et le sauvetage du contenu du Cahier via l'IA.

### [0.5.0] - Commit `ce270ac` — `feat: Cahier Thème 1 restructuré + refonte UI Duolingo`

**Ajouté :**
- **Refonte de l'UI (`app.css`)** : Arbre de compétences avec des bulles rondes alternées (effet serpent) et une ligne de progression verticale.
- **Nouveaux moteurs (`app.js`)** :
  - `renderGrammaire` : Parcours en 3 étapes (Échauffement → Règle → Entraînement).
  - `renderProductionEcrite` : Éditeur de texte avec sauvegarde locale (`localStorage`).
  - `renderFlashcards` : Gestion des images, animation de flip 3D.
- **Moteur "À bâtons rompus"** : Nouveau type de section pour les QCM classiques.
- **Scripts d'enrichissement IA** :
  - `structurer-cahier.py`, `finalize-cahier.py` : Reconstruction du Cahier (60 flashcards, 10 QCM) avec Groq (`openai/gpt-oss-120b`).
  - `fetch_images.py` : Téléchargement automatique des images via l'API Pixabay.
- **Nouvelles données** : `data/edito-c1.structured.json` (54 flashcards avec images + 10 QCM).

**Modifié :**
- `app.js` : Ajout de `escapeHtml`, `loadData` pointe vers `structured.json`, `startLesson` route vers le bon moteur.

**Corrigé :**
- Erreur `Cannot read properties of undefined (reading 'split')` (ajout de garde-fous).
- Bug d'affichage des flashcards (face "verso" restaurée).
- Modèle IA obsolète remplacé par `openai/gpt-oss-120b`.

### [0.5.1] - Commit `9b6b824` — `chore: ignore les fichiers de sauvegarde d'éditeur (*~)`
- Ajout de `*~` au `.gitignore` pour ne pas polluer le dépôt.

---

## 🗺️ Prochaines Étapes (Feuille de Route)
- [ ] Générer les QCM de la section **Grammaire** du Thème 1 (actuellement vide).
- [ ] Appliquer le pipeline `finalize-cahier.py` aux **Thèmes 2 à 12**.
- [ ] Corriger les sections sans `type` dans les Thèmes 2, 4, 6, 8, 9, 10.
- [ ] Implémenter un minuteur pour la **Production Orale**.
- [ ] (Long terme) Migration vers une architecture Backend en **Rust (Axum + Tauri)**.

## [0.5.0] — 2026-11-10 — `feat: Cahier interactif + Arbre Duolingo`

### Ajouté
- **Refonte de l'UI (`app.css`)** : Les sections sont désormais affichées sous forme d'un chemin vertical "serpentin" avec des bulles rondes (style Duolingo).
- **Nouveaux moteurs de leçon (`app.js`)** :
  - `renderGrammaire` : Parcours en 3 étapes (Échauffement → Règle → Entraînement).
  - `renderProductionEcrite` : Éditeur de texte avec sauvegarde locale (`localStorage`).
  - `renderFlashcards` : Gestion des images, bouton "Carte suivante", animation de flip.
- **Moteur "À bâtons rompus"** : Nouveau type de section pour les QCM classiques.
- **Scripts d'enrichissement** :
  - `tools/structurer-cahier.py` : Utilise Groq (Llama 3 / GPT-OSS 120B) pour restructurer le Cahier.
  - `tools/finalize-cahier.py` : Extrait le vocabulaire exact (60 flashcards) et les 10 QCM du livre à partir du texte brut.
- **Images des flashcards** : `tools/fetch_images.py` télécharge les images depuis Pixabay pour chaque mot du vocabulaire.

### Modifié
- **`data/edito-c1.structured.json`** : Nouveau fichier de données de référence pour l'UI. Contient le Thème 1 avec 54 flashcards (images incluses) et 10 QCM.
- **`app.js`** : 
  - `escapeHtml` sécurise l'affichage des textes.
  - `loadData` charge `structured.json`.
  - `startLesson` route vers le bon moteur (`vocabulaire`, `grammaire`, `production_ecrite`, `a_batons_rompus`).

### Corrigé
- **Erreur "Cannot read properties of undefined (reading 'split')"** : Ajout de garde-fous (`section.type || "leçon"`) pour les sections sans type.
- **Bug d'affichage des flashcards** : Restauration de la face "verso" (retournement 3D).
- **Modèle IA obsolète** : Remplacement de `llama3-70b-8192` par `openai/gpt-oss-120b`.

### TODO (Prochaines étapes)
- [ ] Générer les QCM de la section Grammaire (Thème 1).
- [ ] Ajouter les sections "À bâtons rompus" pour les Thèmes 2 à 12.
- [ ] Implémenter un minuteur pour la Production Orale.
- [ ] Ajouter un écran de révision (réviser uniquement les cartes ratées).
- [ ] Corriger les sections sans `type` dans les Thèmes 2, 4, 6, 8, 9, 10.
---

## 📄 3. `docs/CHANGELOG.md`

```markdown
# Changelog — DALF Lab

## [0.4.0] — 2025-11-07 — `feat: pipeline TXT`

### Ajouté
- `tools/label-txt.py` (v8) : parser TXT Édito C1
  - Découpe par pages (`--------`)
  - Détecte 34 transcriptions + 48 corrigés (100%)
  - Détecte conteneurs A-G, sections, 475 questions
  - Whitelist conteneurs, filtre pages vides, fusion conteneurs
- `tools/gen-lecons.py` : génère `data/edito-c1.lecons.json`
  - 12 thèmes, 23 conteneurs, 134 sections, 475 questions
  - IDs uniques (`T1-A-comp_audio-q1`)
  - QCM vides (`"qcm": []`)
- `data/edito-c1.manuel.json` : contenu structuré
- `data/edito-c1.ressources.json` : 34 trans + 48 corr
- `data/edito-c1.lecons.json` : squelette
- `docs/PIPELINE.md` : pipeline TXT (remplace PDF)

### Modifié
- `README.md` : vue d'ensemble TXT
- `docs/ARCHITECTURE.md` : pipeline TXT
- `sw.js` : `dalf-v6` → `dalf-v7` (si applicable)

### Archivé
- `tools/label.py` (PDF, v4)
- `tools/extract.py` (PDF, v4)
- `tools/poc.mjs`, `tools/debug-theme.py`, `tools/test-layout.py`

### TODO
- Améliorer détection conteneurs collés (`B Vers un horizon...`)
- Dédupliquer les questions par texte
- Atelier d'étiquetage manuel

---

## [0.3.0] — 2025-11-05 — `docs: documentation complète`

### Ajouté
- `docs/ARCHITECTURE.md`, `docs/CHANGELOG.md`, `docs/PIPELINE.md`
- `README.md` réécrit

### Documenté
- 7 tentatives `seg()` → `seg7()` (échecs)
- Bascule PDF → TXT

---

## [0.2.0] — 2025-11-01 — `refactor: découpage + robustesse`

### Modifié
- `index.html` → `app.js` + `app.css` + `data/`
- `sw.js` : `dalf-v5` → `dalf-v6`

### Corrigé
- `esc()` échappe `"` et `'`
- `nz()` gère `œ`/`æ`/`ß`
- Garde-fou Gemini, AbortController, etc.

---

## [0.1.0] — 2025-10-31 — `feat: prototype initial`

### Ajouté
- Prototype monolithique
- Manifest, Service Worker
- Profils Édito C1, Cosmopolite 5
- 4 leçons, lecteur, écriture, liens, import PDF, IA
