from flask import Flask, render_template, jsonify, request
import os
import csv
from datetime import datetime

app = Flask(__name__)  # Définition de l'objet app

# Chemins des fichiers CSV
EVALUATIONS_CSV = os.path.join(os.path.dirname(__file__), "../scraping/evaluation.csv")

# Chemin du fichier cours_extraits.csv
COURSES_CSV = os.path.join(os.path.dirname(__file__), "../scraping/cours_extraits.csv")

def initialize_evaluation_csv():
    """Crée le fichier evaluation.csv s'il n'existe pas et copie les données de cours_extraits.csv."""
    if not os.path.exists(EVALUATIONS_CSV):
        if os.path.exists(COURSES_CSV):
            try:
                with open(COURSES_CSV, newline='', encoding='utf-8-sig') as courses_file, \
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
            print("Le fichier cours_extraits.csv n'existe pas.")

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
    if os.path.exists(EVALUATIONS_CSV):
        try:
            with open(EVALUATIONS_CSV, newline='', encoding='utf-8-sig') as eval_file:
                reader = csv.DictReader(eval_file, delimiter=';')
                for row in reader:
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

@app.route('/')
def liste():
    evaluations = read_evaluation_data_with_counts()
    print("Données envoyées au template :", evaluations)  # Débogage
    return render_template('liste.html', courses=evaluations)

@app.route('/evaluation', methods=['GET', 'POST'])
def evaluation():
    initialize_evaluation_csv()  # S'assurer que le fichier evaluation.csv existe
    evaluations = read_evaluation_data()  # Lire les données du fichier evaluation.csv

    if request.method == 'POST':
        course_name = request.form.get('course_name')
        interest_q1 = int(request.form.get('interest_q1'))
        interest_q2 = int(request.form.get('interest_q2'))
        interest_q3 = int(request.form.get('interest_q3'))
        difficulty_q1 = int(request.form.get('difficulty_q1'))
        difficulty_q2 = int(request.form.get('difficulty_q2'))
        difficulty_q3 = int(request.form.get('difficulty_q3'))
        work_q1 = int(request.form.get('work_q1'))
        comments_general = request.form.get('comments_general')
        comments_tips = request.form.get('comments_tips')

        # Calcul des moyennes
        moyenne_interet = round((interest_q1 + interest_q2 + interest_q3) / 3, 2)
        moyenne_difficulte = round((difficulty_q1 + difficulty_q2 + difficulty_q3) / 3, 2)
        moyenne_travail = round(work_q1, 2)
        moyenne_globale = round((moyenne_interet + moyenne_difficulte + moyenne_travail) / 3, 2)

        # Mise à jour du fichier evaluation.csv
        success = update_evaluation(course_name, {
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

    return render_template('evaluation.html', courses=evaluations)

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

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Assurez-vous que l'application est lancée correctement
