import numpy as np 
from scipy.signal import convolve2d # convolution image noyau
from scipy.ndimage import gaussian_filter, sobel #floute limage, soccupe des bords
from PIL import Image 

def filtre_flou_uniforme(image):
    matrice = np.array(image).astype(np.float32)
    noyau = np.ones((5, 5)) / 25     # Crée un noyau (matrice) 5x5 rempli de 1/25 pour faire la moyenne des pixels voisins
    resultats = []
    for canal in range(3): #ajt le filtre sur les 3 canaux RGB
        # Convolution entre le canal et le noyau (filtrage spatial)
        canal_filtré = convolve2d(matrice[:, :, canal], noyau, mode='same', boundary='symm')
        canal_filtré = np.clip(canal_filtré, 0, 255) #valeur entre 0 et 255
        resultats.append(canal_filtré) #ajt du canal flouté
    image_filtrée = np.stack(resultats, axis=2).astype(np.uint8) #recompose en une imange les 3 canaux filtrés 
    return Image.fromarray(image_filtrée)

def filtre_niveaux_de_gris(image):
    image_np = np.array(image)
    gris = np.dot(image_np[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8) #Transforme chaque pixel en gris en tenant compte de l’importance de chaque couleur. moyenne ponderer vrb
    return Image.fromarray(np.stack((gris,) * 3, axis=-1)) # # On copie le gris dans les 3 couleurs

def filtre_negatif(image):
    image_np = np.array(image)
    negatif = 255 - image_np # inversion de la couleur
    return Image.fromarray(negatif)

def filtre_sepia(image):
    image_np = np.array(image).astype(np.float32)
    tr = 0.393 * image_np[..., 0] + 0.769 * image_np[..., 1] + 0.189 * image_np[..., 2] #rouge modifié
    tg = 0.349 * image_np[..., 0] + 0.686 * image_np[..., 1] + 0.168 * image_np[..., 2] #vert modifié
    tb = 0.272 * image_np[..., 0] + 0.534 * image_np[..., 1] + 0.131 * image_np[..., 2] #bleu modifié
    sepia = np.stack([tr, tg, tb], axis=-1) # recompose les 3 couleurs 
    sepia = np.clip(sepia, 0, 255).astype(np.uint8) # limitation des valeurs et transformation en image 
    return Image.fromarray(sepia)

def filtre_contraste(image, facteur=1.5):
    image_np = np.array(image).astype(np.float32)
    moyenne = np.mean(image_np, axis=(0, 1), keepdims=True) # camcul couleur moyenne
    contraste = moyenne + facteur * (image_np - moyenne) #ecarte les couleurs de la moyenne
    contraste = np.clip(contraste, 0, 255).astype(np.uint8) #lim les val
    return Image.fromarray(contraste)

def filtre_flou_gaussien(image, sigma=1):
    image_np = np.array(image)
    result = np.zeros_like(image_np) # prepare image vide de meme taille
    for i in range(3):  # Pour chaque couleur RGB
        result[..., i] = gaussian_filter(image_np[..., i], sigma=sigma) #application du flou doux sigma determine niveau flou
    return Image.fromarray(result)

def filtre_vert(image):
    # Transforme l’image en gardant seulement la composante verte
    image_np = np.array(image)
    image_np[:, :, 0] = 0  # On supprime le rouge
    image_np[:, :, 2] = 0  # On supprime le bleu
    return Image.fromarray(image_np)

def filtre_detection_bords(image):
    image_np = np.array(image)
    result = np.zeros_like(image_np) #prepare image vide meme taille
    for i in range(3): #pour chaque couleur
        grad_x = sobel(image_np[..., i], axis=0, mode='nearest') #changemnt vertical traite pixel de bords
        grad_y = sobel(image_np[..., i], axis=1, mode='nearest') #changemnt horizontal
        magnitude = np.hypot(grad_x, grad_y) #force du changement total (bords)
        result[..., i] = np.clip(magnitude, 0, 255) #lim 0 255
    return Image.fromarray(result.astype(np.uint8))

def filtre_fusion(image1, image2=None, alpha=0.5):
    if image2 is None:
        raise ValueError("Aucune image secondaire fournie pour la fusion.") #arrete si ya pas de 2e image 
    image1_np = np.array(image1) #1ete image en tab
    image2_np = np.array(image2) #idem image 2
    if image1_np.shape != image2_np.shape:
        raise ValueError("Les deux images doivent avoir la même taille.") #verif des tailles
    fusion = (alpha * image1_np + (1 - alpha) * image2_np).astype(np.uint8) #melange des 2 images controle intensite alpha
    return Image.fromarray(fusion)
