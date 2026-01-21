# REQUETES DES FILTRES

import sqlite3

# Filtre 1 : Récupère les résultats des quatre type de conformités pour afficher les communes correspondantes
def get_communes_conformites(cursor, chimique, bacterio, ref_bact, ref_chim):
    """Returns all the associations from the database.
  
    Parameters
    ----------
    cursor : 
        The object used to query the database.
  
    Returns
    -------
    A (possibly, empty) list of all the associations in the database. 
    Each item of the list is a tuple (asso_name, asso_desc).
    
    If an error occurs while querying the database, the function returns None.
    """
    # try:
    #     # Valeurs test
    #     #C1="N"
    #     #C2="N"
    #     #C3="N"
    #     #C4="N"
    #     # Requête qui permet de visualiser les infos des communes => Limitation de 20000 communes sinon trop lent dans les requêtes
    #     cursor.execute("SELECT DISTINCT c.inseecommune, c.nomcommune, c.lat, c.lon FROM Commune c JOIN Prelevement p ON p.cdreseau = c.cdreseau WHERE p.plvconformitechimique = ? AND p.plvconformitebacterio = ? AND p.plvconformitereferencebact = ? AND p.plvconformitereferencechim = ? LIMIT 20000;", (chimique, bacterio, ref_bact, ref_chim))
    #     row = cursor.fetchall()
    # except sqlite3.Error as error:
    #     print(error)
    #     return None
    # print("Le resultat est", row)
    # return row
    try : 
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

        def conform(values):
            return ",".join("?" for _ in values)

        query = query.format(
            chimique=conform(chimique),
            bacterio=conform(bacterio),
            ref_bact=conform(ref_bact),
            ref_chim=conform(ref_chim),
        )

        params = chimique + bacterio + ref_bact + ref_chim
        cursor.execute(query, params)
        return cursor.fetchall()

    except sqlite3.Error as error:
        print("Erreur SQL :", error)
        return []

# Filtre 2 : Récupère les communes en fonction d'une date de prélèvement  
def get_communes_dateprel(cursor, dateprel):
    """
    Retourne les communes ayant un prélèvement à une date donnée
    (coordonnées incluses pour affichage sur carte)
    """
    try:
        query = """
            SELECT DISTINCT
                c.inseecommune,
                c.nomcommune,
                c.lat,
                c.lon
            FROM Commune c
            JOIN Prelevement p ON p.cdreseau = c.cdreseau
            WHERE p.dateprel = ?
        """
        cursor.execute(query, (dateprel,))
        return cursor.fetchall()

    except sqlite3.Error as error:
        print("Erreur SQL :", error)
        return None


#Filtre n°5 : Récuperation des molécules
def get_molecules(cursor):
    """
    Retourne les communes ayant un prélèvement à une date donnée
    (coordonnées incluses pour affichage sur carte)
    """
    try:
        query = """
            SELECT DISTINCT
                p1.libminparametre
            FROM Parametre p1
            JOIN Prelevement p ON p.referenceprel = p1.referenceprel JOIN Commune c ON c.cdreseau = p.cdreseau
        """
        cursor.execute(query)
        return [row[0] for row in cursor.fetchall()]

    except sqlite3.Error as error:
        print("Erreur SQL :", error)
        return None

# Filtre 3 : Récupère les communes en fonction d'un paramètre et de sa valeur
def get_communes_parametre(cursor,param,valeur):
    """Returns all the associations from the database.
  
    Parameters
    ----------
    cursor : 
        The object used to query the database.
  
    Returns
    -------
    A (possibly, empty) list of all the associations in the database. 
    Each item of the list is a tuple (asso_name, asso_desc).
    
    If an error occurs while querying the database, the function returns None.
    """
    try:
        # Valeurs test
        #param="pH"
        #valeur="5.9"
        # Requête qui permet de visualiser les infos des associations
        cursor.execute("SELECT c.inseecommune, c.nomcommune FROM Commune c JOIN Prelevement p ON p.cdreseau = c.cdreseau JOIN Parametre m ON m.referenceprel = p.referenceprel WHERE m.libminparametre=? AND m.valtraduite=?;", (param,valeur,))
        row = cursor.fetchall()
    except sqlite3.Error as error:
        print(error)
        return None
    print("Le resultat est", row)
    return row

#Filtre n°6
def get_refqual(cursor, parametre):
    """
    Retourne la valeur réglementaire (refqual) associée à une molécule
    """
    try:
        query = """
            SELECT DISTINCT pa.refqual
            FROM Parametre pa
            WHERE pa.libminparametre = ?
              AND pa.refqual IS NOT NULL
            LIMIT 1
        """
        cursor.execute(query, (parametre,))
        row = cursor.fetchone()
        return row[0] if row else ""

    except sqlite3.Error as error:
        print("Erreur SQL :", error)
        return ""



# Entry point of this module.
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

    # TEST FONCTION
    #get_communes_conformites(cursor)
    #get_communes_dateprel(cursor)
    #get_communes_parametre(cursor)

    # Close the connection to the database.
    cursor.close()
    conn.close()