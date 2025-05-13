import tkinter as tk #interface graphique
from tkinter import filedialog, messagebox #ouvrir fichier et afficher image 
from PIL import Image, ImageTk #ouvrir et afficher image 
import numpy as np # calcul avec image
import os #verif si un fichier existe 
from filtres import (  #import fonction filtres depuis un autre fichier 
    filtre_flou_uniforme,
    filtre_niveaux_de_gris,
    filtre_negatif,
    filtre_sepia,
    filtre_contraste,
    filtre_flou_gaussien,
    filtre_vert,
    filtre_detection_bords,
    filtre_fusion
    )

# variables globales
photo_originale = None #image dorigine
photo_affichee = None #image actuellement visible 
photo_secondaire = None #2e image pour a fusion 
historique = [] #liste etapes precedentes
indice_historique=-1 #position actuelle dans lhistorique 
image_label=None # zone daffichage de limage
slider_luminosite=None
slider_contraste=None

def afficher_image():
    global image_label, photo_affichee
    if photo_affichee:
        tk_image=ImageTk.PhotoImage(photo_affichee) # conversion affichage tkinter
        image_label.configure(image=tk_image) #met image dans label 
        image_label.image =tk_image #garde une ref pour eviter ler bugs
        image_label.update_idletasks() #force la màj de laffichage 

def appliquer_filtre(filtre):
    global photo_affichee, historique, indice_historique
    if photo_affichee:
        historique=historique[:indice_historique + 1] #supp les étapes faites après un retour en arrière
        photo_affichee=filtre(historique[indice_historique].copy()) #applique filtre sur une copie 
        historique.append(photo_affichee.copy()) #sauvegarde le resultat
        indice_historique += 1 #avance dans lhistorique
        afficher_image()

def appliquer_fusion():
    global photo_affichee, photo_secondaire, historique, indice_historique
    if photo_affichee and photo_secondaire:
        image1 =photo_affichee.copy()
        image2 =photo_secondaire.copy()

        #redimensionner si nécessaire la 2e image
        if image1.size !=image2.size:
            image2 =image2.resize(image1.size)

        resultat =filtre_fusion(image1, image2)  #applique la fusuion 
        photo_affichee=resultat
        historique=historique[:indice_historique + 1]  #supp les étapes faites après un retour en arrière
        historique.append(photo_affichee.copy()) #sauvegarde le resultat 
        indice_historique +=1 
        afficher_image()
    else:
        messagebox.showwarning("Fusion impossible", "Les deux images doivent être chargées.")

def annuler():
    global indice_historique, photo_affichee
    if indice_historique> 0:
        indice_historique-=1 #recule dun cran
        photo_affichee =historique[indice_historique].copy() #remet limage precedente
        afficher_image()

def retablir():
    global indice_historique, photo_affichee
    if indice_historique <len(historique) -1:
        indice_historique+=1 #avance dun cran
        photo_affichee=historique[indice_historique].copy() #remet limage suivante
        afficher_image()

def revenir_au_point_de_depart():
    global photo_affichee, historique, indice_historique, slider_luminosite, slider_contraste
    if photo_originale:
        photo_affichee=photo_originale.copy() # remet photo dorigine 
        historique=[photo_affichee.copy()] #reinitialise lhistorique
        indice_historique=0
        # Réinitialiser les sliders
        slider_luminosite.set(0)
        slider_contraste.set(0)
        afficher_image()

def sauvegarder_image():
    global photo_affichee
if photo_affichee: #si image existe
        # Demande à l'utilisateur où sauvegarder l'image
        chemin=filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")])
        if chemin: #sii l'utilisateur a choisi un emplacement
            photo_affichee.save(chemin)

def ouvrir_image():
    global photo_originale, photo_affichee, historique, indice_historique
    #ouvre une fenêtre dialogue pour choisir une image
    chemin=filedialog.askopenfilename(title="Choisir une image", filetypes=[("Images", "*.jpg *.png *.jpeg")])
    if chemin:#si l'utilisateur a selectionné une image
        photo_originale=Image.open(chemin).convert("RGB") #ouvre liamge +convertit en rgb
        photo_affichee=photo_originale.copy() #image affiché devient image originale
        historique=[photo_affichee.copy()]# initialisation historique avec l'image originale
        indice_historique=0 #revient etape depart
        afficher_image() #màj limage 

def charger_image_par_defaut():
    global photo_originale, photo_affichee, photo_secondaire, historique, indice_historique
    chemin1="images/img.jpg" #chemin 1ere image 
    chemin2="images/img2.jpg" #chemin 2e image
    if os.path.exists(chemin1) and os.path.exists(chemin2): #si les 2 images existent 
        photo_originale =Image.open(chemin1).convert("RGB")#ouvrir 1ere image
        photo_secondaire =Image.open(chemin2).convert("RGB")#ouvrir 2e image
        photo_affichee =photo_originale.copy() #image affiché devient 1ere image 
        historique =[photo_affichee.copy()] #initialise historique avecimage originale 
        indice_historique =0 #revient etape de depart 
        afficher_image()
    else:
        #message erreur si no image
        print("Les images img.jpg et img2.jpg doivent être présentes dans le dossier 'images/'.")


def charger_une_seconde_image():
    global photo_secondaire
    #fenetre pour choisir une image a fusionner
    chemin=filedialog.askopenfilename(title="Choisir une image à fusionner", filetypes=[("Images", "*.jpg *.png *.jpeg")])
    if chemin: #si une image est selectionné
        photo_secondaire=Image.open(chemin).convert("RGB") #ouvre 2e image pour la fusion

def correction_luminosite(valeur):
    global photo_affichee
    gamma= float(valeur) #recup valeur curseur

    if gamma == 0:
        # Ne rien faire si gamma est égal à zéro
        return
    
    image_np = np.array(photo_affichee).astype(np.float32)
    #applique la correction gamma pour la luminosité en évitant la division par zéro
    image_gamma=np.power(np.clip(image_np / 255.0, 1e-10, 1), gamma) * 255.0
    image_gamma=np.clip(image_gamma, 0, 255).astype(np.uint8) #entre 0 et 255
    photo_affichee =Image.fromarray(image_gamma)#revientde numpy a image 
    afficher_image()


def correction_contraste(valeur):
    global photo_affichee
    facteur=float(valeur) #recup valeur curseur
    image_np=np.array(photo_affichee).astype(np.float32)
    # Calcule la moyenne des couleurs de l'image
    moyenne=np.mean(image_np, axis=(0, 1), keepdims=True)
    contraste=moyenne+facteur*(image_np-moyenne)#applique l'ajustement du contraste
    contraste=np.clip(contraste, 0, 255).astype(np.uint8) #0 255
    photo_affichee=Image.fromarray(contraste)#numpy à image
    afficher_image()

#fenetre graphique principale 
def lancer_interface():
    global image_label, slider_luminosite, slider_contraste

    fenetre = tk.Tk() #nouvelle fenetre tkinter
    fenetre.title("UVSQolor") #titre a la fenetre
    fenetre.lift() #fenetre tjr premier plan 
    fenetre.attributes('-topmost', True)#garder la fenêtre en haut pendant 100 ms
    fenetre.after(100, lambda: fenetre.attributes('-topmost', False))  # Après la fenêtre peut passer en arrière-plan

    # menu principal
    menu = tk.Menu(fenetre)
    fenetre.config(menu=menu)

    # menu fichier
    fichier_menu = tk.Menu(menu, tearoff=0)
    fichier_menu.add_command(label="Ouvrir", command=ouvrir_image) #ahr commande ouvrir imahe
    fichier_menu.add_command(label="Sauvegarder", command=sauvegarder_image) #ajt commande sauvegarder image 
    fichier_menu.add_separator()# ajt une separation dans le menu
    fichier_menu.add_command(label="Quitter", command=fenetre.quit) #ajt commande quitter lappli
    menu.add_cascade(label="Fichier", menu=fichier_menu)

    # menu edition
    edition_menu = tk.Menu(menu, tearoff=0)
    edition_menu.add_command(label="Annuler", command=annuler) #cmd annule derniere modif
    edition_menu.add_command(label="Rétablir", command=retablir) #cmd retablir derniere modif annulé
    menu.add_cascade(label="Édition", menu=edition_menu)

    # Menu filtres
    filtre_menu=tk.Menu(menu, tearoff=0)
    filtre_menu.add_command(label="Flou uniforme", command=lambda: appliquer_filtre(filtre_flou_uniforme))
    filtre_menu.add_command(label="Niveaux de gris", command=lambda: appliquer_filtre(filtre_niveaux_de_gris))
    filtre_menu.add_command(label="Négatif", command=lambda: appliquer_filtre(filtre_negatif))
    filtre_menu.add_command(label="Sépia", command=lambda: appliquer_filtre(filtre_sepia))
    filtre_menu.add_command(label="Contraste", command=lambda: appliquer_filtre(filtre_contraste))
    filtre_menu.add_command(label="Flou Gaussien", command=lambda: appliquer_filtre(filtre_flou_gaussien))
    filtre_menu.add_command(label="Filtre Vert", command=lambda: appliquer_filtre(filtre_vert))
    filtre_menu.add_command(label="Détection de Bords", command=lambda: appliquer_filtre(filtre_detection_bords))
    filtre_menu.add_command(label="Fusion d'Images", command=appliquer_fusion)
    menu.add_cascade(label="Filtres", menu=filtre_menu)

    # Zone daffichage de limage
    image_label=tk.Label(fenetre)
    image_label.pack()

    # ajt un label pour Luminosité
    label_luminosite=tk.Label(fenetre, text="Luminosité") #txt curseur luminosité
    label_luminosite.pack()

    # Slider Luminosité - plage réduite
    #curseur luminosté
    slider_luminosite=tk.Scale(fenetre,from_=-0.5,to=0.5,orient=tk.HORIZONTAL,length=200,
                                 resolution=0.01, command=correction_luminosite)
    slider_luminosite.set(0)  # Valeur neutre 0
    slider_luminosite.pack(pady=5)  # Réduire l'espace entre les éléments

    # ajt un label pour Contraste
    label_contraste=tk.Label(fenetre, text="Contraste") #txt curseur contraste
    label_contraste.pack()

    # Slider Contraste plage réduite
    #curseur de contraste
    slider_contraste=tk.Scale(fenetre, from_=-0.5, to=0.5, orient=tk.HORIZONTAL, length=200,
                                resolution=0.01, command=correction_contraste) 
    slider_contraste.set(0)  # Valeur neutre 0
    slider_contraste.pack(pady=5)  # Réduire l'espace entre les éléments

    # Bouton Retour au début
    bouton_retour=tk.Button(fenetre, text="Retour au début", command=revenir_au_point_de_depart)
    bouton_retour.pack(pady=10)  # ajt le bouton en dessous des sliders

    # Bouton pour charger la première image
    bouton_charger_premiere_image=tk.Button(fenetre, text="Charger la première image", command=ouvrir_image)
    bouton_charger_premiere_image.pack(pady=10)  # ajt ce bouton avant de fusionner les images

    # Bouton pour charger une seconde image
    bouton_charger_second_image=tk.Button(fenetre, text="Charger une seconde image", command=charger_une_seconde_image)
    bouton_charger_second_image.pack(pady=10)  # ajt ce bouton avant de fusionner les images

    print("Interface prête.")
    charger_image_par_defaut()# Charge images par défaut pour tester

    fenetre.mainloop()

def correction_luminosite(valeur):
    global photo_affichee, historique,indice_historique
    gamma=float(valeur)# convertit  valeur du curseur texte en nombre décimal float

    if historique: #verif image chargé
        image_np=np.array(historique[indice_historique]).astype(np.float32)
        epsilon=1e-8 #petite valeur pour éviter la division par zéro
        # Correction gamma qui rend l’image plus claire ou plus sombre selon la valeur
        image_gamma=np.power(np.clip(image_np / 255.0, epsilon, 1), gamma) * 255.0
        image_gamma=np.clip(image_gamma, 0, 255).astype(np.uint8) #entre 0 255
        photo_affichee=Image.fromarray(image_gamma)
        afficher_image()

def correction_contraste(valeur):
    global photo_affichee, historique, indice_historique
    facteur=float(valeur)

    if historique:
        image_np=np.array(historique[indice_historique]).astype(np.float32)
        # On calcule la moyenne de l'image (moyenne de chaque canal R, G et B)
        moyenne=np.mean(image_np, axis=(0,1),keepdims=True) #garde les dimensions du tableau après la moyenne.
        # On applique la formule du contraste pour que chaque pixel s’éloigne ou se rapproche de la moyenne selon le facteur
        contraste=moyenne+facteur*(image_np-moyenne)
        contraste=np.clip(contraste, 0,255).astype(np.uint8)
        photo_affichee=Image.fromarray(contraste)
        afficher_image()
