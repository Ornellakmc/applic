import numpy as np
from scipy.signal import convolve2d
from scipy.ndimage import gaussian_filter, sobel
from PIL import Image

def filtre_flou_uniforme(image):
    matrice = np.array(image).astype(np.float32)
    noyau = np.ones((5, 5)) / 25
    resultats = []
    for canal in range(3):
        canal_filtré = convolve2d(matrice[:, :, canal], noyau, mode='same', boundary='symm')
        canal_filtré = np.clip(canal_filtré, 0, 255)
        resultats.append(canal_filtré)
    image_filtrée = np.stack(resultats, axis=2).astype(np.uint8)
    return Image.fromarray(image_filtrée)

def filtre_niveaux_de_gris(image):
    image_np = np.array(image)
    gris = np.dot(image_np[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
    return Image.fromarray(np.stack((gris,) * 3, axis=-1))

def filtre_negatif(image):
    image_np = np.array(image)
    negatif = 255 - image_np
    return Image.fromarray(negatif)

def filtre_sepia(image):
    image_np = np.array(image).astype(np.float32)
    tr = 0.393 * image_np[..., 0] + 0.769 * image_np[..., 1] + 0.189 * image_np[..., 2]
    tg = 0.349 * image_np[..., 0] + 0.686 * image_np[..., 1] + 0.168 * image_np[..., 2]
    tb = 0.272 * image_np[..., 0] + 0.534 * image_np[..., 1] + 0.131 * image_np[..., 2]
    sepia = np.stack([tr, tg, tb], axis=-1)
    sepia = np.clip(sepia, 0, 255).astype(np.uint8)
    return Image.fromarray(sepia)

def filtre_contraste(image, facteur=1.5):
    image_np = np.array(image).astype(np.float32)
    moyenne = np.mean(image_np, axis=(0, 1), keepdims=True)
    contraste = moyenne + facteur * (image_np - moyenne)
    contraste = np.clip(contraste, 0, 255).astype(np.uint8)
    return Image.fromarray(contraste)

def filtre_flou_gaussien(image, sigma=1):
    image_np = np.array(image)
    result = np.zeros_like(image_np)
    for i in range(3):  # Pour chaque canal RGB
        result[..., i] = gaussian_filter(image_np[..., i], sigma=sigma)
    return Image.fromarray(result)

def filtre_detection_bords(image):
    image_np = np.array(image)
    result = np.zeros_like(image_np)
    for i in range(3):
        grad_x = sobel(image_np[..., i], axis=0, mode='nearest')
        grad_y = sobel(image_np[..., i], axis=1, mode='nearest')
        magnitude = np.hypot(grad_x, grad_y)
        result[..., i] = np.clip(magnitude, 0, 255)
    return Image.fromarray(result.astype(np.uint8))

def filtre_fusion(image1, image2=None, alpha=0.5):
    if image2 is None:
        raise ValueError("Aucune image secondaire fournie pour la fusion.")
    image1_np = np.array(image1)
    image2_np = np.array(image2)
    if image1_np.shape != image2_np.shape:
        raise ValueError("Les deux images doivent avoir la même taille.")
    fusion = (alpha * image1_np + (1 - alpha) * image2_np).astype(np.uint8)
    return Image.fromarray(fusion)
