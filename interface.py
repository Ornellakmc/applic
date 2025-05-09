import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

# Variables globales
fichier_image = None
image_tkinter = None
zone_image = None
donnees_image = None
image_active = None
image_fusion = None

# --- AFFICHAGE ---
def mettre_a_jour():
    global image_tkinter, image_active
    image_tkinter = ImageTk.PhotoImage(Image.fromarray(image_active))
    zone_image.delete('all')
    zone_image.create_image(0, 0, anchor=tk.NW, image=image_tkinter)
    zone_image.config(width=image_tkinter.width(), height=image_tkinter.height())
    fenetre.update_idletasks()

# --- INTERFACE ---
def ouvrir_fichier():
    global fichier_image, donnees_image, image_active
    chemin = filedialog.askopenfilename(title='Choisir une image')
    if chemin:
        fichier_image = chemin
        img = Image.open(fichier_image)
        donnees_image = np.array(img)
        image_active = donnees_image.copy()
        # Activer les filtres après avoir ouvert une image
        from filtres import activer_filtres
        activer_filtres()

fenetre = tk.Tk()
fenetre.title("UVSQolor")

zone_image = tk.Canvas(fenetre)
zone_image.pack()

menu_general = tk.Menu(fenetre)
fenetre.config(menu=menu_general)

menu_fichier = tk.Menu(menu_general, tearoff=0)
menu_general.add_cascade(label="Fichier", menu=menu_fichier)
menu_fichier.add_command(label="Choisir une image", command=ouvrir_fichier)

effets_menu = tk.Menu(menu_general, tearoff=0)
menu_general.add_cascade(label="Filtres", menu=effets_menu)

fenetre.mainloop()
