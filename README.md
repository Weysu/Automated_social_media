# Youtube to TikTok Clip Generator

Ce projet automatise le téléchargement d'une vidéo YouTube, la transcription audio, le génération de sous-titres, la découpure intelligente par phrase, et l'édition finale avec une vidéo de fond (ex: "satisfying.mp4") pour produire des clips TikTok prêts à publier.

## 🚀 Fonctionnalités principales

Téléchargement automatique d'une vidéo YouTube tendance

Transcription audio avec Whisper

Génération de sous-titres au format SRT

Découpage automatique de la vidéo selon les fins de phrases toutes les ~1min (ou plus)

Ajout de sous-titres incrustés personnalisables (police, taille, couleur, alignement)

Fusion de clips avec une vidéo de fond

Sortie des clips édités avec sous-titres dans output/video_sub/

## ⚖️ Structure du projet

<pre> ``` . ├── main.py # Script principal 
  ├── subtitle.py # Transcription & génération des sous-titres 
  ├── video_downloader.py # Téléchargement de vidéo YouTube 
  ├── video_editor.py # Fusion des vidéos et découpage 
  ├── assets/ 
  │ └── satisfying.mp4 # Vidéo secondaire utilisée en fond 
  ├── output/ │ ├── video/ # Vidéos découpées et éditées 
  │ ├── video_sub/ # Vidéos avec sous-titres incrustés 
  │ └── script/ # Fichiers SRT et transcriptions ``` </pre>

## 🚧 Prérequis

Python 3.9+

FFmpeg installé et accessible depuis le terminal

Bibliothèques Python :

pip install moviepy openai-whisper

## ⚡ Utilisation

python main.py

Les clips générés avec sous-titres seront sauvegardés dans :

output/video_sub/final_video_X_with_subs.mp4

## 📆 Exemple de personnalisation des sous-titres

Modifiez les options dans add_subtitles_to_video() ou dans le main:

FONT_SIZE=20,
Coulour='00FFFF00',     # Jaune
BorderStyle=3,          # Boite opaque
ALIGN='5',              # Centrer verticalement
MARGIN_V=0,             # Hauteur depuis le bas (0 = milieu si ALIGN=5)

## ✅ Fait:
- Génération de sous titre basique
- Récupération autonome de vidéo
- Montage autonome 

## ✍️ To do :
- Fine tunning des sous titre
- Fine tunning des vidéo 
- Récupération de vidéo autres que youtube ( série, ... ) 
- Publication automatiser 
- Vérifier le nettoyage des fichier temp ( audio, script, ... )
  


