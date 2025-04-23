from flask import Flask, render_template, jsonify, request, redirect, send_from_directory
import os
import csv
from datetime import datetime
from flask_socketio import SocketIO
from watchdog.events import FileSystemEventHandler
import re

app = Flask(__name__)  # Définition de l'objet app

# Initialisation de SocketIO
socketio = SocketIO(app)

# Chemins des fichiers CSV
EVALUATIONS_CSV = os.path.join(os.path.dirname(__file__), "../database/evaluations.csv")
LISTE_CSV = os.path.join(os.path.dirname(__file__), "../database/liste.csv")

def get_question_stats_by_course():
    """
    Collecte les statistiques des réponses aux questions pour chaque cours.
    Renvoie un dictionnaire avec les compteurs de réponses pour chaque question et chaque cours.
    """
    course_stats = {}
    
    try:
        with open(EVALUATIONS_CSV, newline='', encoding='utf-8-sig') as eval_file:
            reader = csv.DictReader(eval_file, delimiter=';')
            for row in reader:
                course_name = row['Nom_Cours']
                
                # Initialiser les données pour ce cours s'il n'existe pas encore
                if course_name not in course_stats:
                    course_stats[course_name] = {
                        'interest_q1': [0, 0, 0, 0],  # [Non, Plutôt non, Plutôt oui, Oui]
                        'interest_q2': [0, 0, 0, 0],
                        'interest_q3': [0, 0, 0, 0],
                        'difficulty_q1': [0, 0, 0, 0],
                        'difficulty_q2': [0, 0, 0, 0],
                        'difficulty_q3': [0, 0, 0, 0],
                        'work_q1': [0, 0, 0, 0],
                        'course_id': ''  # Sera rempli plus tard
                    }
                
                # Incrémenter les compteurs pour chaque question si une réponse existe
                questions = {
                    'interest_q1': 'Intérêt_Q1',
                    'interest_q2': 'Intérêt_Q2',
                    'interest_q3': 'Intérêt_Q3',
                    'difficulty_q1': 'Difficulté_Q1',
                    'difficulty_q2': 'Difficulté_Q2',
                    'difficulty_q3': 'Difficulté_Q3',
                    'work_q1': 'Travail_Q1'
                }
                
                for js_key, csv_key in questions.items():
                    if csv_key in row and row[csv_key].strip():
                        try:
                            # Les valeurs dans le CSV sont de 1 à 4, on soustrait 1 pour les index de 0 à 3
                            value = int(float(row[csv_key])) - 1
                            if 0 <= value <= 3:  # Vérifier que l'indice est valide
                                course_stats[course_name][js_key][value] += 1
                        except (ValueError, IndexError):
                            # Ignorer les valeurs non numériques ou hors limites
                            pass
        
        # Lire liste.csv pour obtenir les IDs des cours
        try:
            with open(LISTE_CSV, newline='', encoding='utf-8-sig') as liste_file:
                reader = csv.DictReader(liste_file, delimiter=';')
                for i, row in enumerate(reader, 1):
                    course_name = row['Nom']
                    if course_name in course_stats:
                        course_stats[course_name]['course_id'] = str(i)
        except Exception as e:
            print(f"Erreur lors de la lecture de liste.csv : {e}")
    
    except Exception as e:
        print(f"Erreur lors de la collecte des statistiques : {e}")
    
    return course_stats

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

def get_course_names():
    """Récupère les noms des cours depuis liste.csv."""
    course_names = []
    try:
        with open(LISTE_CSV, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            course_names = [row['Nom'] for row in reader if 'Nom' in row]
    except Exception as e:
        print(f"Erreur lors de la lecture de liste.csv : {e}")
    return course_names

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
                evaluations[row['Evaluation_id']] = row
    except Exception as e:
        print(f"Erreur lors de la lecture de evaluations.csv : {e}")

    # Lire les données de liste.csv et les enrichir avec celles de evaluations.csv
    try:
        with open(LISTE_CSV, newline='', encoding='utf-8-sig') as courses_file:
            reader = csv.DictReader(courses_file, delimiter=';')
            for row in reader:
                Evaluation_id = row.get('Evaluation_id')
                if Evaluation_id in evaluations:
                    row.update(evaluations[Evaluation_id])
                courses.append(row)
    except Exception as e:
        print(f"Erreur lors de la lecture de liste.csv : {e}")

    return courses

def update_evaluation_with_reference(course_name, evaluation_data):
    """Ajoute une nouvelle évaluation avec un Evaluation_id généré."""
    # Générer un identifiant unique
    Evaluation_id = generate_Evaluation_id()
    evaluation_data['Evaluation_id'] = Evaluation_id

    # Compléter les données manquantes avec des valeurs par défaut
    default_values = {
        'Intérêt_Q1': '', 'Intérêt_Q2': '', 'Intérêt_Q3': '', 'Moyenne_Intérêt': '',
        'Difficulté_Q1': '', 'Difficulté_Q2': '', 'Difficulté_Q3': '', 'Moyenne_Difficulté': '',
        'Travail_Q1': '', 'Moyenne_Travail': '', 'Moyenne_Globale': '',
        'Commentaires_Généraux': '', 'Commentaires_Conseils': '',
        'Like_Généraux': '0', 'Dislike_Généraux': '0', 'Signalement_Généraux': '0',
        'Like_Conseils': '0', 'Dislike_Conseils': '0', 'Signalement_Conseils': '0'
    }
    for key, value in default_values.items():
        evaluation_data.setdefault(key, value)

    # Ajouter l'évaluation au fichier CSV
    try:
        with open(EVALUATIONS_CSV, 'a', newline='', encoding='utf-8-sig') as eval_file:
            fieldnames = ['Evaluation_id', 'Nom_Cours', 'Professeur', 'Auteur', 'Date_Evaluation',
                          'Intérêt_Q1', 'Intérêt_Q2', 'Intérêt_Q3', 'Moyenne_Intérêt',
                          'Difficulté_Q1', 'Difficulté_Q2', 'Difficulté_Q3', 'Moyenne_Difficulté',
                          'Travail_Q1', 'Moyenne_Travail', 'Moyenne_Globale',
                          'Commentaires_Généraux', 'Commentaires_Conseils',
                          'Like_Généraux', 'Dislike_Généraux', 'Signalement_Généraux',
                          'Like_Conseils', 'Dislike_Conseils', 'Signalement_Conseils']
            writer = csv.DictWriter(eval_file, fieldnames=fieldnames, delimiter=';')
            if os.stat(EVALUATIONS_CSV).st_size == 0:  # Si le fichier est vide, écrire l'en-tête
                writer.writeheader()
            writer.writerow(evaluation_data)
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
    professor_links = load_professor_links()  # Charger les liens des professeurs
    question_stats = get_question_stats_by_course()  # Récupérer les statistiques des questions par cours
    return render_template('liste.html', courses=courses, professor_links=professor_links, question_stats=question_stats)

def get_professor_from_course(course_name):
    """Récupère le nom du professeur depuis liste.csv en fonction du nom du cours."""
    try:
        with open(LISTE_CSV, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                if row['Nom'] == course_name:
                    return row['Professeur']
    except Exception as e:
        print(f"Erreur lors de la lecture de liste.csv : {e}")
    return "Inconnu"

@app.route('/evaluation', methods=['GET', 'POST'])
def evaluation():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        course_name = request.form.get('course_name')
        professor = get_professor_from_course(course_name)  # Récupérer le professeur depuis liste.csv
        author = request.form.get('author')
        interest_q1 = request.form.get('interest_q1')
        interest_q2 = request.form.get('interest_q2')
        interest_q3 = request.form.get('interest_q3')
        difficulty_q1 = request.form.get('difficulty_q1')
        difficulty_q2 = request.form.get('difficulty_q2')
        difficulty_q3 = request.form.get('difficulty_q3')
        work_q1 = request.form.get('work_q1')
        comments_general = request.form.get('comments_general')
        comments_tips = request.form.get('comments_tips')

        # Calculer les moyennes
        moyenne_interet = round((float(interest_q1) + float(interest_q2) + float(interest_q3)) / 3, 1)
        moyenne_difficulte = round((float(difficulty_q1) + float(difficulty_q2) + float(difficulty_q3)) / 3, 1)
        moyenne_travail = round(float(work_q1), 1)
        moyenne_globale = round((moyenne_interet + moyenne_difficulte + moyenne_travail) / 3, 1)

        # Préparer les données pour l'évaluation
        evaluation_data = {
            'Nom_Cours': course_name,
            'Professeur': professor,
            'Auteur': author,
            'Date_Evaluation': datetime.now().strftime('%d-%m-%Y'),
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
        }

        # Ajouter l'évaluation
        success = update_evaluation_with_reference(course_name, evaluation_data)

        if success:
            return redirect('/')
        else:
            return render_template('evaluation.html', error="Erreur lors de l'ajout de l'évaluation.")

    # Afficher la page d'évaluation
    courses = get_course_names()
    return render_template('evaluation.html', courses=courses)

def load_professor_links():
    """Charge les liens des professeurs depuis professeurs.csv."""
    professor_links = {}
    csv_path = os.path.join(os.path.dirname(__file__), "../database/professeurs.csv")
    try:
        with open(csv_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')  # Ajout du délimiteur
            if 'Professeur' not in reader.fieldnames or 'Lien_Professeur' not in reader.fieldnames:
                raise ValueError("Les colonnes 'Professeur' et 'Lien_Professeur' sont manquantes dans professeurs.csv.")
            for row in reader:
                professor_links[row['Professeur']] = row['Lien_Professeur']
    except FileNotFoundError:
        print(f"Le fichier {csv_path} est introuvable.")
    except Exception as e:
        print(f"Erreur lors de la lecture de professeurs.csv : {e}")
    return professor_links

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

def generate_Evaluation_id():
    """Génère un Evaluation_id au format année_numéro."""
    current_year = datetime.now().year
    evaluations = []

    # Charger les évaluations existantes
    if os.path.exists(EVALUATIONS_CSV):
        with open(EVALUATIONS_CSV, newline='', encoding='utf-8-sig') as eval_file:
            reader = csv.DictReader(eval_file, delimiter=';')
            evaluations = list(reader)

    # Filtrer les évaluations de l'année en cours
    current_year_evaluations = [row for row in evaluations if row['Evaluation_id'].startswith(str(current_year))]
    next_number = len(current_year_evaluations) + 1

    return f"{current_year}_{next_number}"

@app.route('/update-reaction', methods=['POST'])
def update_reaction():
    """Met à jour les colonnes Like_Généraux, Dislike_Généraux, Signalement_Généraux, etc., pour un commentaire donné."""
    try:
        # Récupérer les données JSON reçues
        data = request.json
        print("Données reçues :", data)

        # Vérifier les données envoyées par le client
        if not data:
            return jsonify({"error": "Aucune donnée reçue."}), 400

        # Correction pour accepter evaluation_id en minuscule
        Evaluation_id = data.get('evaluation_id') or data.get('Evaluation_id')
        reaction_type = data.get('reaction_type')
        comment_type = data.get('comment_type')

        # Validation du format de Evaluation_id
        if not Evaluation_id or not re.match(r'^\d{4}_\d+$', Evaluation_id):
            print("Erreur : Evaluation_id manquant ou invalide")
            return jsonify({"error": "Le champ 'Evaluation_id' est requis et doit être au format 'année_numéro'."}), 400

        if reaction_type not in ['Like', 'Dislike', 'Signalement']:
            print("Erreur : reaction_type invalide")
            return jsonify({"error": "Le champ 'reaction_type' est invalide."}), 400

        if comment_type not in ['general', 'conseils']:
            print("Erreur : comment_type invalide")
            return jsonify({"error": "Le champ 'comment_type' est invalide."}), 400

        # Charger les évaluations depuis le fichier CSV
        evaluations = []
        with open(EVALUATIONS_CSV, newline='', encoding='utf-8-sig') as eval_file:
            reader = csv.DictReader(eval_file, delimiter=';')
            evaluations = list(reader)

        # Déterminer la colonne à mettre à jour
        reaction_column = f"{reaction_type}_{'Généraux' if comment_type == 'general' else 'Conseils'}"

        # Mettre à jour la ligne correspondante
        updated = False
        for row in evaluations:
            if row['Evaluation_id'] == Evaluation_id:
                print(f"Avant mise à jour : {reaction_column} = {row.get(reaction_column, 0)}")
                current_value = row.get(reaction_column, "0")
                row[reaction_column] = str(int(current_value) + 1 if current_value.isdigit() else 1)
                print(f"Après mise à jour : {reaction_column} = {row[reaction_column]}")
                updated = True
                break

        if not updated:
            return jsonify({"error": "Évaluation non trouvée."}), 404

        # Sauvegarder les modifications dans le fichier CSV
        with open(EVALUATIONS_CSV, 'w', newline='', encoding='utf-8-sig') as eval_file:
            fieldnames = evaluations[0].keys()
            writer = csv.DictWriter(eval_file, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            writer.writerows(evaluations)

        return jsonify({"message": "Réaction mise à jour avec succès."}), 200

    except Exception as e:
        print("Erreur lors de la mise à jour de la réaction :", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Met à jour les moyennes dans liste.csv au démarrage
    try:
        update_liste_csv()
        print("Les données de liste.csv ont été mises à jour avec succès.")
    except Exception as e:
        print(f"Erreur lors de la mise à jour de liste.csv : {e}")

    # Lancer l'application avec SocketIO
    socketio.run(app, debug=True, port=5000)

class EvaluationFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith("evaluations.csv"):
            print("Modification ignorée pour evaluations.csv.")

from datetime import datetime

def format_date_to_dd_mm_yyyy(date_str):
    """Convertit une date de format aaaa-mm-jj en jj-mm-aaaa."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').strftime('%d-%m-%Y')
    except ValueError:
        return date_str

