# filtres.py
import numpy as np
from PIL import Image
from scipy.signal import convolve2d
from scipy.ndimage import gaussian_filter

def filtre_flou_uniforme(image):
    matrice = np.array(image).astype(np.float32)
    noyau = np.ones((5, 5)) / 25
    resultats = []
    for canal in range(3):
        canal_filtre = convolve2d(matrice[:, :, canal], noyau, mode='same', boundary='symm')
        canal_filtre = np.clip(canal_filtre, 0, 255)
        resultats.append(canal_filtre)
    image_filtrée = np.stack(resultats, axis=2).astype(np.uint8)
    return Image.fromarray(image_filtrée)

def filtre_flou_gaussien(image, sigma=1):
    image_np = np.array(image).astype(np.float32)
    floue = gaussian_filter(image_np, sigma=(sigma, sigma, 0))
    return Image.fromarray(np.clip(floue, 0, 255).astype(np.uint8))

def filtre_detection_bords(image):
    image_np = np.array(image.convert("L"))  # convert to grayscale
    sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
    gx = convolve2d(image_np, sobel_x, mode='same', boundary='symm')
    gy = convolve2d(image_np, sobel_y, mode='same', boundary='symm')
    g = np.sqrt(gx**2 + gy**2)
    g = np.clip(g, 0, 255).astype(np.uint8)
    return Image.fromarray(np.stack((g,)*3, axis=-1))

def filtre_niveaux_de_gris(image):
    image_np = np.array(image)
    gris = np.dot(image_np[..., :3], [0.299, 0.587, 0.114])
    gris = gris.astype(np.uint8)
    return Image.fromarray(np.stack((gris,)*3, axis=-1))

def filtre_negatif(image):
    image_np = np.array(image)
    negatif = 255 - image_np
    return Image.fromarray(negatif)

def filtre_sepia(image):
    image_np = np.array(image)
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

def filtre_fusion(image1, image2, alpha=0.5):
    np1 = np.array(image1).astype(np.float32)
    np2 = np.array(image2.resize(image1.size)).astype(np.float32)
    fusion = alpha * np1 + (1 - alpha) * np2
    return Image.fromarray(np.clip(fusion, 0, 255).astype(np.uint8))

def filtre_gamma(image, gamma):
    image_np = np.array(image).astype(np.float32)
    max_value = float(np.iinfo(image_np.dtype).max)
    image_np = image_np / max_value
    image_np = np.power(image_np, gamma)
    image_np = np.clip(image_np * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(image_np)