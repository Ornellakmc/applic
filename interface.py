import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
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

# Variables globales
photo_originale = None
photo_affichee = None
photo_secondaire = None
historique = []
indice_historique = -1
image_label = None
slider_luminosite = None
slider_contraste = None

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
        photo_affichee = filtre(historique[indice_historique].copy())
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

def revenir_au_point_de_depart():
    global photo_affichee, historique, indice_historique, slider_luminosite, slider_contraste
    if photo_originale:
        photo_affichee = photo_originale.copy()
        historique = [photo_affichee.copy()]
        indice_historique = 0
        # Réinitialiser les sliders
        slider_luminosite.set(0)
        slider_contraste.set(0)
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
    global photo_affichee
    gamma = float(valeur)
    
    if gamma == 0:
        # Ne rien faire si gamma est égal à zéro
        return
    
    image_np = np.array(photo_affichee).astype(np.float32)
    # Appliquer la correction gamma sur chaque canal, en évitant la division par zéro
    image_gamma = np.power(np.clip(image_np / 255.0, 1e-10, 1), gamma) * 255.0
    image_gamma = np.clip(image_gamma, 0, 255).astype(np.uint8)
    photo_affichee = Image.fromarray(image_gamma)
    afficher_image()


def correction_contraste(valeur):
    global photo_affichee
    facteur = float(valeur)
    image_np = np.array(photo_affichee).astype(np.float32)
    moyenne = np.mean(image_np, axis=(0, 1), keepdims=True)
    contraste = moyenne + facteur * (image_np - moyenne)
    contraste = np.clip(contraste, 0, 255).astype(np.uint8)
    photo_affichee = Image.fromarray(contraste)
    afficher_image()

def lancer_interface():
    global image_label, slider_luminosite, slider_contraste

    fenetre = tk.Tk()
    fenetre.title("UVSQolor")
    fenetre.lift()
    fenetre.attributes('-topmost', True)
    fenetre.after(100, lambda: fenetre.attributes('-topmost', False))

    # Menu principal
    menu = tk.Menu(fenetre)
    fenetre.config(menu=menu)

    # Menu Fichier
    fichier_menu = tk.Menu(menu, tearoff=0)
    fichier_menu.add_command(label="Ouvrir", command=ouvrir_image)
    fichier_menu.add_command(label="Sauvegarder", command=sauvegarder_image)
    fichier_menu.add_separator()
    fichier_menu.add_command(label="Quitter", command=fenetre.quit)
    menu.add_cascade(label="Fichier", menu=fichier_menu)

    # Menu Édition
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
    filtre_menu.add_command(label="Fusion d'Images", command=filtre_fusion)
    menu.add_cascade(label="Filtres", menu=filtre_menu)

    # Zone d'affichage de l'image
    image_label = tk.Label(fenetre)
    image_label.pack()

    # Ajouter un label pour Luminosité
    label_luminosite = tk.Label(fenetre, text="Luminosité")
    label_luminosite.pack()

    # Slider Luminosité - plage réduite
    slider_luminosite = tk.Scale(fenetre, from_=-0.5, to=0.5, orient=tk.HORIZONTAL, length=200,
                                 resolution=0.01, command=correction_luminosite)
    slider_luminosite.set(0)  # Valeur neutre
    slider_luminosite.pack(pady=5)  # Réduire l'espace entre les éléments

    # Ajouter un label pour Contraste
    label_contraste = tk.Label(fenetre, text="Contraste")
    label_contraste.pack()

    # Slider Contraste - plage réduite
    slider_contraste = tk.Scale(fenetre, from_=-0.5, to=0.5, orient=tk.HORIZONTAL, length=200,
                                resolution=0.01, command=correction_contraste)
    slider_contraste.set(0)  # Valeur neutre
    slider_contraste.pack(pady=5)  # Réduire l'espace entre les éléments

    # Bouton Retour au début
    bouton_retour = tk.Button(fenetre, text="Retour au début", command=revenir_au_debut)
    bouton_retour.pack(pady=10)  # Ajouter le bouton en dessous des sliders

    # Bouton pour charger la première image
    bouton_charger_premiere_image = tk.Button(fenetre, text="Charger la première image", command=ouvrir_image)
    bouton_charger_premiere_image.pack(pady=10)  # Ajouter ce bouton avant de fusionner les images

    # Bouton pour charger une seconde image
    bouton_charger_second_image = tk.Button(fenetre, text="Charger une seconde image", command=charger_une_seconde_image)
    bouton_charger_second_image.pack(pady=10)  # Ajouter ce bouton avant de fusionner les images

    print("Interface prête.")
    charger_image_par_defaut()

    fenetre.mainloop()

def correction_luminosite(valeur):
    global photo_affichee
    gamma = float(valeur)
    image_np = np.array(photo_originale).astype(np.float32)
    max_value = float(np.iinfo(image_np.dtype).max)
    facteur_gamma = gamma
    image_gamma = np.power(image_np / 255.0, facteur_gamma) * 255.0
    image_gamma = np.clip(image_gamma, 0, 255).astype(np.uint8)
    photo_affichee = Image.fromarray(image_gamma)
    afficher_image()

def correction_contraste(valeur):
    global photo_affichee
    facteur = float(valeur)
    image_np = np.array(photo_originale).astype(np.float32)
    moyenne = np.mean(image_np, axis=(0, 1), keepdims=True)
    contraste = moyenne + facteur * (image_np - moyenne)
    contraste = np.clip(contraste, 0, 255).astype(np.uint8)
    photo_affichee = Image.fromarray(contraste)
    afficher_image()
