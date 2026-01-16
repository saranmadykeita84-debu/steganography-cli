# Travail Pratique #3: Stéganographie 

## Auteur
- Nom KEITA, prénom SARAN MADY

## Compatibilité 
Langage – version < Python -- version  3.8 --> 

## Utilisation 
Dans notre programme on a utiliser "visual code" pour réaliser le travail.
Pour pouvoir démarrez notre code il faut ouvrir le terminal dans "visual code" et installer les dépendances avant tout, on tape: pip install cryptography python-dotenv.
puis les dépendances suivant : pip install Pillow

Ensuite quand l'installation est faite essayer de lancer le programme avec: python src/stegano.py  oubien le button debugger.

pour cacher le message en première position il faudra taper la commande:

python src/stegano.py hide image.png image_output.png "Le message secret a caché"

pour révéler le message caché il faudra taper la commande :

python src/stegano reveal image_output.png

après le programme vas affiché le message caché. 

Mais sa s'applique uniquement pour les images png et non jpeg car, avec les jpeg y aura une perte lors de la compression ce qui ne pas fiable . Raison pour la quelle on a utiliser png.
