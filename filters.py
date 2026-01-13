# REQUETES DES FILTRES

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