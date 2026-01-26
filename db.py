# FICHIER DE CREATION DE NOTRE BDD

### BIBLIOTHEQUE : SQL ###
import sqlite3

# Création de la BDD WaterQuality.db
def create_database(conn, cursor):
    """Creates the WaterQuality database

    Parameters
    ----------
    conn : 
        The object used to manage the database connection.
    cursor : 
        The object used to query the database.

    Returns
    -------
    bool
        True if the database could be created, False otherwise.
    
    """

    cursor.execute("BEGIN")
    
    # Création des tables
    try:
        # Création de la table réseau qui contient les réseaux d'eau
        print("CREATION TABLE RESEAU")
        cursor.execute('''
        CREATE TABLE Reseau(
            cdreseau TEXT PRIMARY KEY,
            nomreseau TEXT
        )
        ''')

        # Création de la table commune qui contient les communes et leurs coordonnées et qui est relié à la table réseau
        # La clé primaire contient deux attributs : insee + réseau pour rendre chaque id unique
        print("CREATION TABLE COMMUNE")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Commune(
                cdreseau TEXT,
                inseecommune TEXT,
                nomcommune TEXT,
                lat REAL,
                lon REAL,
                PRIMARY KEY (inseecommune, cdreseau),
                FOREIGN KEY (cdreseau) REFERENCES Reseau(cdreseau)
            )
        ''')

        # Création de la table prelèvement qui contient l'association des communes et le prélèvement de leurs paramètres ainsi que leurs conformités
        # La table est également reliée à la table Reseau
        print("CREATION TABLE PRELEVEMENT")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Prelevement(
                referenceprel TEXT PRIMARY KEY,
                cdreseau TEXT,
                dateprel DATE,
                plvconformitebacterio TEXT, 
                plvconformitechimique TEXT,
                plvconformitereferencebact TEXT,
                plvconformitereferencechim TEXT,
                FOREIGN KEY (cdreseau) REFERENCES Reseau(cdreseau)
            )
        ''')

        # Création de la table paramètre qui contient les paramètres de qualité relevés lors des prévèlements
        # La table est donc reliée à la table prélèvement 
        # Nous avons ajouté une auto-incrémentation de l'id
        print("CREATION TABLE PARAMETRE")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Parametre(
                id_param INTEGER PRIMARY KEY AUTOINCREMENT,
                referenceprel TEXT,
                libminparametre TEXT,
                valtraduite TEXT, 
                cdunitereferencesiseeaux TEXT,
                refqual TEXT,
                FOREIGN KEY (referenceprel) REFERENCES Prelevement(referenceprel)
            )
        ''')
       
       ###################################################################
        
    # Exception raised when something goes wrong while creating the tables.
    except sqlite3.Error as error:
        print("An error occurred while creating the tables: {}".format(error))
        # IMPORTANT : we rollback the transaction! No table is created in the database.
        conn.rollback()
        # Return False to indicate that something went wrong.
        return False

    # If we arrive here, that means that no error occurred.
    # IMPORTANT : we must COMMIT the transaction, so that all tables are actually created in the database.
    conn.commit()    
    print("Database created successfully")
    # Returns True to indicate that everything went well!
    return True

# The entry point of this module.
if __name__ == "__main__":

    # Chemin de la BDD
    db_file = "WaterQuality.db"

    # Open a connection to the database.
    conn = sqlite3.connect(db_file)

    # The cursor is used to execute queries to the database.
    cursor = conn.cursor()

    # Creates the database. THIS IS THE FUNCTION THAT YOU'LL NEED TO MODIFY
    create_database(conn, cursor)

    # Closes the connection to the database
    cursor.close()
    conn.close()