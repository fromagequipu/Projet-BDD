import sys
import os
import requests
import folium

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QLabel, QComboBox, QPushButton
)
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView


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
        self.setWindowTitle("Supervision Qualité de l'Eau")
        self.resize(900, 600)

        # Widget central
        central = QWidget()
        layout = QVBoxLayout(central)

        # Label
        label = QLabel("Choisissez une ville :")
        layout.addWidget(label)

        # ComboBox villes
        self.combo = QComboBox()
        self.combo.addItem("Sélectionner une ville", None)
        self.combo.addItem("Nantes", "44000")
        self.combo.addItem("Rennes", "35000")
        self.combo.addItem("Saint André des Eaux", "44151")
        layout.addWidget(self.combo)

        # Bouton
        button = QPushButton("Afficher la carte")
        button.clicked.connect(self.update_map)
        layout.addWidget(button)

        # Vue Web (carte)
        self.browser = QWebEngineView()
        layout.addWidget(self.browser)

        self.setCentralWidget(central)

        # Carte initiale
        create_map()
        self.load_map()

    def load_map(self):
        path = os.path.abspath(MAP_FILE)
        self.browser.load(QUrl.fromLocalFile(path))

    def update_map(self):
        insee_code = self.combo.currentData()
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
