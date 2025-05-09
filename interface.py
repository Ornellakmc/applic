import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from filtres import (
    filtre_flou_uniforme,
    filtre_flou_gaussien,
    filtre_niveaux_de_gris,
    filtre_negatif,
    filtre_sepia,
    filtre_contraste,
    filtre_detection_bords,
    filtre_fusion,
    filtre_gamma
)
import os

# Variables globales
photo_originale = None
photo_affichee = None
historique = []
indice_historique = -1
image_label = None
dialogue_effet = None

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

# --- Gamma UI ---
def ouvrir_dialogue_gamma():
    global dialogue_effet
    if not photo_originale:
        return

    dialogue_effet = tk.Toplevel()
    dialogue_effet.title("Luminosité (Gamma)")
    dialogue_effet.geometry("300x150")
    dialogue_effet.grab_set()

    slider = tk.Scale(dialogue_effet, from_=0.1, to=3.0,
                      orient=tk.HORIZONTAL, length=200,
                      resolution=0.1, digits=2,
                      command=correction_gamma)
    slider.set(1.0)
    slider.pack(pady=20)

    frame_boutons = tk.Frame(dialogue_effet)
    frame_boutons.pack(side=tk.BOTTOM, pady=10)

    bouton_appliquer = tk.Button(frame_boutons, text="Appliquer", command=applique_effet)
    bouton_appliquer.pack(side=tk.LEFT, padx=10)

    bouton_annuler = tk.Button(frame_boutons, text="Annuler", command=annule_effet)
    bouton_annuler.pack(side=tk.LEFT, padx=10)

def correction_gamma(valeur):
    global photo_affichee, photo_originale
    gamma = float(valeur)
    photo_affichee = filtre_gamma(photo_originale, gamma)
    afficher_image()

def applique_effet():
    global photo_originale, photo_affichee, dialogue_effet, historique, indice_historique
    photo_originale = photo_affichee.copy()
    historique.append(photo_affichee.copy())
    indice_historique += 1
    dialogue_effet.destroy()

def annule_effet():
    global photo_affichee, photo_originale, dialogue_effet
    photo_affichee = photo_originale.copy()
    afficher_image()
    dialogue_effet.destroy()

# --- Fusion ---
def appliquer_fusion():
    global photo_affichee, historique, indice_historique

    chemin = filedialog.askopenfilename(title="Choisir une deuxième image", filetypes=[("Images", "*.jpg *.png *.jpeg")])
    if not chemin:
        return

    image2 = Image.open(chemin).convert("RGB").resize(photo_affichee.size)
    fusion = filtre_fusion(photo_affichee, image2)
    historique = historique[:indice_historique + 1]
    photo_affichee = fusion
    historique.append(photo_affichee.copy())
    indice_historique += 1
    afficher_image()

# --- Interface principale ---
def lancer_interface():
    global image_label

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
    filtre_menu.add_command(label="Flou gaussien", command=lambda: appliquer_filtre(filtre_flou_gaussien))
    filtre_menu.add_command(label="Niveaux de gris", command=lambda: appliquer_filtre(filtre_niveaux_de_gris))
    filtre_menu.add_command(label="Négatif", command=lambda: appliquer_filtre(filtre_negatif))
    filtre_menu.add_command(label="Sépia", command=lambda: appliquer_filtre(filtre_sepia))
    filtre_menu.add_command(label="Contraste", command=lambda: appliquer_filtre(filtre_contraste))
    filtre_menu.add_command(label="Détection de bords", command=lambda: appliquer_filtre(filtre_detection_bords))
    filtre_menu.add_command(label="Luminosité (Gamma)", command=ouvrir_dialogue_gamma)
    filtre_menu.add_command(label="Fusion d’images", command=appliquer_fusion)
    menu.add_cascade(label="Filtres", menu=filtre_menu)

    # Zone d'affichage
    image_label = tk.Label(fenetre)
    image_label.pack()

    print("Interface prête.")
    charger_image_par_defaut()

    fenetre.mainloop()
