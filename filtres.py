import numpy as np
from scipy.ndimage import gaussian_filter, sobel
from scipy.signal import convolve2d

# --- EFFETS ---
def effet_juste_vert(donnees_image):
    image_active = donnees_image.copy()
    image_active[:, :, [0, 2]] = 0
    return image_active

def effet_nuance_gris(donnees_image):
    niveaux_gris = (0.2125 * donnees_image[:, :, 0] +
                    0.7154 * donnees_image[:, :, 1] +
                    0.0721 * donnees_image[:, :, 2]).astype(np.uint8)
    image_active = np.stack([niveaux_gris] * 3, axis=-1)
    return image_active

def appliquer_gamma(donnees_image, g_val):
    puissance = 2 ** float(g_val)
    image_temp = (donnees_image / 255.0) ** puissance * 255
    return image_temp.astype(np.uint8)

def ajuster_contraste(donnees_image, force, centre):
    normalisee = donnees_image / 255.0
    sigmo = 1 / (1 + np.exp(-force * (normalisee - centre)))
    return (sigmo * 255).astype(np.uint8)

def ajouter_flou(donnees_image):
    noyau_moyen = np.ones((3, 3)) / 9
    floue = np.zeros_like(donnees_image, dtype=np.float64)
    for i in range(3):
        floue[:, :, i] = convolve2d(donnees_image[:, :, i], noyau_moyen, mode='same', boundary='symm')
    return floue.astype(np.uint8)

def flou_gaussien(donnees_image, sigma=1.0):
    return gaussian_filter(donnees_image, sigma=(sigma, sigma, 0)).astype(np.uint8)

def detection_bords(donnees_image):
    gris = (0.299 * donnees_image[:, :, 0] +
            0.587 * donnees_image[:, :, 1] +
            0.114 * donnees_image[:, :, 2])
    dx = sobel(gris, axis=0)
    dy = sobel(gris, axis=1)
    magnitude = np.hypot(dx, dy)
    magnitude = (magnitude / magnitude.max() * 255).astype(np.uint8)
    return np.stack([magnitude] * 3, axis=-1)

def fusionner_images(donnees_image):
    from tkinter import filedialog
    chemin = filedialog.askopenfilename(title="Choisir une 2ème image pour la fusion")
    if not chemin:
        return donnees_image
    img2 = Image.open(chemin).resize((donnees_image.shape[1], donnees_image.shape[0]))
    image_fusion = np.array(img2)
    alpha = 0.5
    return (donnees_image * alpha + image_fusion * (1 - alpha)).astype(np.uint8)

def ajuster_luminosite(donnees_image, val):
    facteur = float(val)  # Récupère la valeur du slider
    return np.clip(donnees_image * facteur, 0, 255).astype(np.uint8)

# --- Activer les filtres dans le menu ---
def activer_filtres():
    from interface import effets_menu
    effets_menu.add_command(label="Vert uniquement", command=lambda: appliquer_et_mettre_a_jour(effet_juste_vert))
    effets_menu.add_command(label="Nuance de gris", command=lambda: appliquer_et_mettre_a_jour(effet_nuance_gris))
    effets_menu.add_command(label="Correction Gamma", command=lambda: appliquer_gamma_popup())
    effets_menu.add_command(label="Contraste", command=lambda: appliquer_contraste_popup())
    effets_menu.add_command(label="Flou", command=lambda: appliquer_et_mettre_a_jour(ajouter_flou))
    effets_menu.add_command(label="Flou Gaussien", command=lambda: appliquer_flou_gaussien_popup())
    effets_menu.add_command(label="Bords", command=lambda: appliquer_et_mettre_a_jour(detection_bords))
    effets_menu.add_command(label="Fusionner avec image", command=lambda: fusionner_images())
    effets_menu.add_command(label="Luminosité", command=lambda: appliquer_luminosite_popup())

# --- Popups pour différents filtres ---
def appliquer_gamma_popup():
    from interface import fenetre
    fenetre_popup = tk.Toplevel(fenetre)
    fenetre_popup.title("Réglage Gamma")
    tk.Label(fenetre_popup, text="Valeur Gamma").pack(pady=10)
    curseur = tk.Scale(fenetre_popup, from_=0.1, to=3.0, orient=tk.HORIZONTAL, resolution=0.1)
    curseur.set(1.0)
    curseur.pack()

    def appliquer_et_valider():
        from interface import image_active
        image_active = appliquer_gamma(donnees_image, curseur.get())
        mettre_a_jour()
        valider_modif()

    tk.Button(fenetre_popup, text="Valider", command=appliquer_et_valider).pack(side=tk.LEFT, padx=10)
    tk.Button(fenetre_popup, text="Annuler", command=annuler_modif).pack(side=tk.LEFT, padx=10)

def appliquer_contraste_popup():
    from interface import fenetre
    fenetre_popup = tk.Toplevel(fenetre)
    fenetre_popup.title("Réglage Contraste")
    slider_force = tk.Scale(fenetre_popup, from_=0.1, to=20.0, orient=tk.HORIZONTAL, resolution=0.1, label="Force", length=200)
    slider_force.set(10.0)
    slider_force.pack(pady=5)

    slider_centre = tk.Scale(fenetre_popup, from_=0.0, to=1.0, orient=tk.HORIZONTAL, resolution=0.01, label="Centre", length=200)
    slider_centre.set(0.5)
    slider_centre.pack(pady=5)

    def mise_a_jour_contraste(_=None):
        from interface import image_active
        image_active = ajuster_contraste(donnees_image, slider_force.get(), slider_centre.get())
        mettre_a_jour()

    slider_force.config(command=mise_a_jour_contraste)
    slider_centre.config(command=mise_a_jour_contraste)
    tk.Button(fenetre_popup, text="Valider", command=valider_modif).pack(side=tk.LEFT, padx=10)
    tk.Button(fenetre_popup, text="Annuler", command=annuler_modif).pack(side=tk.LEFT, padx=10)

def appliquer_luminosite_popup():
    from interface import fenetre
    fenetre_popup = tk.Toplevel(fenetre)
    fenetre_popup.title("Réglage Luminosité")
    slider_luminosite = tk.Scale(fenetre_popup, from_=0.5, to=2.0, orient=tk.HORIZONTAL, resolution=0.01, label="Luminosité", length=200)
    slider_luminosite.set(1.0)
    slider_luminosite.pack(pady=5)

    def mise_a_jour_luminosite(val):
        from interface import image_active
        image_active = ajuster_luminosite(donnees_image, val)
        mettre_a_jour()

    slider_luminosite.config(command=mise_a_jour_luminosite)
    tk.Button(fenetre_popup, text="Valider", command=valider_modif).pack(side=tk.LEFT, padx=10)
    tk.Button(fenetre_popup, text="Annuler", command=annuler_modif).pack(side=tk.LEFT, padx=10)
