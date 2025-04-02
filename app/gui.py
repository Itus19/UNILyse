from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import csv
from datetime import datetime

app = Flask(__name__)

# Page d'accueil - liste des cours
@app.route('/')
def home():
    df = pd.read_csv(r'scraping/cours_extraits.csv', delimiter=';', encoding='utf-8-sig')
    courses = df.to_dict(orient='records')
    return render_template('index.html', courses=courses)

# Page d'évaluation - formulaire d'évaluation
@app.route('/evaluate', methods=['GET', 'POST'])
def evaluate():
    if request.method == 'POST':
        nom = request.form['nom']
        etudiant = request.form['etudiant']
        date = datetime.now().strftime('%Y-%m-%d')

        # Récupération des réponses du formulaire
        questions = [
            'aime', 'recommande', 'stimulation', 
            'objectifs', 'consignes', 'commentaires', 
            'connaissances', 'travail'
        ]
        responses = [int(request.form[q]) for q in questions]

        # Calcul des moyennes
        interet = round(sum(responses[0:3]) / 3 * 1.5, 2)
        difficulte = round(sum(responses[3:7]) / 4 * 1.5, 2)
        travail = round(responses[7] * 1.5, 2)
        globale = round((interet + difficulte + travail) / 3, 2)

        # Enregistrement dans le fichier CSV
        with open('data/evaluations.csv', 'a', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow([nom, date, etudiant] + responses + [globale, interet, difficulte, travail])

        return redirect(url_for('home'))
    return render_template('evaluate.html')

if __name__ == '__main__':
    app.run(debug=True)
