# Importations
import os
import csv
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import re
import shutil

# Définir le chemin vers liste.csv
liste_path = os.path.join(os.path.dirname(__file__), '../database/liste.csv')

# Sauvegarder une copie avant d'écrire
shutil.copy(liste_path, f"{liste_path}.backup")

# Constantes globales
CSV_FILE = os.path.join(os.path.dirname(__file__), "../database/scraping.csv")
HTML_FOLDER = os.path.join(os.path.dirname(__file__), "html_pages")
os.makedirs(HTML_FOLDER, exist_ok=True)

# URLs des pages à scraper
urls = {
    #FDCA
    "FDCA_Droit allemand (étudiants réguliers) - Printemps": "https://applicationspub.unil.ch/interpub/noauth/php/Ud/listeCours.php?v_ueid=5&v_semposselected=170&v_langue=fr&v_isinterne=&v_etapeid1=797",
    "FDCA_Droit allemand (étudiants réguliers) - Automne": "https://applicationspub.unil.ch/interpub/noauth/php/Ud/listeCours.php?v_ueid=5&v_semposselected=171&v_langue=fr&v_isinterne=&v_etapeid1=797",
    #SSP
    "SSP_Bachelor_1ère_partie_Automne": "https://applicationspub.unil.ch/interpub/noauth/php/Ud/listeCours.php?v_ueid=171&v_semposselected=169&v_langue=fr&v_isinterne=&v_etapeid1=32348"
}

# Fonctions utilitaires
def normalize_faculty(faculty_name):
    """ Normalise les noms des facultés en abréviations. """
    mapping = {
        "Faculté des sciences sociales et politiques": "SSP",
        "Faculté de théologie et de sciences des religions": "FTSR",
        "Faculté de droit, des sciences criminelles et d'administration publique": "FDCA",
        "Ecole des sciences criminelles": "ESC",
        "Institut de hautes études en administration publique": "IDHEAP",
        "Faculté des lettres": "LETTRES",
        "Faculté des hautes études commerciales": "HEC",
        "Ecole de biologie": "FBM-BIO",
        "Ecole de médecine": "FBM-MED",
        "Faculté des géosciences et de l'environnement": "FGSE",
        "Sciences au carré": "SCIENCES²",
    }
    return mapping.get(faculty_name, faculty_name)

def extract_semester(soup):
    """Extrait le semestre depuis une page HTML."""
    semesters = set()
    for elem in soup.find_all(["table", "p", "h3"]):
        text = elem.get_text(separator=" ").strip().lower()
        if "printemps" in text:
            semesters.add("Printemps")
        if "automne" in text:
            semesters.add("Automne")
        if "annuel" in text:
            semesters.add("Annuel")

    if "Annuel" in semesters:
        return "Annuel"
    elif "Printemps" in semesters and "Automne" in semesters:
        return "Annuel"
    elif "Printemps" in semesters:
        return "Printemps"
    elif "Automne" in semesters:
        return "Automne"
    return "Inconnu"

def extract_course_info(soup):
    """Extrait les informations d'un cours depuis une page HTML."""
    try:
        course_info = {
            'Faculté': "Inconnu",
            'Semestre': "Inconnu",
            'Crédits': "Inconnu",
            'Nom': "Inconnu",
            'Professeur': "Inconnu"
        }

        # Nom du cours
        title = soup.find('h2')
        if title:
            course_info['Nom'] = title.text.strip()

        # Faculté
        faculty = soup.find('h4')
        if faculty:
            text = faculty.text.strip()
            if "Faculté de gestion: " in text:
                faculty_name = text.split(": ")[1].split(" (")[0]
                course_info['Faculté'] = normalize_faculty(faculty_name)

        # Professeur
        prof = soup.find(string=lambda text: "Responsable(s):" in text)
        if prof:
            course_info['Professeur'] = prof.split(":")[-1].strip()
        # Extraction du semestre
        course_info['Semestre'] = extract_semester(soup)

        # Recherche des crédits
        utilisation_table = soup.find_all("table", class_="resultats")
        for table in utilisation_table:
            for row in table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) >= 4:
                    credits_value = cells[-1].get_text().strip()
                    if credits_value.replace('.', '', 1).isdigit():
                        course_info['Crédits'] = credits_value
                        break
            # Si une valeur valide a été trouvée, sortir de la boucle principale
            if course_info['Crédits'] != "Inconnu":
                break

        # Si aucun crédit valide n'a été trouvé, remplacer "Inconnu" par "0.00"
        if course_info['Crédits'] == "Inconnu":
            course_info['Crédits'] = "0.00"

        return course_info
    except Exception as e:
        print(f"Erreur lors de l'extraction des informations : {e}")
        return None

def extract_links_from_html(file_path):
    """Extrait les liens des fiches de cours depuis un fichier HTML."""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            content = file.read()

        soup = BeautifulSoup(content, 'html.parser')
        links = []
        base_url = "https://applicationspub.unil.ch"
        for a in soup.find_all('a', onclick=True):
            onclick_content = a['onclick']
            if "window.open" in onclick_content:
                start = onclick_content.find("('") + 2
                end = onclick_content.find("','")
                relative_url = onclick_content[start:end]
                full_url = f"{base_url}{relative_url}" if relative_url.startswith("/interpub/noauth/php/Ud/") else f"{base_url}/interpub/noauth/php/Ud/{relative_url}"
                links.append(full_url)
        return links
    except Exception as e:
        print(f"Erreur lors de l'extraction des liens : {e}")
        return []

def get_page_title(soup, name):
    """Extrait le titre pertinent depuis la page HTML."""
    title_tag = soup.find('h2')
    if title_tag:
        title = title_tag.text.strip()
        if title == "Votre sélection":
            title = name
        return title.replace(" ", "_").replace("/", "_")
    return name

def update_html_file(name, url):
    """Télécharge la page HTML d'une liste de cours et nomme le fichier."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Normaliser le nom de la faculté
        faculty_name = normalize_faculty(name.split(" - ")[0])  # Extraire et normaliser la faculté
        
        # Nommer le fichier avec le nom normalisé de la faculté
        file_name = f"{name}.html"
        file_path = os.path.join(HTML_FOLDER, file_name)
        
        with open(file_path, 'w', encoding='utf-8-sig') as file:
            file.write(response.text)
        print(f"Mise à jour du fichier HTML pour {name} réussie sous le nom : {file_name}")
    except Exception as e:
        print(f"Erreur lors de la mise à jour du fichier HTML pour {name} : {e}")

def check_html_update():
    """Vérifie si les fichiers HTML doivent être mis à jour."""
    for name, url in urls.items():
        # Extraire et normaliser le nom de la faculté
        faculty_name = normalize_faculty(name.split(" - ")[0])  # Correction ici
        
        # Construire le chemin du fichier avec le nom normalisé de la faculté
        file_path = os.path.join(HTML_FOLDER, f"{name}.html")
        
        if os.path.exists(file_path):
            last_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
            today = datetime.now()
            if (today - last_modified).days > 180:
                print(f"Le fichier HTML {name} est obsolète. Mise à jour en cours...")
                update_html_file(name, url)
            else:
                print(f"Pas besoin de mise à jour pour {name}.")
        else:
            print(f"Le fichier HTML {name} n'existe pas. Téléchargement en cours...")
            update_html_file(name, url)

def remove_duplicates():
    """Supprime les doublons dans le fichier scraping.csv en combinant les noms des professeurs et en supprimant les doublons dans une même ligne."""
    if not os.path.exists(CSV_FILE):
        print(f"Le fichier {CSV_FILE} n'existe pas. Impossible de supprimer les doublons.")
        return

    # Charger les données du fichier scraping.csv
    with open(CSV_FILE, newline='', encoding='utf-8-sig') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=';')
        data = list(reader)

    # Utiliser un dictionnaire pour regrouper les cours uniques
    unique_courses = {}
    for row in data:
        key = (row['Semestre'], row['Crédits'], row['Nom'])
        if key in unique_courses:
            # Ajouter le professeur à la liste existante s'il n'est pas déjà présent
            existing_professors = set(unique_courses[key]['Professeur'].split(', '))
            new_professor = row['Professeur']
            if new_professor not in existing_professors:
                existing_professors.add(new_professor)
                unique_courses[key]['Professeur'] = ', '.join(sorted(existing_professors))
        else:
            # Ajouter une nouvelle entrée pour ce cours
            unique_courses[key] = row

    # Supprimer les doublons dans les noms des professeurs pour chaque cours
    for course in unique_courses.values():
        professors = course['Professeur'].split(', ')
        unique_professors = sorted(set(professors))
        course['Professeur'] = ', '.join(unique_professors)

    # Écrire les données uniques dans le fichier scraping.csv
    with open(CSV_FILE, 'w', newline='', encoding='utf-8-sig') as csv_file:
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(unique_courses.values())

    print(f"Les doublons ont été supprimés et le fichier {CSV_FILE} a été mis à jour.")

def verify_professor_names():
    """Vérifie que les noms des professeurs ne se répètent pas dans une même ligne du fichier liste.csv."""
    liste_path = os.path.join(os.path.dirname(__file__), '../database/liste.csv')

    if not os.path.exists(liste_path):
        print(f"Le fichier {liste_path} n'existe pas. Impossible de vérifier les noms des professeurs.")
        return

    # Charger les données du fichier liste.csv
    with open(liste_path, newline='', encoding='utf-8-sig') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=';')
        data = list(reader)

    # Vérifier les noms des professeurs
    for row in data:
        professors = row['Professeur'].split(', ')
        unique_professors = set(professors)
        if len(professors) != len(unique_professors):
            print(f"Doublon trouvé dans la ligne : {row}")

    print("Vérification des noms des professeurs terminée.")

# Fonctions principales
def download_html():
    """Télécharge les pages principales listant les cours."""
    for name, url in urls.items():
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            title = get_page_title(soup, name)
            file_path = os.path.join(HTML_FOLDER, f"{title}.html")
            with open(file_path, "w", encoding="utf-8-sig") as file:
                file.write(response.text)
            print(f"Téléchargé : {file_path}")
        else:
            print(f"Erreur lors du téléchargement de {url} : {response.status_code}")

def synchronize_files():
    """Synchronise les fichiers scraping.csv et liste.csv."""
    scraping_path = os.path.join(os.path.dirname(__file__), '../database/scraping.csv')
    liste_path = os.path.join(os.path.dirname(__file__), '../database/liste.csv')

    # Charger les fichiers CSV
    scraping_data = {}
    with open(scraping_path, mode='r', encoding='utf-8-sig') as scraping_file:
        reader = csv.DictReader(scraping_file, delimiter=';')
        for row in reader:
            scraping_data[row['Nom']] = {
                'credits': row.get('Crédits', '0.00'),
                'semestre': row.get('Semestre', 'N/A'),
                'prof': row.get('Professeur', 'VACAT')
            }

    updated_rows = []
    with open(liste_path, mode='r', encoding='utf-8-sig') as liste_file:
        reader = csv.DictReader(liste_file, delimiter=';')
        fieldnames = reader.fieldnames
        for row in reader:
            nom_cours = row['Nom']
            if nom_cours in scraping_data:
                row['Crédits'] = scraping_data[nom_cours]['credits']
                row['Semestre'] = scraping_data[nom_cours]['semestre']
                row['Professeur'] = scraping_data[nom_cours]['prof']
            else:
                row['Crédits'] = '0.00'
                row['Semestre'] = 'N/A'
                row['Professeur'] = 'VACAT'
            updated_rows.append(row)

    # Écrire les données mises à jour dans liste.csv
    with open(liste_path, mode='w', encoding='utf-8-sig', newline='') as liste_file:
        writer = csv.DictWriter(liste_file, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(updated_rows)

    print("Synchronisation entre scraping.csv et liste.csv terminée.")

# Ajout des fonctions pour gérer l'exportation des professeurs et la recherche de leurs liens professionnels
def exporter_professeurs(cours):
    """Exporte une liste unique de professeurs dans professeurs.csv."""
    chemin_fichier = os.path.join(os.path.dirname(__file__), "../database/professeurs.csv")
    professeurs = set()

    # Extraire les noms des professeurs uniques
    for cours_info in cours:
        if 'Professeur' in cours_info and cours_info['Professeur']:
            noms = [nom.strip() for nom in cours_info['Professeur'].split(',')]
            professeurs.update(noms)

    # Écrire dans le fichier CSV
    try:
        with open(chemin_fichier, mode='w', encoding='utf-8-sig', newline='') as fichier:
            writer = csv.writer(fichier)
            writer.writerow(["Professeur", "Lien_Professeur"])
            for professeur in sorted(professeurs):
                writer.writerow([professeur, ""])
        print(f"Liste des professeurs exportée dans {chemin_fichier}")
    except Exception as e:
        print(f"Erreur lors de l'exportation des professeurs : {e}")

def mettre_a_jour_liens_professeurs():
    """Met à jour les liens des professeurs dans professeurs.csv."""
    chemin_fichier = os.path.join(os.path.dirname(__file__), "../database/professeurs.csv")
    base_url = "https://applicationspub.unil.ch/interpub/noauth/php/Un/UnIndex.php?list=pers&LanCode=37"

    try:
        # Lire le fichier existant
        with open(chemin_fichier, mode='r', encoding='utf-8-sig') as fichier:
            lecteur_csv = csv.DictReader(fichier)
            lignes = list(lecteur_csv)

        # Envoyer une requête pour récupérer la page complète
        response = requests.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Parcourir chaque professeur dans le fichier CSV
        for ligne in lignes:
            professeur = ligne['Professeur']
            if not ligne['Lien_Professeur'] or ligne['Lien_Professeur'] == "Non trouvé":
                print(f"Recherche du lien pour : {professeur}")
                # Rechercher le lien correspondant au nom du professeur
                lien = None
                for a_tag in soup.find_all('a', href=True):
                    if professeur.lower() in a_tag.text.lower():
                        lien = a_tag['href']
                        break

                # Mettre à jour le lien dans la ligne
                ligne['Lien_Professeur'] = lien if lien else "Non trouvé"

        # Écrire les mises à jour dans le fichier
        with open(chemin_fichier, mode='w', encoding='utf-8-sig', newline='') as fichier:
            writer = csv.DictWriter(fichier, fieldnames=["Professeur", "Lien_Professeur"])
            writer.writeheader()
            writer.writerows(lignes)
        print(f"Liens des professeurs mis à jour dans {chemin_fichier}")

    except Exception as e:
        print(f"Erreur lors de la mise à jour des liens des professeurs : {e}")

def update_professors_html():
    """Télécharge ou met à jour la page HTML des professeurs si elle a changé."""
    html_file_path = os.path.join(HTML_FOLDER, "professeurs.html")
    url = "https://applicationspub.unil.ch/interpub/noauth/php/Un/UnIndex.php?list=pers&LanCode=37"

    try:
        # Télécharger la page en ligne
        response = requests.get(url)
        response.raise_for_status()
        online_content = response.text

        # Vérifier si le fichier local existe
        if os.path.exists(html_file_path):
            with open(html_file_path, 'r', encoding='utf-8-sig') as local_file:
                local_content = local_file.read()

            # Comparer le contenu local avec le contenu en ligne
            if local_content == online_content:
                print("La page HTML des professeurs est déjà à jour.")
                return

        # Mettre à jour ou créer le fichier local
        with open(html_file_path, 'w', encoding='utf-8-sig') as local_file:
            local_file.write(online_content)
        print("La page HTML des professeurs a été mise à jour.")

    except requests.RequestException as e:
        print(f"Erreur lors du téléchargement de la page des professeurs : {e}")

def normaliser_nom(nom):
    """Nettoie et normalise un nom pour comparaison."""
    return ' '.join(nom.split()).lower()

def extraire_mots(nom):
    """Extrait les mots d'un nom après nettoyage."""
    nom = re.sub(r'[^\w\s]', '', nom)  # Supprimer les caractères spéciaux
    return set(nom.split())

def pourcentage_mots_communs(mots_csv, mots_html):
    """Calcule le pourcentage de mots communs entre deux ensembles de mots."""
    communs = mots_csv.intersection(mots_html)
    total = max(len(mots_csv), len(mots_html))
    return len(communs) / total if total > 0 else 0

def scrape_professors_from_html():
    """Scrape uniquement les liens des professeurs présents dans professeurs.csv depuis la page HTML locale."""
    html_file_path = os.path.join(HTML_FOLDER, "professeurs.html")
    chemin_fichier_csv = os.path.join(os.path.dirname(__file__), "../database/professeurs.csv")
    base_url = "https://applicationspub.unil.ch"

    try:
        # Charger les noms des professeurs depuis professeurs.csv
        with open(chemin_fichier_csv, mode='r', encoding='utf-8-sig') as fichier:
            lecteur_csv = csv.DictReader(fichier)
            professeurs_csv = {ligne['Professeur'].strip(): ligne['Lien_Professeur'].strip() for ligne in lecteur_csv}

        # Lire le fichier HTML local
        with open(html_file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        # Extraire les noms et liens des professeurs depuis tous les tableaux
        professeurs_html = {}
        tableaux = soup.find_all('table')  # Trouver tous les tableaux
        for tableau in tableaux:
            for row in tableau.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 1:  # Vérifier qu'il y a au moins une colonne avec le nom et le lien
                    nom_html = cells[0].get_text(strip=True)
                    lien_partiel = cells[0].find('a', href=True)['href'] if cells[0].find('a', href=True) else None

                    if lien_partiel:
                        lien_complet = f"{base_url}{lien_partiel}"
                        professeurs_html[nom_html] = lien_complet
                        print(f"Extrait : Nom HTML = {nom_html}, Lien = {lien_complet}")

        # Mettre à jour les liens dans le fichier CSV
        professeurs_mis_a_jour = []
        seuil_pourcentage = 0.8  # Seuil de correspondance (80 % de mots communs)
        for nom_csv, lien_csv in professeurs_csv.items():
            mots_csv = extraire_mots(nom_csv)
            correspondance = None

            for nom_html, lien_html in professeurs_html.items():
                mots_html = extraire_mots(nom_html)
                pourcentage = pourcentage_mots_communs(mots_csv, mots_html)

                if pourcentage >= seuil_pourcentage:  # Correspondance basée sur les mots communs
                    correspondance = lien_html
                    break

            if correspondance:
                print(f"Correspondance trouvée : {nom_csv} -> {correspondance}")
                professeurs_mis_a_jour.append({"Professeur": nom_csv, "Lien_Professeur": correspondance})
            else:
                print(f"Aucune correspondance trouvée pour : {nom_csv}")
                professeurs_mis_a_jour.append({"Professeur": nom_csv, "Lien_Professeur": lien_csv or "Non trouvé"})

        # Écrire les résultats dans le fichier CSV
        with open(chemin_fichier_csv, mode='w', encoding='utf-8-sig', newline='') as fichier:
            writer = csv.DictWriter(fichier, fieldnames=["Professeur", "Lien_Professeur"], delimiter=';')
            writer.writeheader()
            writer.writerows(professeurs_mis_a_jour)
        print(f"Les liens des professeurs ont été mis à jour dans {chemin_fichier_csv}.")

    except Exception as e:
        print(f"Erreur lors du scraping des professeurs : {e}")
        
        # Intégration dans la fonction principale
def main():
    """Fonction principale pour scraper les données et les sauvegarder dans un fichier CSV."""
    check_html_update()
    all_courses = []

    for name in urls.keys():
        # Extraire et normaliser le nom de la faculté
        faculty_name = normalize_faculty(name.split(" - ")[0])
        
        # Construire le chemin du fichier HTML
        file_path = os.path.join(HTML_FOLDER, f"{name}.html")
        if os.path.exists(file_path):
            links = extract_links_from_html(file_path)
            print(f"Nombre de liens trouvés dans {name}: {len(links)}")

            for link in links:
                try:
                    response = requests.get(link)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                    course_info = extract_course_info(soup)
                    if course_info and course_info['Nom'] != "Votre sélection":
                        # Ajout du lien vers la fiche de cours
                        course_info['Lien'] = link
                        all_courses.append(course_info)
                except Exception as e:
                    print(f"Erreur lors de l'extraction depuis {link} : {e}")
        else:
            print(f"Erreur : fichier HTML {file_path} non trouvé.")

    if all_courses:
        try:
            keys = all_courses[0].keys()
            with open(CSV_FILE, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=keys, delimiter=';')
                writer.writeheader()
                writer.writerows(all_courses)
            print(f"Données extraites et sauvegardées dans {CSV_FILE}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des données : {e}")
    else:
        print("Aucune donnée extraite.")

    # Supprimer les doublons
    remove_duplicates()

    # Étape : Exporter la liste des professeurs
    exporter_professeurs(all_courses)

    # Étape : Mettre à jour les liens des professeurs
    mettre_a_jour_liens_professeurs()

    # Étape : Scraper les données des professeurs depuis la page HTML locale
    scrape_professors_from_html()

# Point d'entrée
if __name__ == "__main__":
    main()
    synchronize_files()
    verify_professor_names()