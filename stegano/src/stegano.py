import argparse
from PIL import Image
import os

def string_to_bits(s):
    """Convertit une chaîne de caractères en une séquence de bits."""
    return ''.join(f'{ord(c):08b}' for c in s)

def bits_to_string(b):
    """Convertit une séquence de bits en une chaîne de caractères."""
    chars = [chr(int(b[i:i+8], 2)) for i in range(0, len(b), 8)]
    return ''.join(chars)

def hide(input_image_path, output_image_path, secret_message):
    """Cache un message secret dans une image."""
    # Ouvrir l'image
    image = Image.open(input_image_path)
    pixels = image.load()
    
    # Convertir le message secret en bits
    secret_bits = string_to_bits(secret_message) + string_to_bits('\x1F')  # Utiliser un caractère de fin unique
    secret_bits_len = len(secret_bits)
    
    # Vérifier que l'image est assez grande pour cacher le message
    width, height = image.size
    if secret_bits_len > 3 * width * height and image.mode != 'RGBA':
        raise ValueError("Le message est trop long pour cette image.")
    if secret_bits_len > 4 * width * height and image.mode == 'RGBA':
        raise ValueError("Le message est trop long pour cette image RGBA.")
    
    bit_index = 0
    for y in range(height):
        for x in range(width):
            # Récupérer le pixel
            pixel = pixels[x, y]
            
            if image.mode == 'RGB':
                r, g, b = pixel
                # Modifier les bits de poids faible avec vérification de l'index
                if bit_index < secret_bits_len:
                    r = (r & 0xFE) | int(secret_bits[bit_index])  # 0xFE est le masque pour garder les 7 premiers bits
                    bit_index += 1
                if bit_index < secret_bits_len:
                    g = (g & 0xFE) | int(secret_bits[bit_index])
                    bit_index += 1
                if bit_index < secret_bits_len:
                    b = (b & 0xFE) | int(secret_bits[bit_index])
                    bit_index += 1
                
                pixels[x, y] = (r, g, b)

            elif image.mode == 'RGBA':
                r, g, b, a = pixel
                # Modifier les bits de poids faible avec vérification de l'index
                if bit_index < secret_bits_len:
                    r = (r & 0xFE) | int(secret_bits[bit_index])
                    bit_index += 1
                if bit_index < secret_bits_len:
                    g = (g & 0xFE) | int(secret_bits[bit_index])
                    bit_index += 1
                if bit_index < secret_bits_len:
                    b = (b & 0xFE) | int(secret_bits[bit_index])
                    bit_index += 1
                if bit_index < secret_bits_len:
                    a = (a & 0xFE) | int(secret_bits[bit_index])  # Si le message est encore en cours de cache
                    bit_index += 1

                pixels[x, y] = (r, g, b, a)
            
            # Si le message est totalement caché, on arrête
            if bit_index >= secret_bits_len:
                image.save(output_image_path)
                return
    
    # Sauvegarder l'image avec le message caché
    image.save(output_image_path)

def reveal(image_path):
    """Révèle un message caché dans une image."""
    # Ouvrir l'image
    image = Image.open(image_path)
    pixels = image.load()
    
    # Extraire les bits cachés
    secret_bits = ""
    width, height = image.size
    for y in range(height):
        for x in range(width):
            # Récupérer le pixel
            pixel = pixels[x, y]
            
            if image.mode == 'RGB':
                r, g, b = pixel
                secret_bits += str(r & 1)  # R: LSB
                secret_bits += str(g & 1)  # G: LSB
                secret_bits += str(b & 1)  # B: LSB

            elif image.mode == 'RGBA':
                r, g, b, a = pixel
                secret_bits += str(r & 1)  # R: LSB
                secret_bits += str(g & 1)  # G: LSB
                secret_bits += str(b & 1)  # B: LSB
                secret_bits += str(a & 1)  # A: LSB (si le canal alpha est présent)
    
    # Trouver la fin du message en recherchant le caractère spécial
    end_marker = string_to_bits('\x1F')  # Le caractère de fin spécial
    end_marker_index = secret_bits.find(end_marker)
    
    # Si la séquence de fin est trouvée, on coupe la séquence de bits à cet endroit
    if end_marker_index != -1:
        secret_bits = secret_bits[:end_marker_index]
    
    # Convertir les bits en texte
    secret_message = bits_to_string(secret_bits)
    
    return secret_message

def main():
    # Chemins relatifs pour les sous-dossiers 'input' et 'output'
    input_dir = os.path.join(os.getcwd(), 'src', 'input')
    output_dir = os.path.join(os.getcwd(), 'src', 'output')
    
    parser = argparse.ArgumentParser(description="Outil de stéganographie pour cacher et révéler des secrets dans des images PNG.")
    subparsers = parser.add_subparsers(dest='command')
    
    # Commande pour cacher un secret
    hide_parser = subparsers.add_parser('hide', help="Cache un message secret dans une image.")
    hide_parser.add_argument('input_image', help=f"Chemin vers l'image d'entrée (PNG) dans le dossier '{input_dir}'.")
    hide_parser.add_argument('output_image', help=f"Chemin vers l'image de sortie (PNG) avec le message caché dans le dossier '{output_dir}'.")
    hide_parser.add_argument('secret_message', help="Le message secret à cacher.")
    
    # Commande pour révéler un secret
    reveal_parser = subparsers.add_parser('reveal', help="Révèle un message caché dans une image.")
    reveal_parser.add_argument('image', help=f"Chemin vers l'image contenant le message caché dans le dossier '{output_dir}'.")
    
    # Analyser les arguments
    args = parser.parse_args()

    if args.command == 'hide':
        # Construire les chemins complets pour l'entrée et la sortie
        input_image_path = os.path.join(input_dir, args.input_image)
        output_image_path = os.path.join(output_dir, args.output_image)
        
        # Cacher un message
        if not os.path.exists(input_image_path):
            print(f"L'image d'entrée {input_image_path} n'existe pas.")
            return
        hide(input_image_path, output_image_path, args.secret_message)
        print(f"Message caché dans {output_image_path}")
    
    elif args.command == 'reveal':
        # Construire le chemin complet pour l'image à révéler
        image_path = os.path.join(output_dir, args.image)
        
        if not os.path.exists(image_path):
            print(f"L'image {image_path} n'existe pas.")
            return
        
        # Révéler un message
        secret_message = reveal(image_path)
        print(f"Message caché : {secret_message}")
    else:
        parser.print_help()

if __name__ == '__main__':
    main()