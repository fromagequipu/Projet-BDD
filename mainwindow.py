# INTERFACE DE SUPERVISION CARTE

### BIBLIOTHEQUES ###
# Bibliothèque carte géographique interactive
import folium
import requests

# PREMIER TEST FOLIUM



# Fonction pour obtenir les coordonnées et le nom depuis l'API de l'INSEE
def get_coordinates_and_name_from_insee(insee_code):
    # URL de l'API GéoAPI de l'INSEE
    url = f"https://api-adresse.data.gouv.fr/search/?q={insee_code}&type=municipality&limit=1"
    
    # Faire une requête GET pour obtenir les données
    response = requests.get(url)
    
    # Si la requête est réussie, extraire le nom, latitude et longitude
    if response.status_code == 200:
        data = response.json()
        if data['features']:
            # Extraire le nom, latitude et longitude
            name = data['features'][0]['properties']['label']  # Nom de la commune
            latitude = data['features'][0]['geometry']['coordinates'][1]  # Latitude
            longitude = data['features'][0]['geometry']['coordinates'][0]  # Longitude
            return name, latitude, longitude
        else:
            print(f"Aucune donnée trouvée pour le code INSEE : {insee_code}")
            return None, None, None
    else:
        print(f"Erreur avec l'API : {response.status_code}")
        return None, None, None

# Exemple de code INSEE
insee_code = "29200"

# Obtenir le nom, la latitude et la longitude
name, latitude, longitude = get_coordinates_and_name_from_insee(insee_code)

# Vérifier que nous avons bien des coordonnées
if name and latitude and longitude:
    # Créer la carte centrée sur la commune
    m = folium.Map(location=[latitude, longitude], zoom_start=12)
    
    # Ajouter un marqueur pour la commune avec son nom dynamique
    folium.Marker([latitude, longitude], popup=name).add_to(m)
    
    # Sauvegarder la carte
    m.save("commune_nantes.html")
    print("Carte de Nantes créée : commune_nantes.html")
else:
    print("Erreur dans l'obtention des coordonnées ou du nom.")




"""
#Position [latitude, longitude] sur laquelle est centrée la carte
location = [47, 1]

#Niveau de zoom initial : 
#3-4 pour un continent, 5-6 pour un pays, 11-12 pour une ville
zoom = 6

#Style de la carte
tiles = 'cartodbpositron'

Carte = folium.Map(location = location,
                   zoom_start = zoom,
                   tiles = tiles)


#Position du marqueur
location = [45.8, 1.2]

#Texte à afficher lorsqu'on clique sur le marqueur
texte = "Limoge est là (à peu près)"

#Création du marqueur
marqueur = folium.Marker(location = location,
                        popup = texte)

#Ajout à la carte
marqueur.add_to(Carte)

Carte.save("carte.html")
"""