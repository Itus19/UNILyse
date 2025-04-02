import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import datetime

# Emplacement de la base de données des évaluations
evaluation_db = "C:\\Users\\mgabr\\OneDrive\\Bureau\\UNILyse\\database\\evaluations.csv"
html_folder_path = "C:\\Users\\mgabr\\OneDrive\\Bureau\\UNILyse\\scraping\\"
urls = {
    "SSP_Bachelor_1ère_partie_Printemps": "https://applicationspub.unil.ch/interpub/noauth/php/Ud/listeCours.php?v_ueid=171&v_semposselected=170&v_langue=fr&v_isinterne=&v_etapeid1=32348",
    "FTSR_Bachelor_1ère_partie_Automne": "https://applicationspub.unil.ch/interpub/noauth/php/Ud/listeCours.php?v_ueid=253&v_semposselected=169&v_langue=fr&v_isinterne=&v_etapeid1=29959"
}

def normalize_faculty(faculty_name):
    """ Normalise les noms des facultés en abréviations. """
    mapping = {
        "Faculté des sciences sociales et politiques": "SSP",
        "Faculté de théologie et de sciences des religions": "FTSR",
        "Faculté de droit‚ des sciences criminelles et d'administration publique": "FDCA",
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
        file_name = f"UNIL_liste_de_cours_{name}.html"
        file_path = os.path.join(html_folder_path, file_name)
        with open(file_path, 'w', encoding='utf-8-sig') as file:
            file.write(response.text)
        print(f"Mise à jour du fichier HTML pour {name} réussie sous le nom : {file_name}")
    except Exception as e:
        print(f"Erreur lors de la mise à jour du fichier HTML pour {name} : {e}")

def check_html_update():
    """Vérifie si les fichiers HTML doivent être mis à jour."""
    for name, url in urls.items():
        file_path = os.path.join(html_folder_path, f"UNIL_liste_de_cours_{name}.html")
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

def extract_links_from_html(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        content = file.read()

    soup = BeautifulSoup(content, 'html.parser')
    links = []

    for a in soup.find_all('a', onclick=True):
        onclick_content = a['onclick']
        if "window.open" in onclick_content:
            start = onclick_content.find("('") + 2
            end = onclick_content.find("','")
            relative_url = onclick_content[start:end]

            # Vérification pour éviter les doublons d'URL
            if relative_url.startswith("/interpub/noauth/php/Ud/"):
                full_url = f"https://applicationspub.unil.ch{relative_url}"
            else:
                full_url = f"https://applicationspub.unil.ch/interpub/noauth/php/Ud/{relative_url}"
            
            links.append(full_url)

    # Supprimer les doublons
    return list(set(links))
def extract_course_info(soup):
    try:
        course_info = {
            'Faculté': "Inconnu",
            'Semestre': "Inconnu",
            'Cursus': "Inconnu",
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

        # Trouver le tableau des horaires (classe "resultats")
        horaires_table = soup.find("table", class_="resultats")
        if horaires_table:
            # Rechercher la section qui suit immédiatement le tableau des horaires
            section = horaires_table.find_next("p")
            if section:
                section_text = section.get_text().lower()

                # Recherche du semestre
                printemps_present = "printemps" in section_text
                automne_present = "automne" in section_text
                annuel_present = "annuel" in section_text

                if printemps_present and automne_present:
                    course_info['Semestre'] = "Annuel"
                elif printemps_present:
                    course_info['Semestre'] = "Printemps"
                elif automne_present:
                    course_info['Semestre'] = "Automne"
                elif annuel_present:
                    course_info['Semestre'] = "Annuel"
        # Recherche du tableau "Utilisation" pour extraire les crédits
        utilisation_table = soup.find_all("table", class_="resultats")
        for table in utilisation_table:
            for row in table.find_all("tr"):
                cells = row.find_all("td")
                # Vérifie si la ligne contient au moins 4 colonnes (la dernière étant les crédits)
                if len(cells) >= 4:
                    # Vérifie si l'une des cellules contient le mot "Baccalauréat"
                    if any("baccalauréat" in cell.get_text().lower() for cell in cells):
                        # Récupérer la valeur des crédits (dernière colonne)
                        credits_value = cells[-1].get_text().strip()
                        # Vérifie si la valeur est bien un nombre (avec ou sans point)
                        if credits_value.replace('.', '', 1).isdigit():
                            course_info['Crédits'] = credits_value
                        else:
                            # Si la case est vide ou non numérique, on affiche "n/d"
                            course_info['Crédits'] = "n/d"
                        break  # On a trouvé la bonne ligne, on peut arrêter
            if course_info['Crédits'] != "Inconnu":
                break  # Sortir de la boucle principale si les crédits sont déjà trouvés

        # Recherche du cursus dans le tableau "Utilisation"
        utilisation_table = soup.find_all("table", class_="resultats")
        for table in utilisation_table:
            for row in table.find_all("tr"):
                cells = row.find_all("td")
                for cell in cells:
                    cell_text = cell.get_text().lower()
                    if "baccalauréat" in cell_text:
                      course_info['Cursus'] = "Bachelor"
                      break
                    elif "maîtrise" in cell_text:
                      course_info['Cursus'] = "Master"
                      break

        return course_info

    except Exception as e:
        print(f"Erreur lors de l'extraction des informations : {e}")
        return None

def main():
    check_html_update()
    all_courses = []

    for name in urls.keys():
        file_path = os.path.join(html_folder_path, f"UNIL_liste_de_cours_{name}.html")
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
                        all_courses.append(course_info)
                except Exception as e:
                    print(f"Erreur lors de l'extraction depuis {link} : {e}")
        else:
            print(f"Erreur : fichier HTML {file_path} non trouvé.")

    if all_courses:
        csv_file = "cours_extraits.csv"
        keys = all_courses[0].keys()
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=keys, delimiter=';')
            writer.writeheader()
            writer.writerows(all_courses)
        print(f"Données extraites et sauvegardées dans {csv_file}")
    else:
        print("Aucune donnée extraite.")

if __name__ == "__main__":
    main()
