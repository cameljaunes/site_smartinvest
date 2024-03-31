# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 13:54:15 2024

@author: Lilou
"""

from flask import Flask, flash
from flask import render_template
from flask import request
from flask import redirect, url_for
from flask import session
from datetime import datetime
import numpy as np
import random
import hashlib
import secrets
import folium
import pandas as pd
import webbrowser




import sqlite3
import os.path
#Import de la librairie pour faire afficher les résultats en graphiques
import matplotlib.pyplot as plt
app = Flask(__name__)
app.secret_key = 'asjhfijawehttgiuwehauihtuiawehiuothuihweuihriuwea9812y458972y897y89ys78dfty87'


# ***************** Fonction de connection a la BD *******************
def connect():
   
    path = "db\projet_inte (2).db"
    connection = sqlite3.connect(path)
    if not os.path.exists(path):
        print(f"Le fichier {connection} n'existe pas")
        connection = None
    else:
        try:
            connection = sqlite3.connect(path)
            print("Connection to SQLite réussi")
        except sqlite3.Error as e:
            print(f"The error {e} occured")
    return connection

print(connect())

#j'associe la fonction connect() à la variable connection 
connection = connect() 


# **************** Fonction d'exectution de requete avec résultat ****************
def execute_requete(connection, requete):
    try:
        cursor = connection.cursor()
        cursor.execute(requete)
        #Recuperer les lignes (data)
        lignes = cursor.fetchall()
        #Recuperer les noms de colonnes (metadata)
        meta = cursor.description
        connection.close()
        return meta, lignes
    except sqlite3.Error as e2:
        print(f"The error {e2} occured")


# *********** Fonction d'exectution de requete sans résultat *************
def execute_query_SansResultat(connection, query):
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        connection.close()
    except sqlite3.Error as e2:
        print(f"The error {e2} occured")
  
        
    
def change_type(): #Fonction pour modifier de type de données dans la BD
#Changer le type de NbHab, NbPolice, NbBar, NbResto de INT à REAL car utile pour faire des calculs avec ratio    
    query = [
        """
        CREATE TABLE InfoQuartier_new (
            codeInfo INT PRIMARY KEY,
            NbHab REAL,
            NbPolice REAL,
            NbBar REAL,
            NbResto REAL
        )
        """,
        """
        INSERT INTO InfoQuartier_new (codeInfo, NbHab, NbPolice, NbBar, NbResto)
        SELECT codeInfo, CAST(NbHab AS REAL), CAST(NbPolice AS REAL), CAST(NbBar AS REAL), CAST(NbResto AS REAL)
        FROM InfoQuartier
        """,
        """
        DROP TABLE InfoQuartier
        """,
        """
        ALTER TABLE InfoQuartier_new RENAME TO InfoQuartier
        """
    ]
    
    for q in query:
        execute_query_SansResultat(connect(),q)

change_type()
        

# *************** Nos requêtes pour l'analyse générale *******************

requete_clara= """SELECT Q.codeQ, NomQ, ROUND(((NbBar + NbResto)/ NbHab) * 1000, 1) AS "Pourcentage d'annimation du quartier"
                    FROM Quartier Q, InfoQuartier IQ, Caractériser C
                    WHERE 
                        Q.codeQ = C.codeQ AND
                        C.codeInfo = IQ.codeInfo
                    
                    ORDER BY ((NbBar + NbResto)/ NbHab) DESC
                    LIMIT 5"""

meilleurbien = """ SELECT Q.NomQ AS 'Nom quartier', B.codeB AS codeBien, N.note as NoteBien 
                FROM Quartier Q, Bien B, Noter N
                WHERE Q.codeQ = B.codeQ
                AND B.codeB = N.codeB
                AND (B.codeB, N.note) IN (
                                        SELECT B2.codeB, MAX(N2.note)
                                        FROM Bien B2, Noter N2 
                                        WHERE B2.codeB = N2.codeB
                                        AND B2.codeQ = B.codeQ
                                        GROUP BY B2.codeQ
                                        )
                GROUP BY Q.NomQ
                ORDER BY Q.NomQ
                LIMIT 10
                """
                
qualite_prix = """
SELECT 
    B.codeB,
    B.Prix,
    Q.NomQ AS Quartier,
    N.note AS NoteBien
    
FROM 
    Bien B,
    Quartier Q,
    Noter N,
    (SELECT 
        B2.codeQ,
        AVG(B2.Prix) AS AvgPrixQuartier
    FROM 
        Bien B2
    GROUP BY 
        B2.codeQ
    ) AS Prix_Moyen
WHERE 
    B.codeQ = Q.codeQ
    AND B.codeB = N.codeB
    AND B.codeQ = Prix_Moyen.codeQ
    AND N.note > 3
    AND B.Prix < Prix_Moyen.AvgPrixQuartier
GROUP BY Q.NomQ
ORDER BY 
    N.note DESC
LIMIT 10;
 """
        
query_recherche = """ SELECT NomQ as "Nom Quartier"
FROM (
    SELECT NomQ, COUNT(Cl.codeCli) as nombre
    FROM Client Cl, Chercher C, Bien B, Quartier Q
    WHERE Cl.codeCli = C.codeCli
        AND C.codeB = B.codeB
        AND B.codeQ = Q.codeQ
    GROUP BY NomQ
    ORDER BY COUNT(Cl.codeCli) DESC
    LIMIT 1
) AS max_recherche;

 """
 
query_topBienRecherche = """ SELECT codeB, adresseB
FROM (
    SELECT B.codeB, adresseB, COUNT(*) AS nombre_recherches
    FROM Chercher C, Bien B
    WHERE C.codeB = B.codeB
    GROUP BY B.codeB
    ORDER BY COUNT(*) DESC
    LIMIT 1
) AS 'Bien le plus recheché';
"""
            
@app.route('/index', methods=['GET', 'POST'])                    
def affichepage():
    if 'nom' in session :
        if request.method == 'POST':
            
            #Execution des requêtes
            clara = requete_clara
            meta_clara, liste_clara = execute_requete(connect(), clara)
            
            best = meilleurbien
            meta_best, liste_best = execute_requete(connect(), best)
            
            QualiPrix = qualite_prix
            meta_qp, liste_qp = execute_requete(connect(), QualiPrix)
            
            
            return redirect(url_for('reponse_form', meta_clara=meta_clara, liste_clara=liste_clara, meta_best=meta_best, liste_best=liste_best, meta_qp=meta_qp, liste_qp=liste_qp))

        else:
            # Méthode 'GET'
            clara = requete_clara
            meta_clara, liste_clara = execute_requete(connect(), clara)
            
            best = meilleurbien
            meta_best, liste_best = execute_requete(connect(), best)
            
            QualiPrix = qualite_prix
            meta_qp, liste_qp = execute_requete(connect(), QualiPrix)
            
            QRech = query_recherche
            meta_qr, liste_qr = execute_requete(connect(), QRech)
            
            BRech = query_topBienRecherche
            meta_br, liste_br = execute_requete(connect(), BRech)
            
            # Création de graphique Matplotlib pour afficher la visualisation des résultats
            
            #Pour requete 1
            x_data = [row[1] for row in liste_clara]  # Noms des quartiers
            y_data = [row[2] for row in liste_clara]  # Valeurs Vie_quartier
            
            plt.figure(figsize=(6, 4))
            plt.bar(x_data, y_data, color='#f4623a')
            plt.xlabel('Quartier')
            plt.ylabel("Niveau d'Animation")
            plt.title("Nombre de lieux conviviaux (bars/restaurants) pour 1000 habitants")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # Sauvegarder le graphique dans un fichier image
            graph_image = 'static/graphique.png'
            plt.savefig(graph_image)
            carte=afficher_carte()
            carte2=afficher_carte_quartier_nbHab()
            carte4=afficher_carte_quartier_resto()
            carte3=afficher_carte_quartier_nbPolice()
            # session['email']= email
            # session['nom']= reslt[1]
            return render_template("index.html",carte4=carte4,carte3=carte3,carte2=carte2,carte=carte, nom=session['nom'], meta_clara=meta_clara, liste_clara=liste_clara, graph_image=graph_image, meta_best=meta_best, liste_best=liste_best, meta_qp=meta_qp, liste_qp=liste_qp,  meta_qr=meta_qr, liste_qr=liste_qr, meta_br=meta_br, liste_br=liste_br)

    
    else :
        session['erreur']= "Vous devez d'abord vous connecter pour accéder à nos services !"
        return redirect(url_for('connection'))
        
@app.route('/RecupReponse', methods=['GET', 'POST'])
def reponse_form():
    if request.method == 'GET':
        # Extract the data from the form
        Hab = int(request.args['jaugeA'])
        Resto = int(request.args['jaugeS'])

    print(Hab)
    print(Resto)
    # Exécuter la requête Clara pour récupérer les résultats
    clara = requete_clara
    meta_clara, liste_clara = execute_requete(connect(), clara)
    
    best = meilleurbien
    meta_best, liste_best = execute_requete(connect(), best)
    
    QualiPrix = qualite_prix
    meta_qp, liste_qp = execute_requete(connect(), QualiPrix)
    
    QRech = query_recherche
    meta_qr, liste_qr = execute_requete(connect(), QRech)
    
    BRech = query_topBienRecherche
    meta_br, liste_br = execute_requete(connect(), BRech)
    
    # Préparer les données pour le graphique
    x_data = [row[1] for row in liste_clara]  # Noms des quartiers
    y_data = [row[2] for row in liste_clara]  # Valeurs Vie_quartier
    
    # Créer le graphique avec Matplotlib
    plt.figure(figsize=(6, 4))
    plt.bar(x_data, y_data, color='#f4623a')
    plt.xlabel('Quartier')
    plt.ylabel("Niveau d'Animation")
    plt.title("Nb de lieux convivials (bars/restaurants) pour 1000 hab")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Sauvegarder le graphique dans un fichier image
    graph_image = 'static/graphique.png'
    plt.savefig(graph_image)

    # Exécuter la requête pour récupérer les données du quartier
    connection = connect()
    if connection:
        cursor=connection.cursor()
        requete_recupData = """SELECT Q.NomQ, Q.CP
                        FROM Quartier Q, InfoQuartier I
                        WHERE Q.codeQ = I.codeInfo
                        ORDER BY ABS(I.NbHab - ?) ASC, ABS(I.NbResto - ?) ASC
                        LIMIT 1;"""

        # Exécution de la requête avec les paramètres de requête nommés
        cursor.execute(requete_recupData, (Hab, Resto,))

        # Récupération du résultat de la requête
        lignes = cursor.fetchall()

        

        print(lignes)
        session['quartier'] = lignes[0][0]
    # On récupère le max et le min de chaque attribut en fonction du quartier

    cursor=connect().cursor()
    # Prix
    minprix1 = """SELECT min(prix) 
              FROM bien b, quartier q 
              WHERE Q.CODEQ = B.CODEQ
              AND Q.NOMQ = ?"""

    cursor.execute(minprix1, (str(session['quartier']),))
    minprix = cursor.fetchone()[0]

    
    
    maxprix1="""SELECT max(prix) 
        FROM bien b, quartier q 
        WHERE Q.CODEQ=B.CODEQ
        AND Q.NOMQ = ?"""

    cursor.execute(maxprix1, (str(session['quartier']),))
    maxprix=cursor.fetchone()[0]

    # TypeB
    typeB1="""SELECT distinct(typeB)
        FROM bien b, quartier q 
        WHERE Q.CODEQ=B.CODEQ
        AND Q.NOMQ = ?"""

    cursor.execute(typeB1, (str(session['quartier']),))
    typeB=cursor.fetchall()
    print(typeB)

    # NbPiece
    minnbpiece1="""SELECT min(nbpiece) 
        FROM bien b, quartier q 
        WHERE Q.CODEQ=B.CODEQ
        AND Q.NOMQ = ?"""

    cursor.execute(minnbpiece1, (str(session['quartier']),))
    minnbpiece=cursor.fetchone()[0]

    maxnbpiece1="""SELECT max(nbpiece) 
        FROM bien b, quartier q 
        WHERE Q.CODEQ=B.CODEQ
        AND Q.NOMQ = ?"""

    cursor.execute(maxnbpiece1, (str(session['quartier']),))
    maxnbpiece=cursor.fetchone()[0]

    # Surface
    minsurface1="""SELECT min(surface) 
        FROM bien b, quartier q 
        WHERE Q.CODEQ=B.CODEQ
        AND Q.NOMQ = ?"""

    cursor.execute(minsurface1, (str(session['quartier']),))
    minsurface=cursor.fetchone()[0]

    maxsurface1="""SELECT max(surface) 
        FROM bien b, quartier q 
        WHERE Q.CODEQ=B.CODEQ
        AND Q.NOMQ = ?"""

    cursor.execute(maxsurface1, (str(session['quartier']),))
    maxsurface=cursor.fetchone()[0]
    connection.close()

    carte=afficher_carte()
    carte2=afficher_carte_quartier_nbHab()
    carte4=afficher_carte_quartier_resto()
    carte3=afficher_carte_quartier_nbPolice()

    return render_template('index.html',carte4=carte4,carte3=carte3,carte2=carte2,carte=carte,nom=session['nom'], lignes=lignes, meta_clara=meta_clara, liste_clara=liste_clara, graph_image=graph_image, meta_best=meta_best, liste_best=liste_best, meta_qp=meta_qp, liste_qp=liste_qp, minprix=minprix,maxprix=maxprix,typeB=typeB,minnbpiece=minnbpiece,maxnbpiece=maxnbpiece,minsurface=minsurface,maxsurface=maxsurface, Hab=Hab, Resto=Resto, meta_qr=meta_qr, liste_qr=liste_qr, meta_br=meta_br, liste_br=liste_br)

   

@app.route('/RecupReponse2', methods=['GET'])
def reponse_form2():
    typeB = request.args['typeBien']
    surface = request.args['surface']
    nbpiece = request.args['nbpiece']
    prix = request.args['budget']
    quartier = session.get('quartier')
    
    
        
    print(prix)
    print(typeB)
    print(nbpiece)
    print(quartier)
    print(surface)

    connection = connect()
    if connection:
        requete_recupData2 = f"""SELECT * FROM (
                                    SELECT B.nbpiece, Q.nomQ, B.surface, B.prix, B.adresseB, B.TypeB, A.mailAg, A.telAg, B.codeB, B.GPS_B
                                    FROM Quartier Q, Bien B, Agence A
                                    WHERE Q.codeQ = B.codeQ
                                    AND Q.codeQ = A.codeQ
                                    AND TypeB = '{typeB}'
                                    AND Q.nomQ = "{quartier}"
                                    GROUP BY B.codeB

                                    UNION

                                    SELECT B.nbpiece, Q.nomQ, B.surface, B.prix, B.adresseB, B.TypeB, A.mailAg, A.telAg, B.codeB, B.GPS_B
                                    FROM Quartier Q, Bien B, Agence A
                                    WHERE Q.codeQ = B.codeQ
                                    AND Q.codeQ = A.codeQ
                                    GROUP BY B.codeB
                                ) AS r
                                ORDER BY r.nomQ = "{quartier}" DESC,r.nomQ = '{typeB}' DESC, ABS(r.Prix - {prix}) ASC, ABS(r.surface - {surface}) ASC
                                LIMIT 4;

                            """
                            
        meta, lignes = execute_requete(connection, requete_recupData2)
        
        if lignes:
            prix_vouloir = float(prix)
            prix_avoir = float(lignes[0][3]) 
            surface_vouloir = float(surface)
            surface_avoir = float(lignes[0][2]) 
            
            labels = ['']
            
            # Valeurs pour les barres Prix
            vouloir_data_prix = [prix_vouloir]
            avoir_data_prix = [prix_avoir]

            # Valeurs pour les barres Surface
            vouloir_data_surface = [surface_vouloir]
            avoir_data_surface = [surface_avoir]
            
            x = np.arange(len(labels))  # les positions des barres sur l'axe x
            width = 0.35  # largeur des barres
            
            # Création du graphique pour la comparaison de prix
            fig_prix, ax_prix = plt.subplots()
            ax_prix.bar(x - width/1.5, vouloir_data_prix, width, label='Prix souhaité', color='#f7886a')
            ax_prix.bar(x + width/1.5, avoir_data_prix, width, label='Prix proposé', color='#f4623a')
        
            ax_prix.set_ylabel('Prix en €')
            ax_prix.set_title('Comparaison de prix')
            ax_prix.set_xticks(x)
            ax_prix.set_xticklabels(labels)
            ax_prix.legend()

            # Sauvegarder le graphique sous forme d'image
            graphique_prix = 'static/comparaison_prix.png'
            plt.savefig(graphique_prix)
            plt.close(fig_prix)  # Fermer le graphique pour éviter l'affichage sur le serveur

            # Création du graphique pour la comparaison de surface
            fig_surface, ax_surface = plt.subplots()
            ax_surface.bar(x - width/1.5, vouloir_data_surface, width, label='Surface souhaitée', color='#f7886a')
            ax_surface.bar(x + width/1.5, avoir_data_surface, width, label='Surface proposée', color='#f4623a')
        
            ax_surface.set_ylabel('Surface en m²')
            ax_surface.set_title('Comparaison de surface')
            ax_surface.set_xticks(x)
            ax_surface.set_xticklabels(labels)
            ax_surface.legend()

            # Sauvegarder le graphique sous forme d'image
            graphique_surface = 'static/comparaison_surface.png'
            plt.savefig(graphique_surface)
            plt.close(fig_surface)  # Fermer le graphique pour éviter l'affichage sur le serveur
        
            session['lignes_autres_suggestions'] = lignes
            
        session['codeB'] = lignes[0][8]
        query_codecli='''
            select codecli
            from client
            where mailcli = ?
            '''
        connection=connect()
        cursor= connection.cursor()
        cursor.execute(query_codecli,(session['email'],))

        session['codeCli']=cursor.fetchone()[0]
        codeCli=session['codeCli']

        import datetime

        query_insert_chercher='''
                            INSERT INTO CHERCHER(DateRech, CodeCli, CodeB)
                            VALUES (?, ?, ?)
                            '''
        maintenant = datetime.datetime.now()
        date_heure_formatee = maintenant.strftime("%Y-%m-%d %H:%M:%S")
        print(date_heure_formatee)

        cursor= connection.cursor()
        cursor.execute(query_insert_chercher,(date_heure_formatee, codeCli, session['codeB']))
        connection.commit()
        
        # Récupération des coordonnées depuis la base de données
        gps_bien = lignes[0][9]  # Supposons que la 10ème colonne contient les coordonnées GPS

        # Séparation des coordonnées en longitude et latitude
        longitude, latitude = map(float, gps_bien.split(';'))

        # Construction de l'URL de l'iframe avec les nouvelles coordonnées
        url_iframe = f"https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d11575.351733065341!2d{longitude}!3d{latitude}!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!5e0!3m2!1sfr!2sfr!4v1711787448279!5m2!1sfr!2sfr"

# Passer l'URL de l'iframe au modèle pour l'afficher dans le HTML

    return render_template('Appart.html',nom=session['nom'],lignes=lignes, quartier=quartier, graphique_surface=graphique_surface, graphique_prix=graphique_prix, url_iframe=url_iframe)

                
        
@app.route('/couponYes')
def afficheCouponY():
    codeB = session.get('codeB')  

    return render_template('couponYes.html',nom=session['nom'], codeB=codeB)
                           
@app.route('/couponNo')
def afficheCouponN():
    # Récupérer les données de la session Flask
    lignes = session.get('lignes_autres_suggestions')
    
    # Passer les données récupérées au rendu de la page couponNo.html
    return render_template('couponNo.html',nom=session['nom'], lignes=lignes)

@app.route('/dommage')
def afficheDommage():
    return render_template('dommage.html',nom=session['nom'])


@app.route('/recupNote', methods = ['GET', 'POST'])
def recupNote():
    if request.method=='GET':
        note = request.args['note']
    else :
        note = request.form['note']
    
    codeCli=session['codeCli']
    codeB = session.get('codeB')  # Récupérez le code du bien à partir de la session
   
    verif_deja_note='''
                SELECT *
                FROM NOTER
                WHERE CodeCLI = ?
                AND CodeB = ?
            '''
    connection = connect()
    cursor= connection.cursor()
    cursor.execute(verif_deja_note,(codeCli, codeB,))
    verif_noter=cursor.fetchone()
    connection.close()

    if verif_noter is not None :
        session['msg_noter']='Vous avez déjà noté ce bien auparavant !'
        return redirect(url_for('connection'))
    else :

    

    # Insérez la note dans la table noter
        connection = connect()
        insertNoter = f"""INSERT INTO noter VALUES ({note}, {codeCli}, {codeB})"""
        cursor= connection.cursor()
        cursor.execute(insertNoter)
        connection.commit()
        connection.close()

        session['msg_note']='Votre note a été enregistrée avec succès ! En espérant vous revoir très bientôt !'
        return redirect(url_for('connection'))


# Sel utilisé pour cacher le mdp
salt = "nvjrbivbreohfoirnrzefzb"

def hash_password(mdp, salt):

    salted_password = mdp + salt

    hashed_password = hashlib.sha256(salted_password.encode()).hexdigest()

    return hashed_password
    
@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if 'message' in session:
        message=session.pop('message')
        return render_template('inscription.html', message=message)
    else : 
        return render_template('inscription.html')


@app.route('/confirmation_inscription', methods=['GET', 'POST'])
def confirmation_inscription():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        nom = request.form['nom']
        prenom = request.form['prenom']
        tel = request.form['tele']
    else :
        email = request.args['email']
        password = request.args['password']
        nom = request.args['nom']
        prenom = request.args['prenom']
        tel = request.args['tele']
    connection = connect()
    verif_mail='''
            SELECT * from client 
            WHERE mailcli= ?
            '''
    cursor = connection.cursor()
    cursor.execute(verif_mail,(f"{email}",))
    verf= cursor.fetchone()
    print(f" AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA : {verf}")
    
    if verf is not None :
        session['message'] = "Un client est déjà inscrit avec cet email"
        return redirect(url_for('inscription'))
    
    else :      
        nomc=f"{prenom} {nom}"
        mdp=hash_password(password, salt)

        query = '''
        select max(codecli) from client 
        '''
        connection = connect()
        codec = execute_requete(connection, query)[1][0][0] + 1

        connection = connect()

        requete = """insert into client (codeCli, NomCli, TelCli, MailCli, MDP) values(?,?,?,?,?)"""
        cursor = connection.cursor()
        cursor.execute(requete, (codec, nomc, tel, email, mdp))
        connection.commit()

        cursor.close()
        connection.close()          
        session['mes']="Félicitation, votre inscription est confirmée ! Vous pouvez maintenant vous connecter : "
       
        return redirect(url_for('connection'))

    
    
   


@app.route('/connection', methods=['GET', 'POST'])
def connection():
    if 'codeB' in session :
        session.pop('codeB')
    if 'codeCli' in session :
        session.pop('codeCli')
    if 'email' in session :
        session.pop('email')
    if 'lignes_autres_suggestions' in session :
        session.pop('lignes_autres_suggestions')
    if 'nom' in session :
        session.pop('nom')
    if 'quartier' in session :
        session.pop('quartier')

    if 'msg_noter' in session :
        msg_noter=session.pop('msg_noter')
        return render_template('connection.html', msg_noter=msg_noter)
    if 'mes' in session :
        mes=session.pop('mes')
        return render_template('connection.html', mes=mes)
    elif 'msg_note' in session :
        msg_note=session.pop('msg_note')
        return render_template('connection.html', msg_note=msg_note)
    elif 'msg_mdp' in session :
        msg_mdp=session.pop('msg_mdp')
        return render_template('connection.html', msg_mdp=msg_mdp)
    elif 'erreur' in session :
        erreur=session.pop('erreur')
        return render_template('connection.html', erreur=erreur)
    else :
        return render_template('connection.html')


@app.route('/verif_connection', methods=['GET', 'POST'])
def verif_connection():
    if request.method == 'POST':
        email=request.form['email1']
        password=request.form['password1']
    else :
        email=request.args['email1']
        password=request.args['password1']
    print(email)
    print(password)
    print(hash_password(password,salt))
    salt_mdp=hash_password(password,salt)
    if email is not None :
        verif_client_existe='''
                            SELECT *
                            FROM CLIENT
                            WHERE MAILCLI = ?
                            '''
        connection = connect()
        cursor=connection.cursor()
        cursor.execute(verif_client_existe,(email,))
        reslt=cursor.fetchone()
        print(reslt)
        if reslt is None :
            session['erreur']= "Vous devez saisir l'email d'un participant déjà inscrit !"
            return redirect(url_for('connection'))
        else :
            verif_mdp='''
                    SELECT MDP 
                    FROM CLIENT
                    WHERE MAILCLI = ?
                '''
            cursor=connection.cursor()
            cursor.execute(verif_mdp,(email,))
            bool_mdp=cursor.fetchone()[0]
            print(bool_mdp)
            if salt_mdp==bool_mdp:
                session['email']= email
                session['nom']= reslt[1]
                return redirect(url_for('affichepage'))
            else :
                session['msg_mdp']="Veuillez saisir un mot de passe qui correspond à l'email."
                return redirect(url_for('connection'))
    else : 
        session['erreur']= "Vous devez d'abord vous connecter pour accéder à nos services !"
        return redirect(url_for('connection'))

        
import plotly.express as px


def afficher_carte():
    connection = connect()
    cursor = connection.cursor()
    
    cursor.execute("SELECT AdresseB, Prix, GPS_B FROM Bien")

    # Récupération des résultats de la requête
    rows = cursor.fetchall()

 

    # Création d'un DataFrame pandas à partir des résultats
    df_bien = pd.DataFrame(rows, columns=['AdresseB', 'Prix', 'GPS_B'])

    # Supprimer les lignes avec des coordonnées GPS vides
    df_bien = df_bien.dropna(subset=['GPS_B'])
    df_bien = df_bien[df_bien['GPS_B'] != '']  # Supprimer les valeurs vides dans la colonne GPS_B

    # Diviser la colonne GPS_B en Latitude et Longitude
    df_bien[['Longitude', 'Latitude']] = df_bien['GPS_B'].str.split(';', expand=True)

    # Supprimer les lignes avec des valeurs vides dans la colonne Latitude
    df_bien = df_bien.dropna(subset=['Latitude'])
    df_bien = df_bien[df_bien['Latitude'] != '']

    # Nettoyer les valeurs de Latitude et Longitude
    df_bien['Latitude'] = pd.to_numeric(df_bien['Latitude'], errors='coerce')
    df_bien['Longitude'] = pd.to_numeric(df_bien['Longitude'], errors='coerce')

    # Supprimer les lignes avec des valeurs non numériques dans Latitude et Longitude
    df_bien = df_bien.dropna(subset=['Latitude', 'Longitude'])
    print(df_bien.columns)

     # Calcul de la moyenne des prix
    moyenne_prix = df_bien['Prix'].mean()

    # Définir les bornes inférieure et supérieure pour la coloration en orange
    borne_inferieure = moyenne_prix - 50000
    borne_superieure = moyenne_prix + 50000
    # Coordonnées de Toulouse
    latitude_toulouse = 43.6045
    longitude_toulouse = 1.4442

    # Niveau de zoom initial
    zoom_level = 11

    # Colorer les points en rouge si le prix est supérieur à la moyenne
    df_bien.loc[df_bien['Prix'] > moyenne_prix, 'Prix du bien'] = 'Prix élevé'

    # Colorer les points en vert si le prix est inférieur à la moyenne
    df_bien.loc[df_bien['Prix'] < moyenne_prix, 'Prix du bien'] = 'Prix bas'

    # Colorer les points en orange si le prix est entre moyenne-50000 et moyenne+50000
    df_bien.loc[(df_bien['Prix'] >= borne_inferieure) & (df_bien['Prix'] <= borne_superieure), 'Prix du bien'] = 'Prix moyen'
    print(df_bien)
    # Créer la carte avec les points colorés
    fig = px.scatter_mapbox(df_bien, lat="Latitude", lon="Longitude", hover_name="AdresseB", hover_data=["Prix"],
                            color="Prix du bien", color_discrete_map={'Prix élevé': 'red', 'Prix bas': 'green', 'Prix moyen': 'orange'})

    # Personnaliser la carte
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(mapbox_center={"lat": latitude_toulouse, "lon": longitude_toulouse})
    fig.update_layout(mapbox_zoom=zoom_level)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # Afficher uniquement l'adresse et le prix du bien lorsque vous passez la souris sur un point
    fig.update_traces(hovertemplate="<b>Adresse:</b> %{hovertext}<br><b>Prix:</b> %{customdata[0]:.2f} €")
    # Définition des limites de la carte pour qu'elle soit carrée et délimitée à Toulouse
    lat_diff = 0.1
    lon_diff = 0.1
    fig.update_geos(fitbounds="locations", visible=False, lataxis_range=[latitude_toulouse - lat_diff, latitude_toulouse + lat_diff],
                    lonaxis_range=[longitude_toulouse - lon_diff, longitude_toulouse + lon_diff])

    
    # Afficher la carte
    carte_html = fig.to_html()

    # Renvoyer le modèle HTML rendu
    return carte_html








def afficher_carte_quartier_nbHab():
    connection = connect()
    cursor = connection.cursor()
    
    cursor.execute('''select q.nomq, InfoQuartier.nbhab , q.gps_q
                   from quartier q, InfoQuartier, Caractériser
                   where q.codeq = Caractériser.codeq
                   and InfoQuartier.codeInfo=Caractériser.codeinfo''')

    # Récupération des résultats de la requête
    rows = cursor.fetchall()

 

    # Création d'un DataFrame pandas à partir des résultats
    df_hab = pd.DataFrame(rows, columns=['NomQ', 'NbHab', 'GPS_Q'])

    # Supprimer les lignes avec des coordonnées GPS vides
    df_hab = df_hab.dropna(subset=['GPS_Q'])
    df_hab = df_hab[df_hab['GPS_Q'] != '']  # Supprimer les valeurs vides dans la colonne GPS_B

    # Diviser la colonne GPS_Q en Latitude et Longitude en détectant le séparateur
    df_hab[['Latitude', 'Longitude']] = df_hab['GPS_Q'].apply(lambda x: pd.Series(x.split(';') if ';' in x else x.split(',')))


    # Supprimer les lignes avec des valeurs vides dans la colonne Latitude
    df_hab = df_hab.dropna(subset=['Latitude'])
    df_hab = df_hab[df_hab['Latitude'] != '']

    # Nettoyer les valeurs de Latitude et Longitude
    df_hab['Latitude'] = pd.to_numeric(df_hab['Latitude'], errors='coerce')
    df_hab['Longitude'] = pd.to_numeric(df_hab['Longitude'], errors='coerce')

    # Supprimer les lignes avec des valeurs non numériques dans Latitude et Longitude
    df_hab = df_hab.dropna(subset=['Latitude', 'Longitude'])
    

     # Calcul de la moyenne des prix
    moyenne_nbhab = df_hab['NbHab'].mean()
    print(moyenne_nbhab)

    # Définir les bornes inférieure et supérieure pour la coloration en orange
    borne_inferieure = moyenne_nbhab - 3000
    borne_superieure = moyenne_nbhab + 3000
    # Coordonnées de Toulouse
    latitude_toulouse = 43.6045
    longitude_toulouse = 1.4442

    # Niveau de zoom initial
    zoom_level = 11

    # Colorer les points en rouge si le prix est supérieur à la moyenne
    df_hab.loc[df_hab['NbHab'] > moyenne_nbhab, "Nombre d'habitants"] = "Nombre élevé d'habitants"

    # Colorer les points en vert si le prix est inférieur à la moyenne
    df_hab.loc[df_hab['NbHab'] < moyenne_nbhab, "Nombre d'habitants"] = "Nombre bas d'habitants"

    # Colorer les points en orange si le prix est entre moyenne-50000 et moyenne+50000
    df_hab.loc[(df_hab['NbHab'] >= borne_inferieure) & (df_hab['NbHab'] <= borne_superieure), "Nombre d'habitants"] = "Nombre d'habitants moyen"
    print(df_hab)
    # Créer la carte avec les points colorés
    fig = px.scatter_mapbox(df_hab, lat="Latitude", lon="Longitude", hover_name="NomQ", hover_data=["NbHab"],
                            color="Nombre d'habitants", color_discrete_map={"Nombre élevé d'habitants": 'red', "Nombre bas d'habitants": 'green', "Nombre d'habitants moyen": 'blue'})

    # Personnaliser la carte
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(mapbox_center={"lat": latitude_toulouse, "lon": longitude_toulouse})
    fig.update_layout(mapbox_zoom=zoom_level)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # Afficher uniquement l'adresse et le prix du bien lorsque vous passez la souris sur un point
    fig.update_traces(hovertemplate="<b>NomQ:</b> %{hovertext}<br><b>NbHab:</b> %{customdata[0]:.2f}")
    # Définition des limites de la carte pour qu'elle soit carrée et délimitée à Toulouse
    lat_diff = 0.1
    lon_diff = 0.1
    fig.update_geos(fitbounds="locations", visible=False, lataxis_range=[latitude_toulouse - lat_diff, latitude_toulouse + lat_diff],
                    lonaxis_range=[longitude_toulouse - lon_diff, longitude_toulouse + lon_diff])

    
    # Afficher la carte
    carte_html = fig.to_html()

    # Renvoyer le modèle HTML rendu
    return carte_html




def afficher_carte_quartier_resto():
    connection = connect()
    cursor = connection.cursor()
    
    cursor.execute('''select q.nomq, InfoQuartier.nbresto , q.gps_q
                   from quartier q, InfoQuartier, Caractériser
                   where q.codeq = Caractériser.codeq
                   and InfoQuartier.codeInfo=Caractériser.codeinfo''')

    # Récupération des résultats de la requête
    rows = cursor.fetchall()

 

    # Création d'un DataFrame pandas à partir des résultats
    df_hab = pd.DataFrame(rows, columns=['NomQ', 'NbResto', 'GPS_Q'])

    # Supprimer les lignes avec des coordonnées GPS vides
    df_hab = df_hab.dropna(subset=['GPS_Q'])
    df_hab = df_hab[df_hab['GPS_Q'] != '']  # Supprimer les valeurs vides dans la colonne GPS_B

    # Diviser la colonne GPS_Q en Latitude et Longitude en détectant le séparateur
    df_hab[['Latitude', 'Longitude']] = df_hab['GPS_Q'].apply(lambda x: pd.Series(x.split(';') if ';' in x else x.split(',')))


    # Supprimer les lignes avec des valeurs vides dans la colonne Latitude
    df_hab = df_hab.dropna(subset=['Latitude'])
    df_hab = df_hab[df_hab['Latitude'] != '']

    # Nettoyer les valeurs de Latitude et Longitude
    df_hab['Latitude'] = pd.to_numeric(df_hab['Latitude'], errors='coerce')
    df_hab['Longitude'] = pd.to_numeric(df_hab['Longitude'], errors='coerce')

    # Supprimer les lignes avec des valeurs non numériques dans Latitude et Longitude
    df_hab = df_hab.dropna(subset=['Latitude', 'Longitude'])
    

     # Calcul de la moyenne des prix
    moyenne_nbhab = df_hab['NbResto'].mean()
    print(moyenne_nbhab)

    # Définir les bornes inférieure et supérieure pour la coloration en orange
    borne_inferieure = moyenne_nbhab - 5
    borne_superieure = moyenne_nbhab + 5
    # Coordonnées de Toulouse
    latitude_toulouse = 43.6045
    longitude_toulouse = 1.4442

    # Niveau de zoom initial
    zoom_level = 11

    # Colorer les points en rouge si le prix est supérieur à la moyenne
    df_hab.loc[df_hab['NbResto'] > moyenne_nbhab, "Nombre de restaurants"] = "Nombre de restaurants élevé"

    # Colorer les points en vert si le prix est inférieur à la moyenne
    df_hab.loc[df_hab['NbResto'] < moyenne_nbhab, "Nombre de restaurants"] = "Nombre de restaurants bas"

    # Colorer les points en orange si le prix est entre moyenne-50000 et moyenne+50000
    df_hab.loc[(df_hab['NbResto'] >= borne_inferieure) & (df_hab['NbResto'] <= borne_superieure), "Nombre de restaurants"] = "Nombre de restaurants moyen"
    print(df_hab)
    # Créer la carte avec les points colorés
    fig = px.scatter_mapbox(df_hab, lat="Latitude", lon="Longitude", hover_name="NomQ", hover_data=["NbResto"],
                            color="Nombre de restaurants", color_discrete_map={"Nombre de restaurants élevé": 'red', "Nombre de restaurants bas": 'green', "Nombre de restaurants moyen": 'blue'})

    # Personnaliser la carte
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(mapbox_center={"lat": latitude_toulouse, "lon": longitude_toulouse})
    fig.update_layout(mapbox_zoom=zoom_level)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # Afficher uniquement l'adresse et le prix du bien lorsque vous passez la souris sur un point
    fig.update_traces(hovertemplate="<b>NomQ:</b> %{hovertext}<br><b>NbResto:</b> %{customdata[0]:.2f}")
    # Définition des limites de la carte pour qu'elle soit carrée et délimitée à Toulouse
    lat_diff = 0.1
    lon_diff = 0.1
    fig.update_geos(fitbounds="locations", visible=False, lataxis_range=[latitude_toulouse - lat_diff, latitude_toulouse + lat_diff],
                    lonaxis_range=[longitude_toulouse - lon_diff, longitude_toulouse + lon_diff])

    
    # Afficher la carte
    carte_html = fig.to_html()

    # Renvoyer le modèle HTML rendu
    return carte_html



def afficher_carte_quartier_nbPolice():
    connection = connect()
    cursor = connection.cursor()
    
    cursor.execute('''select q.nomq, InfoQuartier.nbPolice , q.gps_q
                   from quartier q, InfoQuartier, Caractériser
                   where q.codeq = Caractériser.codeq
                   and InfoQuartier.codeInfo=Caractériser.codeinfo''')

    # Récupération des résultats de la requête
    rows = cursor.fetchall()

 

    # Création d'un DataFrame pandas à partir des résultats
    df_police = pd.DataFrame(rows, columns=['NomQ', 'nbPolice', 'GPS_Q'])

    # Supprimer les lignes avec des coordonnées GPS vides
    df_police = df_police.dropna(subset=['GPS_Q'])
    df_police = df_police[df_police['GPS_Q'] != '']  # Supprimer les valeurs vides dans la colonne GPS_B

    # Diviser la colonne GPS_Q en Latitude et Longitude en détectant le séparateur
    df_police[['Latitude', 'Longitude']] = df_police['GPS_Q'].apply(lambda x: pd.Series(x.split(';') if ';' in x else x.split(',')))


    # Supprimer les lignes avec des valeurs vides dans la colonne Latitude
    df_police = df_police.dropna(subset=['Latitude'])
    df_police = df_police[df_police['Latitude'] != '']

    # Nettoyer les valeurs de Latitude et Longitude
    df_police['Latitude'] = pd.to_numeric(df_police['Latitude'], errors='coerce')
    df_police['Longitude'] = pd.to_numeric(df_police['Longitude'], errors='coerce')

    # Supprimer les lignes avec des valeurs non numériques dans Latitude et Longitude
    df_police = df_police.dropna(subset=['Latitude', 'Longitude'])
    

     # Calcul de la moyenne des prix
    moyenne_nbPolice = 1
    print(moyenne_nbPolice)

    # Définir les bornes inférieure et supérieure pour la coloration en orange
    borne_inferieure = moyenne_nbPolice
    borne_superieure = moyenne_nbPolice
    # Coordonnées de Toulouse
    latitude_toulouse = 43.6045
    longitude_toulouse = 1.4442

    # Niveau de zoom initial
    zoom_level = 11

    # Colorer les points en rouge si le prix est supérieur à la moyenne
    df_police.loc[df_police['nbPolice'] == moyenne_nbPolice, "Quartier"] = "Quartiers possédant des commissariats"

    # Colorer les points en vert si le prix est inférieur à la moyenne
    df_police.loc[df_police['nbPolice'] < moyenne_nbPolice, "Quartier"] = "Quartiers sans commissariat"

    print(df_police)
    # Créer la carte avec les points colorés
    fig = px.scatter_mapbox(df_police, lat="Latitude", lon="Longitude", hover_name="NomQ", hover_data=["nbPolice"],
                            color="Quartier", color_discrete_map={"Quartiers possédant des commissariats": 'green', "Quartiers sans commissariat": 'red'})

    # Personnaliser la carte
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(mapbox_center={"lat": latitude_toulouse, "lon": longitude_toulouse})
    fig.update_layout(mapbox_zoom=zoom_level)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # Afficher uniquement l'adresse et le prix du bien lorsque vous passez la souris sur un point
    fig.update_traces(hovertemplate="<b>NomQ:</b> %{hovertext}<br><b>nbPolice:</b> %{customdata[0]:.2f}")
    # Définition des limites de la carte pour qu'elle soit carrée et délimitée à Toulouse
    lat_diff = 0.1
    lon_diff = 0.1
    fig.update_geos(fitbounds="locations", visible=False, lataxis_range=[latitude_toulouse - lat_diff, latitude_toulouse + lat_diff],
                    lonaxis_range=[longitude_toulouse - lon_diff, longitude_toulouse + lon_diff])

    
    # Afficher la carte
    carte_html = fig.to_html()

    # Renvoyer le modèle HTML rendu
    return carte_html