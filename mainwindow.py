# INTERFACE DE SUPERVISION CARTE

### BIBLIOTHEQUES ###
# Bibliothèque carte géographique interactive
import folium

# PREMIER TEST FOLIUM

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