import sys
import os
import requests
import folium

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QDateEdit, QGroupBox,
    QButtonGroup, QRadioButton
)
from PyQt5.QtCore import QUrl, QDate, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QIcon


MAP_FILE = "map.html"


# -------------------------
# API INSEE
# -------------------------
def get_coordinates_and_name_from_insee(insee_code):
    url = f"https://api-adresse.data.gouv.fr/search/?q={insee_code}&type=municipality&limit=1"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data["features"]:
            name = data["features"][0]["properties"]["label"]
            lon, lat = data["features"][0]["geometry"]["coordinates"]
            return name, lat, lon
    return None, None, None


# -------------------------
# Création carte Folium
# -------------------------
def create_map(insee_code=None):
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

    m.save(MAP_FILE)


# -------------------------
# Fenêtre principale
# -------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
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
        boxville = QGroupBox("Ville")
        boxville.setLayout(ville_layout)
        
        self.combo_ville = QComboBox()
        
        
        #Partie à changer pour pouvoir faire dynamiquement
        self.combo_ville.addItem("Sélectionner une ville", None)
        self.combo_ville.addItem("Nantes", "44000")
        self.combo_ville.addItem("Rennes", "35000")
        self.combo_ville.addItem("Saint André des Eaux", "44151")
        
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
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        
        col1_layout.addWidget(QLabel("Date"))
        col1_layout.addWidget(self.date_edit)

        # -------------------------
        # COLONNE 2 - Conformité
        # -------------------------
        col2_layout = QVBoxLayout()
        box2 = QGroupBox("Conformité")
        box2.setLayout(col2_layout)

        self.combo_conformite = QButtonGroup()
        radio_c = QRadioButton("Conforme")
        radio_nc = QRadioButton("Non conforme")
        statut_layout = QHBoxLayout()
        statut_layout.addWidget(QLabel("Limite Bactériologique"))
        statut_layout.addWidget(radio_c)
        statut_layout.addWidget(radio_nc)
        col2_layout.addLayout(statut_layout)
        #col2_layout.addWidget(QLabel("Statut"))
        #col2_layout.addWidget(radio_c)
        #col2_layout.addWidget(radio_nc)
        #self.combo_conformite.addItem("Conforme", "C")
        #self.combo_conformite.addItem("Non conforme", "NC")

        self.combo_categorie = QButtonGroup()
        radio_chimie = QRadioButton("Conforme")
        radio_chimie1 = QRadioButton("Non conforme")
        statut_layout2 = QHBoxLayout()
        statut_layout2.addWidget(QLabel("Limite Physico-chimique"))
        statut_layout2.addWidget(radio_chimie)
        statut_layout2.addWidget(radio_chimie1)
        col2_layout.addLayout(statut_layout2)

        self.combo_refbacteriologique = QButtonGroup()
        radio_refbacteriologique = QRadioButton("Conforme")
        radio_refbacteriologique1 = QRadioButton("Non conforme")
        statut_layout2 = QHBoxLayout()
        statut_layout2.addWidget(QLabel("Référence Bactériologique"))
        statut_layout2.addWidget(radio_refbacteriologique)
        statut_layout2.addWidget(radio_refbacteriologique1)
        col2_layout.addLayout(statut_layout2)

        self.combo_refchimie = QButtonGroup()
        radio_refchimie = QRadioButton("Conforme")
        radio_refchimie1 = QRadioButton("Non conforme")
        statut_layout2 = QHBoxLayout()
        statut_layout2.addWidget(QLabel("Référence Physico-chimique"))
        statut_layout2.addWidget(radio_refchimie)
        statut_layout2.addWidget(radio_refchimie1)
        col2_layout.addLayout(statut_layout2)
        #self.combo_categorie = QComboBox()
        #self.combo_categorie.addItem("Bactéries")
        #self.combo_categorie.addItem("Chimie")
        #self.combo_categorie.addItem("Référence Bactérie")
        #self.combo_categorie.addItem("Référence Chimie")

        #col2_layout.addWidget(QLabel("Statut"))
        #col2_layout.addWidget(self.combo_conformite)
        #col2_layout.addWidget(QLabel("Catégorie"))
        #col2_layout.addWidget(self.combo_categorie)

        # -------------------------
        # COLONNE 3 - Paramètres
        # -------------------------
        col3_layout = QVBoxLayout()
        box3 = QGroupBox("Paramètres")
        box3.setLayout(col3_layout)

        self.combo_molecule = QComboBox()
        self.combo_molecule.addItem("Nitrate")
        self.combo_molecule.addItem("Phosphate")
        self.combo_molecule.addItem("pH")

        self.button = QPushButton("Afficher la carte")
        self.button.clicked.connect(self.update_map)

        col3_layout.addWidget(QLabel("Molécule"))
        col3_layout.addWidget(self.combo_molecule)
        col3_layout.addStretch()
        col3_layout.addWidget(self.button)

        # Ajout des colonnes
        top_layout.addWidget(boxville)
        top_layout.addWidget(box2)
        top_layout.addWidget(box3)

        # -------------------------
        # Carte (pleine largeur en bas)
        # -------------------------
        self.browser = QWebEngineView()
        main_layout.addWidget(self.browser, stretch=1)

        # Carte initiale
        create_map()
        self.load_map()

    def load_map(self):
        path = os.path.abspath(MAP_FILE)
        self.browser.load(QUrl.fromLocalFile(path))

    def update_map(self):
        insee_code = self.combo_ville.currentData()
        create_map(insee_code)
        self.load_map()


# -------------------------
# Lancement
# -------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())