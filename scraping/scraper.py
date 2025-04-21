# Importations
import os
import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import pandas as pd

# Constantes globales
CSV_FILE = os.path.join(os.path.dirname(__file__), "../database/scraping.csv")
HTML_FOLDER = os.path.join(os.path.dirname(__file__), "html_pages")
os.makedirs(HTML_FOLDER, exist_ok=True)

# URLs des pages à scraper
urls = {
    #FTSR
    "FTSR_Attestation de 30 crédits ECTS (BA) en Langues de l'Orient - Automne": "https://applicationspub.unil.ch/interpub/noauth/php/Ud/listeCours.php?v_ueid=253&v_semposselected=169&v_langue=fr&v_isinterne=&v_etapeid1=33033",
    "FTSR_Attestation de 30 crédits ECTS (BA) en Langues de l'Orient - Printemps": "https://applicationspub.unil.ch/interpub/noauth/php/Ud/listeCours.php?v_ueid=253&v_semposselected=170&v_langue=fr&v_isinterne=&v_etapeid1=33033",
    "FTSR_Attestation de 60 crédits ECTS (BA) en sciences des religions (2017), 1ère année - Automne": "https://applicationspub.unil.ch/interpub/noauth/php/Ud/listeCours.php?v_ueid=253&v_semposselected=169&v_langue=fr&v_isinterne=&v_etapeid1=29963",
    "FTSR_Attestation de 60 crédits ECTS (BA) en sciences des religions (2017), 1ère année - Printemps": "https://applicationspub.unil.ch/interpub/noauth/php/Ud/listeCours.php?v_ueid=253&v_semposselected=170&v_langue=fr&v_isinterne=&v_etapeid1=29963",
    "FTSR_Attestation de 60 crédits ECTS (BA) en sciences des religions, 2ème partie - Automne": "https://applicationspub.unil.ch/interpub/noauth/php/Ud/listeCours.php?v_ueid=253&v_semposselected=169&v_langue=fr&v_isinterne=&v_etapeid1=29964",
    "FTSR_Attestation de 60 crédits ECTS (BA) en sciences des religions, 2ème partie - Printemps": "https://applicationspub.unil.ch/interpub/noauth/php/Ud/listeCours.php?v_ueid=253&v_semposselected=170&v_langue=fr&v_isinterne=&v_etapeid1=29964",
    "FTSR_Baccalauréat universitaire en sciences des religions (2017), 1ère année - Automne": "https://applicationspub.unil.ch/interpub/noauth/php/Ud/listeCours.php?v_ueid=253&v_semposselected=169&v_langue=fr&v_isinterne=&v_etapeid1=29959",
    "FTSR_Baccalauréat universitaire en sciences des religions (2017), 1ère année - Printemps": "https://applicationspub.unil.ch/interpub/noauth/php/Ud/listeCours.php?v_ueid=253&v_semposselected=170&v_langue=fr&v_isinterne=&v_etapeid1=29959",
    "FTSR_Baccalauréat universitaire en sciences des religions (2017), 2ème partie - Automne": "https://applicationspub.unil.ch/interpub/noauth/php/Ud/listeCours.php?v_ueid=253&v_semposselected=169&v_langue=fr&v_isinterne=&v_etapeid1=29960",
    "FTSR_Baccalauréat universitaire en sciences des religions (2017), 2ème partie - Printemps": "https://applicationspub.unil.ch/interpub/noauth/php/Ud/listeCours.php?v_ueid=253&v_semposselected=170&v_langue=fr&v_isinterne=&v_etapeid1=29960",
    "FTSR_Préalable à la Maîtrise universitaire en Sciences des religions (2017) - Automne": "https://applicationspub.unil.ch/interpub/noauth/php/Ud/listeCours.php?v_ueid=253&v_semposselected=169&v_langue=fr&v_isinterne=&v_etapeid1=30339",
    "FTSR_Préalable à la Maîtrise universitaire en Sciences des religions (2017) - Printemps": "https://applicationspub.unil.ch/interpub/noauth/php/Ud/listeCours.php?v_ueid=253&v_semposselected=170&v_langue=fr&v_isinterne=&v_etapeid1=30339",
    "FTSR_Programme de spécialisation «Histoire de l'Islam» (Master en sciences des religions) - Automne": "https://applicationspub.unil.ch/interpub/noauth/php/Ud/listeCours.php?v_ueid=253&v_semposselected=169&v_langue=fr&v_isinterne=&v_etapeid1=34855",
    "FTSR_Programme de spécialisation «Histoire de l'Islam» (Master en sciences des religions) - Printemps": "https://applicationspub.unil.ch/interpub/noauth/php/Ud/listeCours.php?v_ueid=253&v_semposselected=170&v_langue=fr&v_isinterne=&v_etapeid1=34855",
    "FTSR_Programme de spécialisation «Eclairer l'interculturalité» (Master en sciences des religions) - Automne": "https://applicationspub.unil.ch/interpub/noauth/php/Ud/listeCours.php?v_ueid=253&v_semposselected=169&v_langue=fr&v_isinterne=&v_etapeid1=31011",
    "FTSR_Programme de spécialisation «Eclairer l'interculturalité» (Master en sciences des religions) - Printemps": "https://applicationspub.unil.ch/interpub/noauth/php/Ud/listeCours.php?v_ueid=253&v_semposselected=170&v_langue=fr&v_isinterne=&v_etapeid1=31011",
    "FTSR_Attestation 30 crédits ECTS (MA) en sciences des religions - Automne": "https://applicationspub.unil.ch/interpub/noauth/php/Ud/listeCours.php?v_ueid=253&v_semposselected=169&v_langue=fr&v_isinterne=&v_etapeid1=28098",
    "FTSR_Attestation 30 crédits ECTS (MA) en sciences des religions - Printemps": "https://applicationspub.unil.ch/interpub/noauth/php/Ud/listeCours.php?v_ueid=253&v_semposselected=170&v_langue=fr&v_isinterne=&v_etapeid1=28098",
    "FTSR_Maîtrise universitaire en sciences des religions - Automne": "https://applicationspub.unil.ch/interpub/noauth/php/Ud/listeCours.php?v_ueid=253&v_semposselected=169&v_langue=fr&v_isinterne=&v_etapeid1=28099",
    "FTSR_Maîtrise universitaire en sciences des religions - Printemps": "https://applicationspub.unil.ch/interpub/noauth/php/Ud/listeCours.php?v_ueid=253&v_semposselected=170&v_langue=fr&v_isinterne=&v_etapeid1=28099",
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
            if course_info['Crédits'] != "Inconnu":
                break

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
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(response.text)
            print(f"Téléchargé : {file_path}")
        else:
            print(f"Erreur lors du téléchargement de {url} : {response.status_code}")

def synchronize_files():
    """Synchronise les fichiers scraping.csv et liste.csv."""
    scraping_path = os.path.join(os.path.dirname(__file__), '../database/scraping.csv')
    liste_path = os.path.join(os.path.dirname(__file__), '../database/liste.csv')

    # Charger les fichiers CSV
    scraping_df = pd.read_csv(scraping_path, delimiter=';', encoding='utf-8-sig')
    liste_df = pd.read_csv(liste_path, delimiter=';', encoding='utf-8-sig')

    # Identifier les cours à mettre à jour ou ajouter
    for index, scraping_row in scraping_df.iterrows():
        match = liste_df[liste_df['Nom'] == scraping_row['Nom']]
        if not match.empty:
            # Mettre à jour les informations existantes
            liste_df.loc[match.index, ['Professeur', 'Crédits']] = scraping_row[['Professeur', 'Crédits']].values
        else:
            # Ajouter les nouveaux cours
            liste_df = pd.concat([liste_df, pd.DataFrame([scraping_row])], ignore_index=True)

    # Identifier les cours à marquer comme "V A C A T" et "N/A"
    for index, liste_row in liste_df.iterrows():
        match = scraping_df[scraping_df['Nom'] == liste_row['Nom']]
        if match.empty:
            liste_df.loc[index, ['Professeur', 'Crédits']] = ['V A C A T', 'N/A']

    # Sauvegarder les modifications dans liste.csv
    liste_df.to_csv(liste_path, sep=';', index=False, encoding='utf-8-sig')
    print("Synchronisation entre scraping.csv et liste.csv terminée.")

def main():
    """Fonction principale pour scraper les données et les sauvegarder dans un fichier CSV."""
    check_html_update()
    all_courses = []

    for name in urls.keys():
        # Extraire et normaliser le nom de la faculté
        faculty_name = normalize_faculty(name.split(" - ")[0])  # Correction ici
        
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

# Point d'entrée
if __name__ == "__main__":
    main()
    synchronize_files()
    verify_professor_names()