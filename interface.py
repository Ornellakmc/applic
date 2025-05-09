import tkinter as tk
import numpy as np
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
from filtres import (
    filtre_flou_uniforme,
    filtre_niveaux_de_gris,
    filtre_negatif,
    filtre_sepia,
    filtre_contraste,
    filtre_flou_gaussien,
    filtre_detection_bords,
    filtre_fusion
)

photo_originale = None
photo_affichee = None
photo_secondaire = None
historique = []
indice_historique = -1
image_label = None

def afficher_image():
    global image_label, photo_affichee
    if photo_affichee:
        tk_image = ImageTk.PhotoImage(photo_affichee)
        image_label.configure(image=tk_image)
        image_label.image = tk_image
        image_label.update_idletasks()

def appliquer_filtre(filtre):
    global photo_affichee, historique, indice_historique
    if photo_affichee:
        historique = historique[:indice_historique + 1]
        photo_affichee = filtre(photo_affichee.copy())
        historique.append(photo_affichee.copy())
        indice_historique += 1
        afficher_image()

def annuler():
    global indice_historique, photo_affichee
    if indice_historique > 0:
        indice_historique -= 1
        photo_affichee = historique[indice_historique].copy()
        afficher_image()

def retablir():
    global indice_historique, photo_affichee
    if indice_historique < len(historique) - 1:
        indice_historique += 1
        photo_affichee = historique[indice_historique].copy()
        afficher_image()

def sauvegarder_image():
    global photo_affichee
    if photo_affichee:
        chemin = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")])
        if chemin:
            photo_affichee.save(chemin)

def ouvrir_image():
    global photo_originale, photo_affichee, historique, indice_historique
    chemin = filedialog.askopenfilename(title="Choisir une image", filetypes=[("Images", "*.jpg *.png *.jpeg")])
    if chemin:
        photo_originale = Image.open(chemin).convert("RGB")
        photo_affichee = photo_originale.copy()
        historique = [photo_affichee.copy()]
        indice_historique = 0
        afficher_image()

def charger_image_par_defaut():
    global photo_originale, photo_affichee, historique, indice_historique
    chemin = "images/img.jpg"
    if os.path.exists(chemin):
        photo_originale = Image.open(chemin).convert("RGB")
        photo_affichee = photo_originale.copy()
        historique = [photo_affichee.copy()]
        indice_historique = 0
        afficher_image()
    else:
        print("Aucune image par défaut trouvée.")

def charger_une_seconde_image():
    global photo_secondaire
    chemin = filedialog.askopenfilename(title="Choisir une image à fusionner", filetypes=[("Images", "*.jpg *.png *.jpeg")])
    if chemin:
        photo_secondaire = Image.open(chemin).convert("RGB")

def correction_luminosite(valeur):
    global photo_affichee, historique, indice_historique
    if photo_affichee:
        gamma = float(valeur)
        image_np = np.array(photo_affichee).astype(np.float32)
        image_gamma = 255.0 * ((image_np / 255.0) ** (1.0 / gamma if gamma != 0 else 1.0))
        image_gamma = np.clip(image_gamma, 0, 255).astype(np.uint8)
        photo_affichee = Image.fromarray(image_gamma)
        historique = historique[:indice_historique + 1]
        historique.append(photo_affichee.copy())
        indice_historique += 1
        afficher_image()

def correction_contraste(valeur):
    global photo_affichee, historique, indice_historique
    if photo_affichee:
        facteur = float(valeur)
        image_np = np.array(photo_affichee).astype(np.float32)
        moyenne = np.mean(image_np, axis=(0, 1), keepdims=True)
        contraste = moyenne + facteur * (image_np - moyenne)
        contraste = np.clip(contraste, 0, 255).astype(np.uint8)
        photo_affichee = Image.fromarray(contraste)
        historique = historique[:indice_historique + 1]
        historique.append(photo_affichee.copy())
        indice_historique += 1
        afficher_image()

def lancer_interface():
    global image_label, slider_luminosite, slider_contraste

    fenetre = tk.Tk()
    fenetre.title("UVSQolor")
    fenetre.lift()
    fenetre.attributes('-topmost', True)
    fenetre.after(100, lambda: fenetre.attributes('-topmost', False))

    menu = tk.Menu(fenetre)
    fenetre.config(menu=menu)

    fichier_menu = tk.Menu(menu, tearoff=0)
    fichier_menu.add_command(label="Ouvrir", command=ouvrir_image)
    fichier_menu.add_command(label="Sauvegarder", command=sauvegarder_image)
    fichier_menu.add_separator()
    fichier_menu.add_command(label="Quitter", command=fenetre.quit)
    menu.add_cascade(label="Fichier", menu=fichier_menu)

    edition_menu = tk.Menu(menu, tearoff=0)
    edition_menu.add_command(label="Annuler", command=annuler)
    edition_menu.add_command(label="Rétablir", command=retablir)
    menu.add_cascade(label="Édition", menu=edition_menu)

    # Menu Filtres
    filtre_menu = tk.Menu(menu, tearoff=0)
    filtre_menu.add_command(label="Flou uniforme", command=lambda: appliquer_filtre(filtre_flou_uniforme))
    filtre_menu.add_command(label="Niveaux de gris", command=lambda: appliquer_filtre(filtre_niveaux_de_gris))
    filtre_menu.add_command(label="Négatif", command=lambda: appliquer_filtre(filtre_negatif))
    filtre_menu.add_command(label="Sépia", command=lambda: appliquer_filtre(filtre_sepia))
    filtre_menu.add_command(label="Contraste", command=lambda: appliquer_filtre(filtre_contraste))
    filtre_menu.add_command(label="Flou Gaussien", command=lambda: appliquer_filtre(filtre_flou_gaussien))
    filtre_menu.add_command(label="Détection de Bords", command=lambda: appliquer_filtre(filtre_detection_bords))
    filtre_menu.add_command(label="Fusion d'Images", command=lambda: appliquer_filtre(lambda img: filtre_fusion(img, photo_secondaire)))
    filtre_menu.add_command(label="Charger image secondaire", command=charger_une_seconde_image)
    menu.add_cascade(label="Filtres", menu=filtre_menu)


    image_label = tk.Label(fenetre)
    image_label.pack()

    slider_luminosite = tk.Scale(fenetre, from_=0.1, to=3.0, orient=tk.HORIZONTAL, length=200,
                                 resolution=0.1, label="Luminosité", command=correction_luminosite)
    slider_luminosite.set(1.0)
    slider_luminosite.pack(pady=10)

    slider_contraste = tk.Scale(fenetre, from_=-2.0, to=2.0, orient=tk.HORIZONTAL, length=200,
                                resolution=0.1, label="Contraste", command=correction_contraste)
    slider_contraste.set(0)
    slider_contraste.pack(pady=10)

    print("Interface prête.")
    charger_image_par_defaut()

    fenetre.mainloop()
