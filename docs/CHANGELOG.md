# Changelog — DALF Lab

Toutes les évolutions notables du projet. Format inspiré de
[Keep a Changelog](https://keepachangelog.com/fr/1.1.0/).
Versionnage : [SemVer](https://semver.org/lang/fr/).

---

## [Non publié] — branche `dev`

### À venir
- Pipeline d'extraction PDF (choix `pdfplumber` vs Atelier)
- `data/cosmopolite-5.lecons.json`
- `PFS` chargé en `await` au boot
- Remplacement des `onclick` inline par `addEventListener`
- Nettoyage `oldapp.js`, `oldindex.html`, `app.js.casse`

---

## [0.3.0] — 2025-11-07 — `docs: documentation complète`

### Ajouté
- `docs/ARCHITECTURE.md` : vue d'ensemble, structure, modèle de données,
  pipeline PDF, sécurité, conventions, points ouverts.
- `docs/CHANGELOG.md` : ce fichier.
- `docs/PIPELINE.md` : documentation dédiée à l'extraction PDF.
- `README.md` réécrit : présentation, lancement, structure, roadmap.

### Documenté
- Les 7 tentatives de reconstruction des colonnes (`seg` → `seg7`)
  et leurs échecs, pour éviter de refaire les mêmes erreurs.
- La décision de basculer vers `pdfplumber` (option B) ou un Atelier
  d'étiquetage manuel (`tools/atelier.html`).

---

## [0.2.0] — 2025-11-05 — `refactor: découpage + robustesse`

### Modifié
- `index.html` : réduit à une coquille HTML (~30 lignes).
- `app.js` : logique extraite, 3 sections commentées, pont
  `window.App` pour les `onclick` inline.
- `app.css` : styles extraits.
- `sw.js` : `dalf-v5` → `dalf-v6`, ajout `app.css`, `app.js`,
  `data/edito-c1.lecons.json` au cache.

### Ajouté
- `data/edito-c1.lecons.json` : données du manuel Édito C1
  (leçons, liens, tâches, connecteurs, sujets IA).
- `tools/poc.mjs` : preuve de concept d'extraction PDF (Node).
- `.gitignore` : `old.sw.js`, `python-server.txt`, `*.casse`,
  `*.cassé`, `tools/out/`.

### Corrigé (revue de code)
- `esc()` échappe désormais `"` et `'` (XSS stocké).
- `nz()` gère `œ`, `æ`, `ß` (correction FR).
- Garde-fou Gemini si `candidates[0]` absent.
- `AbortController` 60 s sur `ai()`.
- `asv()` refuse « Autre » sans URL/modèle.
- `S.gen` / `S.res` protégés contre les non-tableaux
  (migration `localStorage`).
- `index.html` : retrait de l'attribut `integrity` (hash invalide
  bloquait `pdf.min.js`).
- Enregistrement du Service Worker dans `app.js` (manquait).

### Supprimé
- `oldapp.js`, `oldindex.html`, `app.js.casse`, `old.sw.js`,
  `python-server.txt` (sauvegardes locales, non versionnées).

---

## [0.1.0] — 2025-10-31 — `feat: prototype initial`

### Ajouté
- `index.html` : prototype monolithique (~233 lignes denses).
- `manifest.json` : manifest PWA.
- `sw.js` : Service Worker `dalf-v1` → `dalf-v5`.
- `icon-192.png`, `icon-512.png` : icônes PWA.
- `profiles/edito-c1.json` : règles de détection Édito C1.
- `profiles/cosmopolite-5.json` : règles de détection Cosmopolite 5.
- 4 leçons interactives sur le thème 1 d'Édito C1
  (vocabulaire, procès pénal, voix passive, participes passés).
- Lecteur de texte avec surlignage.
- Production écrite (résumé, essai) avec compteur de mots et
  détection de connecteurs.
- Carte des liens entre ressources (validation manuelle).
- Import PDF (`pdf.js`) : détection des transcriptions, corrigés,
  pistes audio, diagnostic des fichiers lus.
- Ajout manuel de ressources (transcription, corrigé, texte, note).
- Études extra avec l'IA (Gemini, Mistral, Groq, OpenRouter,
  DeepSeek, autre compatible OpenAI).
- `.gitignore` : `manuels/`, `audio/`, `video/`, `*.pdf`, `*.mp3`,
  `*.mp4`, `*.wav`, `.env`, `*.key`, `node_modules/`, `.DS_Store`.

---

## Légende des types de commits

| Préfixe | Usage |
|---|---|
| `feat:` | nouvelle fonctionnalité |
| `fix:` | correction de bug |
| `refactor:` | réorganisation sans changement de comportement |
| `docs:` | documentation uniquement |
| `chore:` | tâches diverses (`.gitignore`, dépendances…) |
| `perf:` | amélioration de performance |
| `test:` | ajout ou correction de tests |
