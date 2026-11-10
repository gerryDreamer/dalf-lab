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
