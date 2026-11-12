# Notes de développement — DALF Lab

## État actuel (12/11/2026)
- **Thème 1 (La Justice)** : Structure 100% complète.
  - Manuel : 3 cartes (A, B, C) avec sections.
  - Cahier : 11 sections (5 niveaux vocab + Grammaire + Comp orale + Comp écrite + Prod orale + À bâtons rompus + Quiz).
  - Total : 60 flashcards + 95 QCM.
- **Fichier de référence** : `data/edito-c1.final-tree.json`.

## 🚨 Problèmes connus (à corriger en priorité)
1. **Flashcards ne s'affichent pas** : les données sont bonnes (60 cartes avec `image_url`), mais `renderFlashcards` ne semble pas se déclencher correctement.
2. **Texte de compréhension écrite ne s'affiche pas** : le `texte_lecture` existe dans le JSON mais n'apparaît pas à l'écran.
3. **Fichiers audio manquants** : les `.mp3` ne sont pas associés aux sections dans l'arbre.

## 🎯 Stratégie
- **Thème 1 = Laboratoire** : On corrige les 3 bugs ci-dessus avant de passer aux autres thèmes.
- **Arbres spécifiques** : chaque thème aura son propre arbre, adapté à son contenu.
- **Pipeline par thème** : on applique `finalize-cahier.py` + `fetch_images.py` + `merge-trees.py` thème par thème.

## Prochains thèmes (dans l'ordre)
1. Thème 2 : SOS démocratie
2. Thème 3 : ...

# Notes de développement — DALF Lab

## Stratégie actuelle (Décision du 12/11/2026)
- **Thème 1 = Laboratoire** : On perfectionne le Thème 1 à 100% avant de passer aux autres.
- **Arbres spécifiques** : Chaque thème aura son propre arbre, adapté à son contenu (certains n'auront pas les mêmes sections).
- **Pipeline par thème** : On applique le pipeline (`finalize-cahier.py` + `fetch_images.py` + `merge-trees.py`) thème par thème, en adaptant les scripts si nécessaire.

## État du Thème 1 (en cours de perfectionnement)
- [x] Manuel A, B, C reconstruit.
- [x] Cahier : 8 niveaux de vocabulaire + Grammaire + À bâtons rompus.
- [x] Images Pixabay pour le vocabulaire (54/60).
- [ ] Compréhension orale (film + équithérapie) : à remplir avec les vraies questions.
- [ ] Compréhension écrite (justice restaurative) : à remplir avec les vraies questions.
- [ ] Production orale (débat) : à tester.
- [ ] Quiz de révision : à générer.
- [ ] Grammaire : à générer les 5 QCM.

## Prochains thèmes (dans l'ordre)
1. Thème 2 : SOS démocratie
2. Thème 3 : ...
(etc.)
