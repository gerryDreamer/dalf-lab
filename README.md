# DALF Lab

Appli type Duolingo pour préparer le DALF C1/C2 : elle transforme des manuels (PDF, audios, vidéos, transcriptions, corrigés) en exercices interactifs et relie automatiquement les ressources entre elles.

## État actuel
Prototype statique (`index.html`), sans serveur :
- leçons interactives tirées du cahier (thème 1 d'Édito C1), avec XP ;
- lecteur de texte et production écrite (compteur de mots, corrigé du manuel) ;
- import de PDF (pdf.js) : détection des transcriptions, des corrigés et des pistes audio, bilan de ce qui manque ;
- carte des liens entre ressources, avec validation manuelle.

## Lancer
Ouvrir `index.html` dans un navigateur, ou :
`python3 -m http.server 8000` puis http://localhost:8000

## Structure
- `index.html` : le prototype
- `profiles/` : un profil par manuel (règles de détection : fichiers, numérotation des pistes, renvois)

## Modèle de données (cible)
- ressource : id, manuel, source (livre ou cahier), type (texte, audio, vidéo, transcription, corrigé, exercice), page, statut (officiel, ajouté, généré par IA, absent)
- lien : de, vers, méthode (référence explicite, nom de fichier, ordre, sémantique), confiance, validé

## Règles du projet
- Aucun manuel, audio ou vidéo dans le dépôt (voir `.gitignore`) : les fichiers restent sur l'appareil de l'utilisateur.
- Aucune clé d'API dans le code : elle se saisit dans l'appli et reste locale.
- Un corrigé du manuel prime toujours sur un contenu généré par IA, qui reste marqué « à vérifier ».

## Feuille de route
1. Profils par manuel dans l'import (Édito C1, Cosmopolite 5)
2. Sauvegarde locale (IndexedDB) et synchronisation Google Drive
3. Correction IA des productions écrites
4. Débats et jeux de rôle avec l'IA
5. Groupes simulés par l'IA

## Installer l'appli sur le téléphone (PWA)
Ouvrir l'adresse GitHub Pages dans Chrome, puis menu > « Installer l'application » (ou « Ajouter à l'écran d'accueil »). L'appli fonctionne ensuite hors ligne.
À chaque mise à jour, changer la version du cache dans `sw.js` (ligne `const C="dalf-v1"`) pour que les téléphones récupèrent la nouvelle version.

## Profils de manuel
L'onglet Import propose un profil par manuel (dossier `profiles/`) : il fixe la lecture des noms de fichiers audio (livre ou cahier) et affiche ce que le manuel ne contient pas.

## Ajouter des ressources à la main
Onglet Import > « Ajouter à la main » : transcription, corrigé, texte du manuel ou note, rattachés à une leçon (et à une question au choix). Le texte peut être collé ou lu depuis des pages d'un PDF. Dans la leçon, ces ressources s'ouvrent sous la question ; un corrigé n'apparaît qu'après la vérification de la réponse.
