# REQUETES DES FILTRES

import sqlite3

def get_conformites(cursor):
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
        # Reqûete qui permet de visualiser les infos des associations
        cursor.execute("SELECT c.inseecommune, c.nomcommune FROM Commune c JOIN Prelevement p ON p.cdreseau = c.cdreseau WHERE p.plvconformitechimique = ? AND p.plvconformitebacterio = ? AND p.plvconformitereferencebact = ? AND p.plvconformitereferencechim = ?;", (VARS,))
        row = cursor.fetchall()
    except sqlite3.Error as error:
        print(error)
        return None
    print("Le resultat est", row)
    return row



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

    # Close the connection to the database.
    cursor.close()
    conn.close()