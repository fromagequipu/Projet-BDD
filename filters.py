# REQUETES SQL DES FILTRES

### BIBLIOTHEQUE : SQL ###
import sqlite3


def get_commune_by_insee(cursor, insee):
    try:
        query = """
            SELECT
                inseecommune,
                nomcommune,
                lat,
                lon
            FROM Commune
            WHERE inseecommune = ?
        """
        cursor.execute(query, (insee,))
        return cursor.fetchall()

    except sqlite3.Error as error:
        print("Erreur SQL :", error)
        return []


# Filtre 2 (au centre de l'application) : Récupère les résultats des quatre type de conformités pour afficher les communes correspondantes
# Récupère en paramètre si l'élément a été coché ou non (C ou N) pour les 4 conformités
def get_communes_conformites(cursor, chimique, bacterio, ref_bact, ref_chim):
    """
    Retourne les communes en fonction des conformités
    """
    # Valeurs test pour tester la requête
    #C1="N"
    #C2="N"
    #C3="N"
    #C4="N"
       
    try : 
        # Requête SQL qui permet de visualiser les infos des communes (nom, insee, coord) en fonction des conformités sélectionnées de la table Prélèvement
        # => Limitation de 20 000 communes sinon trop lent dans les requêtes => plus de 34 000 communes dans la BDD
        query = """
            SELECT DISTINCT
                c.inseecommune,
                c.nomcommune,
                c.lat,
                c.lon
            FROM Commune c
            JOIN Prelevement p ON p.cdreseau = c.cdreseau
            WHERE (p.plvconformitechimique IN ({chimique}))
            AND (p.plvconformitebacterio IN ({bacterio}))
            AND (p.plvconformitereferencebact IN ({ref_bact}))
            AND (p.plvconformitereferencechim IN ({ref_chim}))
            LIMIT 20000;
        """
        # Fonction conform qui génère le bon nombre de placeholders SQL ("?") en fonction du nombre de valeurs passées en paramètre
        # Exemple :
        # values = [C, C]
        # conform(values) -> "?, ?" -> va s'adapter aux nombres d'éléments cochés dans le filtre
        def conform(values):
            return ",".join("?" for _ in values)

        # Remplacement des placeholders dynamiques dans la requête SQL
        # Chaque champ de conformité reçoit le bon nombre de "?" selon la taille des listes chimique, bacterio, ref_bact et ref_chim
        query = query.format(
            chimique=conform(chimique),
            bacterio=conform(bacterio),
            ref_bact=conform(ref_bact),
            ref_chim=conform(ref_chim),
        )

        # Exécution de toutes les conformités en même temps dans la requête
        params = chimique + bacterio + ref_bact + ref_chim
        cursor.execute(query, params)
        # Renvoie le résultat
        return cursor.fetchall()

    # En cas d'erreur SQL
    except sqlite3.Error as error:
        print("Erreur SQL :", error)
        return []

# Filtre 1 (à gauche de l'application) : Récupère les communes en fonction d'une date de prélèvement de début et de fin
def get_communes_dateprel(cursor, date_start, date_end):
    """
    Retourne les communes ayant au moins un prélèvement
    dans l'intervalle de dates donné
    """
    try:
        # Requête qui récupère les informations des communes et qui joint à la table Prélèvement afin de récupérer les dates
        # Limitations à 20 000 communes également sinon chargement trop long dans l'application => plantage 
        query = """
            SELECT DISTINCT
                c.inseecommune,
                c.nomcommune,
                c.lat,
                c.lon
            FROM Commune c
            JOIN Prelevement p ON p.cdreseau = c.cdreseau
            WHERE p.dateprel BETWEEN ? AND ?
            LIMIT 20000;
        """
        # Exécution de la requête 
        cursor.execute(query, (date_start, date_end))
        # Affichage du résultat
        return cursor.fetchall()

    # En cas d'erreur SQL
    except sqlite3.Error as error:
        print("Erreur SQL :", error)
        return []


# Alimentation du menu déroulant du filtre 3 : Récuperation des paramètres
def get_molecules(cursor):
    """
    Renvoi la liste des paramètres de la table Parametre

    """
    try:
        # Requête qui récupère distinctement tous les paramètres relevés dans les communes
        query = """
            SELECT DISTINCT
                p1.libminparametre
            FROM Parametre p1
            JOIN Prelevement p ON p.referenceprel = p1.referenceprel JOIN Commune c ON c.cdreseau = p.cdreseau
        """
        # Exécution de la requête
        cursor.execute(query)
        # Renvoi du résultat
        return [row[0] for row in cursor.fetchall()]

    # En cas d'erreur SQL
    except sqlite3.Error as error:
        print("Erreur SQL :", error)
        return None

# Filtre 3 (à droite de l'application): Récupère les communes en fonction d'un paramètre et de sa valeur personnalisée
def get_communes_parametre(cursor,param,valeur):
    """
    Retourne les communes en fonction de la valeur d'un paramètre sélectionné
    """
    try:
        # Valeurs pour tester la requête  
        # param="pH"
        # valeur="5.9"
        # Requête qui permet de visualiser les infos des communes et de joindre à la table prélèvement et paramètre pour récupèrer seulement celles qui sont associées au paramètre et à la valeur sélectionnée
        cursor.execute("SELECT c.inseecommune, c.nomcommune FROM Commune c JOIN Prelevement p ON p.cdreseau = c.cdreseau JOIN Parametre m ON m.referenceprel = p.referenceprel WHERE m.libminparametre=? AND m.valtraduite=?;", (param,valeur,))
        row = cursor.fetchall()
    # En cas d'erreur SQL
    except sqlite3.Error as error:
        print(error)
        return None
    # Affichage du résultat
    print("Le resultat est", row)
    return row

# Alimentation du champ de valeur référence du paramètre pour connaître la norme (filtre 3) d'un paramètre sélectionné venant de la table Parametre
def get_refqual(cursor, parametre):
    """
    Retourne la valeur réglementaire (refqual) associée à un paramètre
    """
    try:
        # Requête qui permet de sélectionner la valeur de référence de la table Parametre, si elle n'est pas nulle
        query = """
            SELECT DISTINCT pa.refqual
            FROM Parametre pa
            WHERE pa.libminparametre = ?
              AND pa.refqual IS NOT NULL
            LIMIT 1
        """
        # Exécution de la requête
        cursor.execute(query, (parametre,))
        row = cursor.fetchone()
        # Affichage du résultat
        return row[0] if row else ""

    # En cas d'erreur SQL
    except sqlite3.Error as error:
        print("Erreur SQL :", error)
        return ""


# Filtre 3 (à droite de l'application): Récupère les communes en fonction d'un paramètre ainsi que d'un opérateur par rapport à une valeur personnalisée
def get_communes_by_parameter_value(cursor, molecule, seuil, operator):
    try:
        # Conversion du seuil en float
        seuil_float = float(seuil)
    except ValueError:
        return []

    # Vérifie que l’opérateur choisi est autorisé (> , < ou =)
    # Si l’opérateur fourni n'est pas valide, on utilise ">" par défaut
    if operator not in [">", "<", "="]:
        operator = ">"

    try:
        # Requête qui permet de récupérer distinctement les infos des communes pour lesquelles on sélectionne un paramètre et un opérateur (supérieur, égal ou inférieur) par rapport à la valeur choisie
        # Limitation à 20 000 communes aussi sinon plantage de l'application
        query = f"""
            SELECT DISTINCT 
                c.inseecommune, 
                c.nomcommune, 
                c.lat, 
                c.lon
            FROM Commune c
            JOIN Prelevement pr ON c.cdreseau = pr.cdreseau
            JOIN Parametre pa ON pr.referenceprel = pa.referenceprel
            WHERE pa.libminparametre = ?
              AND CAST(pa.valtraduite AS FLOAT) {operator} ?
              AND c.lat IS NOT NULL
              AND c.lon IS NOT NULL
            LIMIT 20000;
        """
        # Exécution de la requête
        cursor.execute(query, (molecule, seuil_float))
        # Affichage du résultat
        return cursor.fetchall()

    # En cas d'erreur SQL
    except sqlite3.Error as error:
        print("Erreur SQL :", error)
        return []

# Programma principal
if __name__ == '__main__':
    
    # Chemin de la BDD
    db_file = "WaterQuality.db"

    # Connects to the database.
    conn = sqlite3.connect(db_file)
    
    # Enables the foreign key contraints support in SQLite.
    conn.execute("PRAGMA foreign_keys = 1")
    
    # Get the cursor for the connection. This object is used to execute queries 
    # in the database.
    cursor = conn.cursor()

    # TEST DES FONCTIONS AVANT INTEGRATION DANS L'INTERFACE
    # get_communes_conformites(cursor)
    # get_communes_dateprel(cursor)
    # get_communes_parametre(cursor)

    # Close the connection to the database.
    cursor.close()
    conn.close()