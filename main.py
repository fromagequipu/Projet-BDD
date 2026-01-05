import sys
import requests
import folium
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton
from PyQt6.QtCore import Qt

# Fonction pour obtenir les coordonnées et le nom depuis l'API de l'INSEE
def get_coordinates_and_name_from_insee(insee_code):
    url = f"https://api-adresse.data.gouv.fr/search/?q={insee_code}&type=municipality&limit=1"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data['features']:
            name = data['features'][0]['properties']['label']
            latitude = data['features'][0]['geometry']['coordinates'][1]
            longitude = data['features'][0]['geometry']['coordinates'][0]
            return name, latitude, longitude
    return None, None, None


# Créer une carte avec Folium
def create_map(selected_code_insee=None, selected_name=None):
    codes_insee = {
        "Nantes": "44000",
        "Rennes": "35000",
        "Lyon": "69000"
    }

    # Créer la carte centrée sur la France
    m = folium.Map(location=[46.603354, 1.888334], zoom_start=6)

    # Sélectionner les communes à afficher
    communes_to_display = []

    if selected_code_insee:
        name, lat, lon = get_coordinates_and_name_from_insee(selected_code_insee)
        if name:
            communes_to_display.append({"name": name, "latitude": lat, "longitude": lon})

    if selected_name:
        # Si on a un nom de ville, on filtre par celui-ci
        if selected_name in codes_insee:
            code_insee = codes_insee[selected_name]
            name, lat, lon = get_coordinates_and_name_from_insee(code_insee)
            if name:
                communes_to_display.append({"name": name, "latitude": lat, "longitude": lon})

    # Ajouter les marqueurs pour chaque commune filtrée
    for commune in communes_to_display:
        folium.Marker([commune["latitude"], commune["longitude"]], popup=commune["name"]).add_to(m)

    # Sauvegarder la carte dans un fichier HTML
    m.save("carte_communes_filtrées.html")
    print("Carte générée : carte_communes_filtrées.html")


# Interface PyQt6
class SimpleMapApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Filtrer les Communes")
        self.setGeometry(100, 100, 300, 200)
        
        self.layout = QVBoxLayout()

        # Ajouter une étiquette
        self.label = QLabel("Choisissez un filtre pour la carte:", self)
        self.layout.addWidget(self.label)

        # Ajouter un combo box pour le choix du code INSEE
        self.combo_code_insee = QComboBox(self)
        self.combo_code_insee.addItem("Sélectionner un code INSEE")
        self.combo_code_insee.addItem("44000")  # Nantes
        self.combo_code_insee.addItem("35000")  # Paris
        self.combo_code_insee.addItem("69000")  # Lyon
        self.layout.addWidget(self.combo_code_insee)

        # Ajouter un combo box pour le choix du nom de la ville
        self.combo_name = QComboBox(self)
        self.combo_name.addItem("Sélectionner une ville")
        self.combo_name.addItem("Nantes")
        self.combo_name.addItem("Rennes")
        self.combo_name.addItem("Lyon")
        self.layout.addWidget(self.combo_name)

        # Ajouter un bouton pour générer la carte
        self.button = QPushButton("Générer la carte", self)
        self.button.clicked.connect(self.on_generate_map)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)

    def on_generate_map(self):
        # Récupérer les sélections
        selected_code_insee = self.combo_code_insee.currentText()
        selected_name = self.combo_name.currentText()

        # Vérifier si un code INSEE ou un nom de ville a été sélectionné
        if selected_code_insee != "Sélectionner un code INSEE":
            create_map(selected_code_insee=selected_code_insee)
        elif selected_name != "Sélectionner une ville":
            create_map(selected_name=selected_name)
        else:
            print("Aucun filtre sélectionné")

        print("Carte générée et sauvegardée sous 'carte_communes_filtrées.html'")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleMapApp()
    window.show()
    sys.exit(app.exec())
