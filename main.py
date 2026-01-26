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
from filters import get_communes_by_parameter_value


from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QDateEdit, QGroupBox,
    QButtonGroup, QRadioButton, QCheckBox, QLineEdit, QCompleter,
    QToolButton, QMessageBox
)
from PyQt5.QtCore import QUrl, QDate, Qt, QThread, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QIcon

# Fichier de sauvegarde de la carte
MAP_FILE = "map.html"

# -------------------------
# API INSEE -> ALIMENTATION DE LA TABLE COMMUNE
# -------------------------

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

#On va créer la carte avec un marqueur folium
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

    def __init__(self, chimique, bacterio, ref_bact, ref_chim):
        super().__init__()
        self.chimique = chimique
        self.bacterio = bacterio
        self.ref_bact = ref_bact
        self.ref_chim = ref_chim

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
        # Génération de la carte
        create_map(communes)

        cursor.close()
        conn.close()

        self.finished.emit()

# -------------------------
# Fenêtre principale
# -------------------------
#Création de la fenêtre principal avec connexion à la BDD
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.conn = sqlite3.connect("WaterQuality.db")
        self.cursor = self.conn.cursor()

        #Titre de la fenêtre
        self.setWindowTitle("Water Quality")
        #Logo
        self.setWindowIcon(QIcon("logo.png"))
        self.resize(1650, 900)

        #Définition d'un gros widget central pour la fenêtre
        central = QWidget()
        self.setCentralWidget(central)

        # Layout principal (vertical)
        main_layout = QVBoxLayout(central)

        # Layout titre
        titre_layout = QHBoxLayout()
        main_layout.addLayout(titre_layout)
        
        #Layout choix ville
        ville_layout = QHBoxLayout()
        ville_layout.setAlignment(Qt.AlignCenter)
        boxville = QGroupBox("")
        boxville.setLayout(ville_layout)

        main_layout.addWidget(boxville)  
        

        self.combo_ville = QComboBox()
        self.combo_ville.addItem("Toutes les communes", None)

        query = """
            SELECT DISTINCT inseecommune, nomcommune
            FROM Commune
            ORDER BY nomcommune
        """
        self.cursor.execute(query)
        communes = self.cursor.fetchall()

        for insee, nom in communes:
            self.combo_ville.addItem(nom, insee)
        
        ville_layout.addWidget(QLabel(""))
        ville_layout.addWidget(self.combo_ville)

        self.combo_ville.currentIndexChanged.connect(
        self.update_map_from_commune
    )

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
        # COLONNE 1 - Général à gauche
        # -------------------------
        col1_layout = QVBoxLayout()
        box1 = QGroupBox("Date")
        box1.setLayout(col1_layout)
        
        #Bouton d'éxécution afficher la carte
        self.button1 = QPushButton("Afficher la carte")
        self.button1.clicked.connect(self.update_map)
        
        #Creation d'un champ date qui peut être modifié
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setMinimumDate(QDate(2024, 1, 1))
        self.date_start.setMaximumDate(QDate(2024, 12, 31))
        self.date_start.setDate(QDate(2024, 1, 1))
        self.date_start.setDisplayFormat("dd-MM-yyyy")

        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setMinimumDate(QDate(2024, 1, 1))
        self.date_end.setMaximumDate(QDate(2024, 12, 31))
        self.date_end.setDate(QDate(2024, 12, 31))
        self.date_end.setDisplayFormat("dd-MM-yyyy")

        #On peut définir une date de début et une date de fin
        col1_layout.addWidget(QLabel("Date début :"))
        col1_layout.addWidget(self.date_start)

        col1_layout.addWidget(QLabel("Date fin :"))
        col1_layout.addWidget(self.date_end)

        col1_layout.addWidget(self.button1)
        


        # -------------------------
        # COLONNE 2 - Conformité (Partie centrale)
        # -------------------------
        col2_layout = QVBoxLayout()
        box2 = QGroupBox("Conformité")
        box2.setLayout(col2_layout)

        # ----- CONFORMITE BACTERIOLOGIQUE -----

        self.radio_bacterio = QCheckBox("Conforme")
        self.radio_bacterio1 = QCheckBox("Non conforme")

        label_bacterio = QLabel("Limite Bactériologique")

        # ----- BOUTON INFO -----
        info_bacterio = QToolButton()
        info_bacterio.setToolButtonStyle(Qt.ToolButtonIconOnly)

        # Icône standard Qt
        info_bacterio.setIcon(QApplication.style().standardIcon(QApplication.style().SP_MessageBoxInformation))
        
        # Fenêtre pop-up pour afficher l'information supplémentaire
        def show_info():
            QMessageBox.information(
                None,
                "Limite Bactériologique",
                "Indicateur de la conformité des paramètres microbiologiques aux limites de qualité en vigueur au moment du\n"
                "prélèvement pour le type d’eau considéré.\n"
                "Valeurs possibles : 'blanc', 'C=conforme', 'N=non conforme', 'S' (sans objet lorsqu'aucun paramètre microbio n'a été mesuré)."
            )

        info_bacterio.clicked.connect(show_info)

        #Mise en forme des boutons à l'horizontal 
        statut_layout = QHBoxLayout()
        statut_layout.addWidget(label_bacterio)
        statut_layout.addWidget(info_bacterio) # icône info
        statut_layout.addWidget(self.radio_bacterio)
        statut_layout.addWidget(self.radio_bacterio1)

        col2_layout.addLayout(statut_layout)

        # ----- CONFORMITE PHYSICO-CHIMIQUE -----

        self.radio_chimie = QCheckBox("Conforme")
        self.radio_chimie1 = QCheckBox("Non conforme")
        statut_layout2 = QHBoxLayout()
        statut_layout2.addWidget(QLabel("Limite Physico-chimique"))

        # ----- BOUTON INFO -----
        info_chimie = QToolButton()
        info_chimie.setToolButtonStyle(Qt.ToolButtonIconOnly)

        # Icône standard Qt
        info_chimie.setIcon(QApplication.style().standardIcon(QApplication.style().SP_MessageBoxInformation))
        
        # Fenêtre pop-up pour afficher l'information supplémentaire
        def show_info():
            QMessageBox.information(
                None,
                "Limite Physico-chimique",
                "Indicateur de la conformité des paramètres chimiques aux limites de qualité en vigueur au moment du prélèvement\n"
                "pour le type d’eau considéré (et en prenant en compte les dérogations éventuelles en cours pour l'installation concernée).\n"
                "Valeurs possibles : 'blanc', 'C=conforme', 'N=non conforme', 'D=conforme dans le cadre d’une dérogation','S (sans objet lorsqu'aucun paramètre chimique n'a été mesuré)'."
            )

        info_chimie.clicked.connect(show_info)

        statut_layout2.addWidget(info_chimie)
        statut_layout2.addWidget(self.radio_chimie)
        statut_layout2.addWidget(self.radio_chimie1)
        col2_layout.addLayout(statut_layout2)

        # ----- CONFORMITE REF BACTERIOLOGIQUE -----

        self.radio_refbacteriologique = QCheckBox("Conforme")
        self.radio_refbacteriologique1 = QCheckBox("Non conforme")
        statut_layout2 = QHBoxLayout()
        statut_layout2.addWidget(QLabel("Référence Bactériologique"))

        # ----- BOUTON INFO -----
        info_refbact = QToolButton()
        info_refbact.setToolButtonStyle(Qt.ToolButtonIconOnly)

        # Icône standard Qt
        info_refbact.setIcon(QApplication.style().standardIcon(QApplication.style().SP_MessageBoxInformation))
        
        # Fenêtre pop-up pour afficher l'information supplémentaire
        def show_info():
            QMessageBox.information(
                None,
                "Référence Bactériologique",
                "Indicateur de la conformité des paramètres microbiologiques aux références de qualité en vigueur au moment du\n"
                "prélèvement pour le type d’eau considéré.\n"
                "Valeurs possibles : 'blanc', 'C=conforme', 'N=non conforme', 'S (sans objet lorsqu'aucun paramètre microbio n'a été mesuré)."
                )

        info_refbact.clicked.connect(show_info)

        statut_layout2.addWidget(info_refbact)
        statut_layout2.addWidget(self.radio_refbacteriologique)
        statut_layout2.addWidget(self.radio_refbacteriologique1)
        col2_layout.addLayout(statut_layout2)

         # ----- CONFORMITE REF PHYSICO-CHIMIQUE -----

        self.radio_refchimie = QCheckBox("Conforme")
        self.radio_refchimie1 = QCheckBox("Non conforme")
        statut_layout2 = QHBoxLayout()
        statut_layout2.addWidget(QLabel("Référence Physico-chimique"))
        
        # ----- BOUTON INFO -----
        info_refchimie = QToolButton()
        info_refchimie.setToolButtonStyle(Qt.ToolButtonIconOnly)

        # Icône standard Qt
        info_refchimie.setIcon(QApplication.style().standardIcon(QApplication.style().SP_MessageBoxInformation))
        
        # Fenêtre pop-up pour afficher l'information supplémentaire
        def show_info():
            QMessageBox.information(
                None,
                "Référence Physico-Chimique",
                "Indicateur de la conformité des paramètres chimiques aux références de qualité en vigueur au moment du prélèvement\n"
                "pour le type d’eau considéré.\n"
                "Valeurs possibles : 'blanc', 'C=conforme', 'N=non conforme', 'S (sans objet lorsqu'aucun paramètre chimique n'a été mesuré)'."
            )

        info_refchimie.clicked.connect(show_info)

        statut_layout2.addWidget(info_refchimie)
        statut_layout2.addWidget(self.radio_refchimie)
        statut_layout2.addWidget(self.radio_refchimie1)

        col2_layout.addLayout(statut_layout2)

        # Bouton pour actualiser la carte avec les conformités sélectionnées
        self.btn_actualiser = QPushButton("Afficher la carte")
        col2_layout.addWidget(self.btn_actualiser)
        self.btn_actualiser.clicked.connect(self.update_map_with_conformities)

        # -------------------------
        # COLONNE 3 - Paramètres (partie droite)
        # -------------------------
        col3_layout = QVBoxLayout()
        box3 = QGroupBox("Parametres")
        box3.setLayout(col3_layout)
        box3.setMaximumWidth(650)
        
        # Récupération des molécules depuis la BDD
        parametres = get_molecules(self.cursor)
        parametres.sort()
        # Menu déroulant des molécules
        self.combo_molecule = QComboBox()
        self.combo_molecule.addItem("Sélectionner un parametre")
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
        self.value_input.setPlaceholderText("Valeur de référence")
        self.combo_molecule.currentTextChanged.connect(self.update_refqual)
        
        #Suggestions proposées pour les valeurs à renseigner
        completer = QCompleter(suggestions)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)

        self.value_input.setCompleter(completer)
        
        #Creation du champ label pour entrer la valeur personnalisé
        self.manual_value_input = QLineEdit()
        self.manual_value_input.setPlaceholderText("Entrer la valeur personnalisée")
        
        # RADIO BUTTONS COMPARAISON
# -----------------------
        self.radio_sup = QRadioButton("Supérieur à")
        self.radio_inf = QRadioButton("Inférieur à")
        self.radio_eq = QRadioButton("Égal à")

        # Groupe pour forcer un seul choix
        self.group_comparaison = QButtonGroup(self)
        self.group_comparaison.addButton(self.radio_sup)
        self.group_comparaison.addButton(self.radio_inf)
        self.group_comparaison.addButton(self.radio_eq)
        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.radio_sup)
        radio_layout.addWidget(self.radio_eq)
        radio_layout.addWidget(self.radio_inf)

        # Valeur par défaut
        self.radio_sup.setChecked(True)
        
        # -----------------------

        # Bouton
        self.button = QPushButton("Afficher la carte")
        self.button.clicked.connect(self.update_map_with_parameter_value)

        # Ajout au layout
        col3_layout.addWidget(QLabel("Choisir un parametre :"))
        col3_layout.addWidget(self.combo_molecule)

        col3_layout.addWidget(QLabel("Valeur de référence:"))
        col3_layout.addWidget(self.value_input)
        
        col3_layout.addWidget(QLabel("Saisir la valeur personnalisée :"))
        col3_layout.addWidget(self.manual_value_input)

        col3_layout.addStretch()
        col3_layout.addWidget(self.button)

        col3_layout.addWidget(QLabel("Condition sur la valeur :"))
        col3_layout.addLayout(radio_layout)

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
        
    def update_map_from_commune(self):
        """
        Mise à jour automatique de la carte
        déclenchée par la sélection d'une commune
        """
        # On réutilise le comportement EXISTANT
        self.update_map()


    def update_map(self):
        insee_code = self.combo_ville.currentData()
        create_map([])
        date_start = self.date_start.date().toString("dd-MM-yyyy")
        date_end = self.date_end.date().toString("dd-MM-yyyy")

        communes = get_communes_dateprel(self.cursor, date_start, date_end)

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

        #Mets à jour la carte avec les informations renseignées avant, permet d'avoir quelque chose de dynamique
    def update_map_with_parameter_value(self):
        molecule = self.combo_molecule.currentText()
        seuil = self.manual_value_input.text().strip()

        if molecule == "Sélectionner un parametre" or not seuil:
            QMessageBox.warning(
                self,
                "Erreur",
                "Veuillez sélectionner un paramètre et saisir une valeur."
            )
            return

        # Détermination de l'opérateur selon le radio bouton
        if self.radio_sup.isChecked():
            operator = ">"
        elif self.radio_inf.isChecked():
            operator = "<"
        else:
            operator = "="

        communes = get_communes_by_parameter_value(
            self.cursor,
            molecule,
            seuil,
            operator
        )

        create_map(communes)
        self.lbl_count.setText(f"Nombre de communes : {len(communes)}")
        self.load_map()



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