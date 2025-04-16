from flask import Flask, render_template, jsonify, request, send_from_directory
import os
import csv
from datetime import datetime
from flask_socketio import SocketIO
from watchdog.events import FileSystemEventHandler

app = Flask(__name__)  # Définition de l'objet app

# Initialisation de SocketIO
socketio = SocketIO(app)

# Chemins des fichiers CSV
EVALUATIONS_CSV = os.path.join(os.path.dirname(__file__), "../database/evaluations.csv")
LISTE_CSV = os.path.join(os.path.dirname(__file__), "../database/liste.csv")

def initialize_evaluation_csv():
    """Crée le fichier evaluation.csv s'il n'existe pas et copie les données de liste.csv."""
    if not os.path.exists(EVALUATIONS_CSV):
        if os.path.exists(LISTE_CSV):
            try:
                with open(LISTE_CSV, newline='', encoding='utf-8-sig') as courses_file, \
                     open(EVALUATIONS_CSV, 'w', newline='', encoding='utf-8-sig') as eval_file:
                    reader = csv.DictReader(courses_file, delimiter=';')
                    fieldnames = reader.fieldnames + ['Intérêt_Q1', 'Intérêt_Q2', 'Intérêt_Q3', 'Moyenne_Intérêt', 'Difficulté_Q1', 'Difficulté_Q2', 'Difficulté_Q3', 'Moyenne_Difficulté', 'Travail_Q1', 'Moyenne_Travail', 'Moyenne_Globale', 'Commentaires_Généraux', 'Commentaires_Conseils']
                    writer = csv.DictWriter(eval_file, fieldnames=fieldnames, delimiter=';')
                    writer.writeheader()
                    for row in reader:
                        row.update({'Intérêt_Q1': '', 'Intérêt_Q2': '', 'Intérêt_Q3': '', 'Moyenne_Intérêt': '', 'Difficulté_Q1': '', 'Difficulté_Q2': '', 'Difficulté_Q3': '', 'Moyenne_Difficulté': '', 'Travail_Q1': '', 'Moyenne_Travail': '', 'Moyenne_Globale': '', 'Commentaires_Généraux': '', 'Commentaires_Conseils': ''})
                        writer.writerow(row)
            except Exception as e:
                print(f"Erreur lors de l'initialisation de evaluation.csv : {e}")
        else:
            print("Le fichier liste.csv n'existe pas.")

def initialize_liste_csv():
    """Initialise le fichier liste.csv avec les données de scraping.csv."""
    scraping_csv = os.path.join(os.path.dirname(__file__), "../database/scraping.csv")
    try:
        with open(scraping_csv, newline='', encoding='utf-8-sig') as scraping_file, \
             open(LISTE_CSV, 'w', newline='', encoding='utf-8-sig') as liste_file:
            reader = csv.DictReader(scraping_file, delimiter=';')
            fieldnames = ['Faculté', 'Semestre', 'Crédits', 'Nom', 'Professeur', 'Lien', 'Moyenne_Intérêt', 'Moyenne_Difficulté', 'Moyenne_Travail', 'Moyenne_Globale', 'Nombre_Evaluations']
            writer = csv.DictWriter(liste_file, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()

            for row in reader:
                row.update({
                    'Moyenne_Intérêt': 0,
                    'Moyenne_Difficulté': 0,
                    'Moyenne_Travail': 0,
                    'Moyenne_Globale': 0,
                    'Nombre_Evaluations': 0
                })
                writer.writerow(row)
    except Exception as e:
        print(f"Erreur lors de l'initialisation de liste.csv : {e}")

# Appeler cette fonction au démarrage pour s'assurer que liste.csv est initialisé
initialize_liste_csv()

def read_csv_data():
    """Lit les données du fichier CSV et les retourne sous forme de liste de dictionnaires."""
    filepath = os.path.join(os.path.dirname(__file__), "../scraping/cours_extraits.csv")
    courses = []
    if os.path.exists(filepath):
        try:
            with open(filepath, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                for row in reader:
                    courses.append(row)
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier CSV : {e}")
    else:
        print("Le fichier CSV n'existe pas.")
    return courses

def read_evaluation_data():
    """Lit les données du fichier evaluation.csv et les retourne sous forme de liste de dictionnaires."""
    evaluations = []
    try:
        with open(EVALUATIONS_CSV, newline='', encoding='utf-8-sig') as eval_file:
            reader = csv.DictReader(eval_file, delimiter=';')
            for row in reader:
                row['Date_Evaluation'] = format_date_to_dd_mm_yyyy(row['Date_Evaluation'])
                evaluations.append(row)
    except Exception as e:
        print(f"Erreur lors de la lecture de evaluation.csv : {e}")
    return evaluations

def read_evaluation_data_with_counts():
    """Lit les données du fichier evaluation.csv et ajoute le nombre d'évaluations pour chaque cours."""
    evaluations = []
    if os.path.exists(EVALUATIONS_CSV):
        try:
            with open(EVALUATIONS_CSV, newline='', encoding='utf-8-sig') as eval_file:
                reader = csv.DictReader(eval_file, delimiter=';')
                for row in reader:
                    # Compter une évaluation si au moins une des colonnes est remplie
                    count = 1 if any(row[key] for key in ['Intérêt_Q1', 'Difficulté_Q1', 'Travail_Q1']) else 0
                    row['Nombre_Evaluations'] = count
                    evaluations.append(row)
        except Exception as e:
            print(f"Erreur lors de la lecture de evaluation.csv : {e}")
    return evaluations

def update_evaluation(course_name, data):
    """Met à jour ou ajoute une évaluation pour un cours donné."""
    evaluations = read_evaluation_data()
    updated = False
    for row in evaluations:
        if row['Nom'] == course_name:
            # Incrémenter le compteur Nombre_Evaluations
            row['Nombre_Evaluations'] = int(row.get('Nombre_Evaluations', 0)) + 1
            row.update(data)
            updated = True
            break
    if not updated:
        print(f"Erreur : le cours '{course_name}' n'existe pas dans evaluation.csv.")
        return False

    try:
        with open(EVALUATIONS_CSV, 'w', newline='', encoding='utf-8-sig') as eval_file:
            fieldnames = evaluations[0].keys()
            writer = csv.DictWriter(eval_file, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            writer.writerows(evaluations)
        return True
    except Exception as e:
        print(f"Erreur lors de la mise à jour de evaluation.csv : {e}")
        return False

def update_evaluation_counts():
    """Met à jour le nombre d'évaluations pour chaque cours dans le fichier evaluation.csv."""
    evaluations = []
    try:
        with open(EVALUATIONS_CSV, newline='', encoding='utf-8-sig') as eval_file:
            reader = csv.DictReader(eval_file, delimiter=';')
            fieldnames = reader.fieldnames

            # Ajouter la colonne Nombre_Evaluations si elle n'existe pas
            if 'Nombre_Evaluations' not in fieldnames:
                fieldnames.append('Nombre_Evaluations')

            for row in reader:
                # Compter les évaluations non vides
                count = sum(1 for key in ['Intérêt_Q1', 'Difficulté_Q1', 'Travail_Q1'] if row.get(key))
                row['Nombre_Evaluations'] = count
                evaluations.append(row)

        # Écrire les données mises à jour dans le fichier
        with open(EVALUATIONS_CSV, 'w', newline='', encoding='utf-8-sig') as eval_file:
            writer = csv.DictWriter(eval_file, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            writer.writerows(evaluations)

    except Exception as e:
        print(f"Erreur lors de la mise à jour des comptes d'évaluations : {e}")

def read_courses_data():
    """Lit les données des fichiers liste.csv et evaluations.csv et les fusionne."""
    courses = []
    evaluations = {}

    # Lire les données de evaluations.csv
    try:
        with open(EVALUATIONS_CSV, newline='', encoding='utf-8-sig') as eval_file:
            reader = csv.DictReader(eval_file, delimiter=';')
            for row in reader:
                evaluations[row['evaluation_id']] = row
    except Exception as e:
        print(f"Erreur lors de la lecture de evaluations.csv : {e}")

    # Lire les données de liste.csv et les enrichir avec celles de evaluations.csv
    try:
        with open(LISTE_CSV, newline='', encoding='utf-8-sig') as courses_file:
            reader = csv.DictReader(courses_file, delimiter=';')
            for row in reader:
                evaluation_id = row.get('evaluation_id')
                if evaluation_id in evaluations:
                    row.update(evaluations[evaluation_id])
                courses.append(row)
    except Exception as e:
        print(f"Erreur lors de la lecture de liste.csv : {e}")

    return courses

def update_evaluation_with_reference(course_name, data):
    """Ajoute une nouvelle évaluation en complétant les données manquantes avec liste.csv."""
    courses = read_courses_data()
    course_data = next((course for course in courses if course['Nom'] == course_name), None)

    if not course_data:
        print(f"Erreur : le cours '{course_name}' n'existe pas dans liste.csv.")
        return False

    # Compléter les données manquantes avec les informations de liste.csv
    new_evaluation = {
        'Nom_Cours': course_name,
        'Professeur': course_data['Professeur'],
        'Date_Evaluation': datetime.now().strftime('%d-%m-%Y'),
        'Auteur': 'Anne Onyme',  # Remplacer par l'utilisateur actuel si nécessaire
        'Intérêt_Q1': '',
        'Intérêt_Q2': '',
        'Intérêt_Q3': '',
        'Moyenne_Intérêt': '',
        'Difficulté_Q1': '',
        'Difficulté_Q2': '',
        'Difficulté_Q3': '',
        'Moyenne_Difficulté': '',
        'Travail_Q1': '',
        'Moyenne_Travail': '',
        'Moyenne_Globale': '',
        'Commentaires_Généraux': '',
        'Commentaires_Conseils': '',
        'Like_Généraux': '0',
        'Dislike_Généraux': '0',
        'Signalement_Généraux': '0',
        'Like_Conseils': '0',
        'Dislike_Conseils': '0',
        'Signalement_Conseils': '0'
    }

    # Mettre à jour les colonnes avec les données fournies
    new_evaluation.update(data)

    try:
        with open(EVALUATIONS_CSV, 'a', newline='', encoding='utf-8-sig') as eval_file:
            fieldnames = ['Nom_Cours', 'Professeur', 'Auteur', 'Date_Evaluation', 'Intérêt_Q1', 'Intérêt_Q2', 'Intérêt_Q3', 'Moyenne_Intérêt', 'Difficulté_Q1', 'Difficulté_Q2', 'Difficulté_Q3', 'Moyenne_Difficulté', 'Travail_Q1', 'Moyenne_Travail', 'Moyenne_Globale', 'Commentaires_Généraux', 'Commentaires_Conseils', 'Like_Généraux', 'Dislike_Généraux', 'Signalement_Généraux', 'Like_Conseils', 'Dislike_Conseils', 'Signalement_Conseils']
            writer = csv.DictWriter(eval_file, fieldnames=fieldnames, delimiter=';')

            # Écrire l'évaluation dans le fichier
            writer.writerow(new_evaluation)
        return True
    except Exception as e:
        print(f"Erreur lors de l'ajout de l'évaluation dans evaluations.csv : {e}")
        return False

def update_liste_csv():
    """Met à jour les moyennes et le nombre d'évaluations dans liste.csv en fonction des données d'evaluations.csv."""
    # Charger les données d'évaluations
    evaluations = []
    try:
        with open(EVALUATIONS_CSV, newline='', encoding='utf-8-sig') as eval_file:
            reader = csv.DictReader(eval_file, delimiter=';')
            evaluations = list(reader)
    except Exception as e:
        print(f"Erreur lors de la lecture de evaluations.csv : {e}")
        return

    # Calculer les moyennes et le nombre d'évaluations par cours
    course_averages = {}
    for eval_row in evaluations:
        course_name = eval_row['Nom_Cours']
        if course_name not in course_averages:
            course_averages[course_name] = {
                'Moyenne_Intérêt': 0,
                'Moyenne_Difficulté': 0,
                'Moyenne_Travail': 0,
                'Moyenne_Globale': 0,
                'Nombre_Evaluations': 0
            }

        def safe_float_conversion(value):
            try:
                return float(value)
            except ValueError:
                return 0.0

        course_averages[course_name]['Moyenne_Intérêt'] += safe_float_conversion(eval_row['Moyenne_Intérêt'])
        course_averages[course_name]['Moyenne_Difficulté'] += safe_float_conversion(eval_row['Moyenne_Difficulté'])
        course_averages[course_name]['Moyenne_Travail'] += safe_float_conversion(eval_row['Moyenne_Travail'])
        course_averages[course_name]['Moyenne_Globale'] += safe_float_conversion(eval_row['Moyenne_Globale'])
        course_averages[course_name]['Nombre_Evaluations'] += 1

    # Calculer les moyennes finales
    for course_name, averages in course_averages.items():
        averages['Moyenne_Intérêt'] = round(averages['Moyenne_Intérêt'] / averages['Nombre_Evaluations'], 2)
        averages['Moyenne_Difficulté'] = round(averages['Moyenne_Difficulté'] / averages['Nombre_Evaluations'], 2)
        averages['Moyenne_Travail'] = round(averages['Moyenne_Travail'] / averages['Nombre_Evaluations'], 2)
        averages['Moyenne_Globale'] = round(averages['Moyenne_Globale'] / averages['Nombre_Evaluations'], 2)

    # Mettre à jour liste.csv
    try:
        with open(LISTE_CSV, newline='', encoding='utf-8-sig') as liste_file:
            reader = csv.DictReader(liste_file, delimiter=';')
            courses = list(reader)

        for course in courses:
            course_name = course['Nom']
            if course_name in course_averages:
                course.update({
                    'Moyenne_Intérêt': course_averages[course_name]['Moyenne_Intérêt'],
                    'Moyenne_Difficulté': course_averages[course_name]['Moyenne_Difficulté'],
                    'Moyenne_Travail': course_averages[course_name]['Moyenne_Travail'],
                    'Moyenne_Globale': course_averages[course_name]['Moyenne_Globale'],
                    'Nombre_Evaluations': course_averages[course_name]['Nombre_Evaluations']
                })

        with open(LISTE_CSV, 'w', newline='', encoding='utf-8-sig') as liste_file:
            fieldnames = ['Faculté', 'Semestre', 'Crédits', 'Nom', 'Professeur', 'Lien', 'Moyenne_Intérêt', 'Moyenne_Difficulté', 'Moyenne_Travail', 'Moyenne_Globale', 'Nombre_Evaluations']
            writer = csv.DictWriter(liste_file, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            writer.writerows(courses)

    except Exception as e:
        print(f"Erreur lors de la mise à jour de liste.csv : {e}")

@app.route('/')
def liste():
    courses = read_courses_data()  # Lire les données depuis liste.csv
    return render_template('liste.html', courses=courses)

@app.route('/evaluation', methods=['GET', 'POST'])
def evaluation():
    initialize_evaluation_csv()  # S'assurer que le fichier evaluation.csv existe

    if request.method == 'POST':
        course_name = request.form.get('course_name')
        interest_q1 = float(request.form.get('interest_q1')) * 1.5  # Conversion sur 6
        interest_q2 = float(request.form.get('interest_q2')) * 1.5  # Conversion sur 6
        interest_q3 = float(request.form.get('interest_q3')) * 1.5  # Conversion sur 6
        difficulty_q1 = float(request.form.get('difficulty_q1')) * 1.5  # Conversion sur 6
        difficulty_q2 = float(request.form.get('difficulty_q2')) * 1.5  # Conversion sur 6
        difficulty_q3 = float(request.form.get('difficulty_q3')) * 1.5  # Conversion sur 6
        work_q1 = float(request.form.get('work_q1')) * 1.5  # Conversion sur 6
        comments_general = request.form.get('comments_general')
        comments_tips = request.form.get('comments_tips')

        # Calcul des moyennes sur 4
        moyenne_interet = round((float(request.form.get('interest_q1')) + float(request.form.get('interest_q2')) + float(request.form.get('interest_q3'))) / 3, 1)
        moyenne_difficulte = round((float(request.form.get('difficulty_q1')) + float(request.form.get('difficulty_q2')) + float(request.form.get('difficulty_q3'))) / 3, 1)
        moyenne_travail = round(float(request.form.get('work_q1')), 1)

        # Conversion des moyennes sur 6
        moyenne_interet = round(moyenne_interet * 1.5, 1)
        moyenne_difficulte = round(moyenne_difficulte * 1.5, 1)
        moyenne_travail = round(moyenne_travail * 1.5, 1)

        # Calcul de la moyenne globale
        moyenne_globale = round((moyenne_interet + moyenne_difficulte + moyenne_travail) / 3, 1)

        # Ajouter une nouvelle évaluation dans evaluations.csv
        success = update_evaluation_with_reference(course_name, {
            'Intérêt_Q1': interest_q1,
            'Intérêt_Q2': interest_q2,
            'Intérêt_Q3': interest_q3,
            'Moyenne_Intérêt': moyenne_interet,
            'Difficulté_Q1': difficulty_q1,
            'Difficulté_Q2': difficulty_q2,
            'Difficulté_Q3': difficulty_q3,
            'Moyenne_Difficulté': moyenne_difficulte,
            'Travail_Q1': work_q1,
            'Moyenne_Travail': moyenne_travail,
            'Moyenne_Globale': moyenne_globale,
            'Commentaires_Généraux': comments_general,
            'Commentaires_Conseils': comments_tips
        })

        if success:
            return jsonify({"message": "Évaluation enregistrée avec succès."}), 200
        else:
            return jsonify({"error": "Erreur lors de l'enregistrement de l'évaluation."}), 500

    courses = read_courses_data()  # Lire les données depuis liste.csv
    return render_template('evaluation.html', courses=courses)

@app.route('/last-update')
def last_update():
    try:
        # Chemin relatif vers le fichier evaluation.csv
        filepath = EVALUATIONS_CSV
        if not os.path.exists(filepath):
            raise FileNotFoundError("Le fichier CSV n'existe pas.")
        timestamp = os.path.getmtime(filepath)  # Récupère le timestamp de la dernière modification
        date = datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M:%S')  # Format 24h
        return jsonify(date)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Erreur inconnue"}), 500

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/forum')
def forum():
    return render_template('forum.html')

@app.route('/propositions')
def propositions():
    propositions_data = []
    csv_path = os.path.join(os.path.dirname(__file__), '../database/améliorations.csv')

    try:
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                propositions_data.append(row)
    except FileNotFoundError:
        print(f"Le fichier {csv_path} est introuvable.")
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier CSV : {e}")

    return render_template('propositions.html', propositions=propositions_data)

@app.route('/database/evaluations.csv')
def serve_evaluations_csv():
    """Route pour servir le fichier evaluations.csv."""
    try:
        directory = os.path.join(os.path.dirname(__file__), '../database')
        return send_from_directory(directory, 'evaluations.csv')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update-reaction', methods=['POST'])
def update_reaction():
    """Met à jour les colonnes Like_Généraux, Dislike_Généraux, Signalement_Généraux, etc., pour un commentaire donné."""
    try:
        # Ajout de logs pour déboguer les données reçues
        print("Données reçues :", request.json)

        evaluation_id = request.json.get('evaluation_id')
        reaction_type = request.json.get('reaction_type')
        comment_type = request.json.get('comment_type')

        if not evaluation_id or reaction_type not in ['Like', 'Dislike', 'Signalement'] or comment_type not in ['general', 'conseils']:
            return jsonify({"error": "Données invalides."}), 400

        evaluations = []
        with open(EVALUATIONS_CSV, newline='', encoding='utf-8-sig') as eval_file:
            reader = csv.DictReader(eval_file, delimiter=';')
            evaluations = list(reader)

        # Déterminer la colonne à mettre à jour
        reaction_column = f"{reaction_type}_{'Généraux' if comment_type == 'general' else 'Conseils'}"

        updated = False
        for row in evaluations:
            if row['evaluation_id'] == evaluation_id:
                print(f"Avant mise à jour : {reaction_column} = {row.get(reaction_column, 0)}")
                row[reaction_column] = str(int(row.get(reaction_column, 0)) + 1)
                print(f"Après mise à jour : {reaction_column} = {row[reaction_column]}")
                updated = True
                break

        if not updated:
            return jsonify({"error": "Évaluation non trouvée."}), 404

        with open(EVALUATIONS_CSV, 'w', newline='', encoding='utf-8-sig') as eval_file:
            fieldnames = evaluations[0].keys()
            writer = csv.DictWriter(eval_file, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            writer.writerows(evaluations)

        return jsonify({"message": "Réaction mise à jour avec succès."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Met à jour les moyennes dans liste.csv au démarrage
    try:
        update_liste_csv()
        print("Les données de liste.csv ont été mises à jour avec succès.")
    except Exception as e:
        print(f"Erreur lors de la mise à jour de liste.csv : {e}")

    app.run(debug=True, port=5001)  # Assurez-vous que l'application est lancée correctement

class EvaluationFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith("evaluations.csv"):
            print("Modification ignorée pour evaluations.csv.")

if __name__ == '__main__':
    # Lancer l'application avec SocketIO
    socketio.run(app, debug=True, port=5001)

from datetime import datetime

def format_date_to_dd_mm_yyyy(date_str):
    """Convertit une date de format aaaa-mm-jj en jj-mm-aaaa."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').strftime('%d-%m-%Y')
    except ValueError:
        return date_str
