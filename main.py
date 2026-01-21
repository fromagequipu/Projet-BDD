import sys
import os
import requests
import folium
import sqlite3
import time
from folium.plugins import MarkerCluster
from filters import get_communes_conformites # fonction requête BDD dans fichier filters
from filters import get_communes_dateprel # fonction requête BDD dans fichier filters
from filters import get_molecules #fonction pour récuperer les paramètres
from filters import get_refqual


from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QDateEdit, QGroupBox,
    QButtonGroup, QRadioButton, QCheckBox, QLineEdit, QCompleter
)
from PyQt5.QtCore import QUrl, QDate, Qt, QThread, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QIcon

# Fichier de sauvegarde de la carte
MAP_FILE = "map.html"

# -------------------------
# API INSEE -> ALIMENTATION DE LA TABLE COMMUNE
# -------------------------

# API AVEC CODE POSTAL
"""
def get_coordinates_and_name_from_insee(insee_code):
    url = f"https://api-adresse.data.gouv.fr/search/?q={insee_code}&type=municipality&limit=1"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data["features"]:
            name = data["features"][0]["properties"]["label"]
            lon, lat = data["features"][0]["geometry"]["coordinates"]
            print(f"{insee_code} -> {name}, lat={lat}, lon={lon}")
            return name, lat, lon
    return None, None, None
"""

# API AVEC CODE INSEE => plus besoin pour l'instant car alimenté dans la BDD 1 fois

# def normalize_insee(insee):
#      return str(insee).zfill(5) # format code INSEE = ajout d'un 0 en premier s'il y en a pas

# conn = sqlite3.connect("WaterQuality.db")
# cur = conn.cursor()

# # Sélection des communes qui n'ont pas de coordonnées remplies 
# cur.execute("""
#      SELECT inseecommune
#      FROM Commune
#      WHERE lat IS NULL OR lon IS NULL
#      LIMIT 100
#  """)

# communes = cur.fetchall()

# for (insee,) in communes:
#      print(insee)
#      insee_norm = normalize_insee(insee)
#      # Récupération des coordonnées avec l'API 
#      url = f"https://geo.api.gouv.fr/communes/{insee_norm}?fields=centre"
#      r = requests.get(url)

#      # Mise à jour dans la BDD des coordonnées
#      if r.status_code == 200:
#          data = r.json()
#          if "centre" in data:
#              lon, lat = data["centre"]["coordinates"]
#              cur.execute(
#                  "UPDATE Commune SET lat=?, lon=? WHERE inseecommune=?",
#                  (lat, lon, insee)
#              )

#      time.sleep(0.1)  # respect API

# conn.commit()
# conn.close()

# -------------------------
# Création carte Folium
# -------------------------
 
"""def create_map(insee_code=None):
    m = folium.Map(location=[46.6, 1.8], zoom_start=6)

    if insee_code:
        name, lat, lon = get_coordinates_and_name_from_insee(insee_code)
        if lat and lon:
            folium.Marker(
                location=[lat, lon],
                popup=name,
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(m)
            m.location = [lat, lon]
            m.zoom_start = 10

    m.save(MAP_FILE) """
"""
def create_map(communes):
    m = folium.Map(location=[46.6, 1.8], zoom_start=6)

    for insee, nom, lat, lon in communes:
        if lat is None or lon is None:
            continue

        folium.Marker(
            location=[lat, lon],
            popup=f"{nom} ({insee})"
        ).add_to(m)

    m.save(MAP_FILE)

"""

# Création de la carte
def create_map(communes):
     # Configuration de la carte
     m = folium.Map(location=[46.6, 1.8], zoom_start=6)

     # Création du cluster de marqueurs si beaucoup
     cluster = MarkerCluster().add_to(m)

     for insee, nom, lat, lon in communes:
         if lat is None or lon is None:
             continue

         # On ajoute le marker dans le cluster (selon coordonnées)
         folium.Marker(
             location=[lat, lon],
             popup=f"{nom} ({insee})"
         ).add_to(cluster)

     m.save(MAP_FILE)

def create_map_from_communes(communes):
    m = folium.Map(location=[46.6, 1.8], zoom_start=6)

    if communes:
        for insee, nom, lat, lon in communes:
            if lat and lon:
                folium.Marker(
                    location=[lat, lon],
                    popup=f"{nom} ({insee})",
                    icon=folium.Icon(color="blue", icon="info-sign")
                ).add_to(m)

        # Centrage automatique sur la première commune
        m.location = [communes[0][2], communes[0][3]]
        m.zoom_start = 9

    m.save(MAP_FILE)

# ======================================================
# THREAD POUR LA GÉNÉRATION DE CARTE FLUIDE
# ======================================================

class MapWorker(QThread):
    finished = pyqtSignal()

    def __init__(self, chimique, bacterio, ref_bact, ref_chim, parametre):
        super().__init__()
        self.chimique = chimique
        self.bacterio = bacterio
        self.ref_bact = ref_bact
        self.ref_chim = ref_chim
        self.parametre = parametre

    def run(self):
        # Connexion BDD DANS le thread
        conn = sqlite3.connect("WaterQuality.db")
        cursor = conn.cursor()

        # Appel de la fonction dans filters avec les paramètres récupérés
        communes = get_communes_conformites(
            cursor,
            self.chimique,
            self.bacterio,
            self.ref_bact,
            self.ref_chim
        )

        self.last_communes = communes  
        
        parametres = get_molecules(
            cursor,
            self.parametre
        )
        # Génération de la carte
        create_map(communes)

        cursor.close()
        conn.close()

        self.finished.emit()

# -------------------------
# Fenêtre principale
# -------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.conn = sqlite3.connect("WaterQuality.db")
        self.cursor = self.conn.cursor()

        self.setWindowTitle("Water Quality")
        self.setWindowIcon(QIcon("logo.png"))
        self.resize(1600, 850)

        central = QWidget()
        self.setCentralWidget(central)

        # Layout principal (vertical)
        main_layout = QVBoxLayout(central)

        # Layout titre
        titre_layout = QHBoxLayout()
        main_layout.addLayout(titre_layout)
        
        #Layout choix ville
        ville_layout = QHBoxLayout()
        main_layout.addLayout(ville_layout)
        ville_layout.setAlignment(Qt.AlignCenter)
        boxville = QGroupBox("")
        boxville.setLayout(ville_layout)
        
        self.combo_ville = QComboBox()
        
        
        #Partie à changer pour pouvoir faire dynamiquement
        self.combo_ville.addItem("Sélectionner une ville", None)
        self.combo_ville.addItem("Nantes", "44000")
        self.combo_ville.addItem("Rennes", "35000")
        self.combo_ville.addItem("Saint André des Eaux", "44117")
        
        ville_layout.addWidget(QLabel(""))
        ville_layout.addWidget(self.combo_ville)

        # Layout du haut (3 colonnes)
        top_layout = QHBoxLayout()
        main_layout.addLayout(top_layout)

        # -------------------------
        # TITRE (au centre, en haut)
        # -------------------------
        title_label = QLabel("Bienvenue dans l'interface Water Quality !")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 34px;
            font-weight: bold;
            color: #1f4e79;
            padding: 20px;
        """)

        titre_layout.addWidget(title_label)

        # -------------------------
        # COLONNE 1 - Général
        # -------------------------
        col1_layout = QVBoxLayout()
        box1 = QGroupBox("Date")
        box1.setLayout(col1_layout)
        
        self.button1 = QPushButton("Afficher la carte")
        self.button1.clicked.connect(self.update_map)
        
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        
        col1_layout.addWidget(QLabel(""))
        col1_layout.addWidget(self.date_edit)
        col1_layout.addWidget(QLabel(""))
        col1_layout.addWidget(self.button1)


        # -------------------------
        # COLONNE 2 - Conformité
        # -------------------------
        col2_layout = QVBoxLayout()
        box2 = QGroupBox("Conformité")
        box2.setLayout(col2_layout)

        self.combo_conformite = QButtonGroup()
        self.radio_bacterio = QCheckBox("Conforme")
        self.radio_bacterio1 = QCheckBox("Non conforme")
        self.combo_conformite.addButton(self.radio_bacterio)
        self.combo_conformite.addButton(self.radio_bacterio1)
        statut_layout = QHBoxLayout()
        statut_layout.addWidget(QLabel("Limite Bactériologique"))
        statut_layout.addWidget(self.radio_bacterio)
        statut_layout.addWidget(self.radio_bacterio1)
        col2_layout.addLayout(statut_layout)

        self.combo_categorie = QButtonGroup()
        self.radio_chimie = QCheckBox("Conforme")
        self.radio_chimie1 = QCheckBox("Non conforme")
        statut_layout2 = QHBoxLayout()
        statut_layout2.addWidget(QLabel("Limite Physico-chimique"))
        statut_layout2.addWidget(self.radio_chimie)
        statut_layout2.addWidget(self.radio_chimie1)
        self.combo_categorie.addButton(self.radio_chimie)
        self.combo_categorie.addButton(self.radio_chimie1)
        col2_layout.addLayout(statut_layout2)

        self.combo_refbacteriologique = QButtonGroup()
        self.radio_refbacteriologique = QCheckBox("Conforme")
        self.radio_refbacteriologique1 = QCheckBox("Non conforme")
        statut_layout2 = QHBoxLayout()
        statut_layout2.addWidget(QLabel("Référence Bactériologique"))
        statut_layout2.addWidget(self.radio_refbacteriologique)
        statut_layout2.addWidget(self.radio_refbacteriologique1)
        self.combo_refbacteriologique.addButton(self.radio_refbacteriologique)
        self.combo_refbacteriologique.addButton(self.radio_refbacteriologique1)
        col2_layout.addLayout(statut_layout2)

        self.combo_refchimie = QButtonGroup()
        self.radio_refchimie = QCheckBox("Conforme")
        self.radio_refchimie1 = QCheckBox("Non conforme")
        statut_layout2 = QHBoxLayout()
        statut_layout2.addWidget(QLabel("Référence Physico-chimique"))
        statut_layout2.addWidget(self.radio_refchimie)
        statut_layout2.addWidget(self.radio_refchimie1)
        self.combo_refchimie.addButton(self.radio_refchimie)
        self.combo_refchimie.addButton(self.radio_refchimie1)
        col2_layout.addLayout(statut_layout2)

        # Bouton pour actualiser la carte avec les conformités sélectionnées
        self.btn_actualiser = QPushButton("Afficher la carte")
        col2_layout.addWidget(self.btn_actualiser)
        self.btn_actualiser.clicked.connect(self.update_map_with_conformities)

        # -------------------------
        # COLONNE 3 - Paramètres
        # -------------------------
        col3_layout = QVBoxLayout()
        box3 = QGroupBox("Molécules")
        box3.setLayout(col3_layout)
        box3.setMaximumWidth(650)
        
        # Récupération des molécules depuis la BDD
        parametres = get_molecules(self.cursor)

        # Menu déroulant des molécules
        self.combo_molecule = QComboBox()
        self.combo_molecule.addItem("Sélectionner une molécule")
        self.combo_molecule.addItems(parametres)


        # Zone de texte pour la valeur
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Entrer la valeur souhaitée")

        # ---- AUTOCOMPLÉTION ----
        suggestions = [
            "0.1", "0.2", "0.5", "1", "2", "5", "10",
            "< 0.1", "< 0.5", "> 1", "> 5"
        ]

        #Partie pour le remplissage automatique du champ refqual suivant la molécule choisit
        self.value_input = QLineEdit()
        self.value_input.setReadOnly(True)
        self.value_input.setPlaceholderText("Valeur réglementaire")
        self.combo_molecule.currentTextChanged.connect(self.update_refqual)
        
        completer = QCompleter(suggestions)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)

        self.value_input.setCompleter(completer)
        # -----------------------

        # Bouton
        self.button = QPushButton("Afficher la carte")
        self.button.clicked.connect(self.update_map)

        # Ajout au layout
        col3_layout.addWidget(QLabel("Choisir une molécule :"))
        col3_layout.addWidget(self.combo_molecule)

        col3_layout.addWidget(QLabel("Valeur :"))
        col3_layout.addWidget(self.value_input)

        col3_layout.addStretch()
        col3_layout.addWidget(self.button)



        # Ajout des colonnes
        top_layout.addWidget(box1)
        top_layout.addWidget(box2)
        top_layout.addWidget(box3)

        # -------------------------
        # Carte (pleine largeur en bas)
        # -------------------------

        # Renvoi le nombre de communes affichées
        self.lbl_count = QLabel("Nombre de communes : 0")
        self.lbl_count.setAlignment(Qt.AlignCenter)
        self.lbl_count.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(self.lbl_count)

        self.browser = QWebEngineView()
        main_layout.addWidget(self.browser, stretch=1)

        # Carte initiale
        create_map([])
        self.load_map()

    # ==================================================
    # Fonctions associées
    # ==================================================

    def load_map(self):
        path = os.path.abspath(MAP_FILE)
        self.browser.load(QUrl.fromLocalFile(path))
        
    def update_refqual(self, parametre):
        if parametre == "Sélectionner une molécule":
            self.value_input.clear()
            return
        refqual = get_refqual(self.cursor, parametre)
        self.value_input.setText(refqual)
        

    def update_map(self):
        insee_code = self.combo_ville.currentData()
        create_map([])
        # Récupération de la date choisie
        date_str = self.date_edit.date().toString("dd-MM-yyyy")

        # Appel BDD → communes EST DÉFINI ICI
        communes = get_communes_dateprel(self.cursor, date_str)

        # Sécurité si la requête retourne None
        if communes is None:
            communes = []

        # Création de la carte AVEC cluster (comme conformité)
        create_map(communes)

        # Mise à jour du compteur
        self.lbl_count.setText(f"Nombre de communes : {len(communes)}")

        # Recharge la carte dans le navigateur
        self.load_map()

    def get_radio_value(self, radio_c, radio_nc):
        # Récupération des valeurs cochées selon C ou N 
        values = []
        if radio_c.isChecked():
            values.append("C")
        if radio_nc.isChecked():
            values.append("N")
        return values  

    # Actualisation de la carte selon filtre 2 
    def update_map_with_conformities(self):

        # Récupération de la valeur cochée
        chimique = self.get_radio_value(self.radio_chimie, self.radio_chimie1)
        bacterio = self.get_radio_value(self.radio_bacterio, self.radio_bacterio1)
        ref_bact = self.get_radio_value(self.radio_refbacteriologique, self.radio_refbacteriologique1)
        ref_chim = self.get_radio_value(self.radio_refchimie, self.radio_refchimie1)

        self.setEnabled(False)

        self.worker = MapWorker(chimique, bacterio, ref_bact, ref_chim)
        self.worker.finished.connect(self.on_map_ready)
        self.worker.start()

    def on_map_ready(self):
        self.load_map()
        self.setEnabled(True)

        # mise à jour du label avec le nombre de communes
        count = len(self.worker.last_communes)
        self.lbl_count.setText(f"Nombre de communes : {count}")


# -------------------------
# Lancement
# -------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())