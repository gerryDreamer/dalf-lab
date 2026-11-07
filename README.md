# DALF Lab

Application web (PWA) pour préparer le DALF C1/C2 à partir de manuels
(Édito C1, Cosmopolite 5…). Transforme un PDF de manuel en exercices
interactifs, relie automatiquement les ressources (transcriptions,
corrigés, audios) et permet de s'entraîner hors ligne.

## État actuel

Prototype statique, sans serveur :
- 4 leçons interactives (QCM + textes à trous) sur le thème 1 d'Édito C1
- Lecteur de texte avec surlignage
- Production écrite avec compteur de mots et détection de connecteurs
- Carte des liens entre ressources, avec validation manuelle
- Import de PDF (pdf.js) : détection des transcriptions, corrigés, pistes audio
- Ajout manuel de ressources (transcription, corrigé, texte, note)
- Études extra avec l'IA (Gemini, Mistral, Groq, OpenRouter, DeepSeek, autre)
- PWA installable, fonctionne hors ligne

## Lancer en local

```bash
cd ~/dalf-lab
python3 -m http.server 8000
# puis http://localhost:8000 dans le navigateur
