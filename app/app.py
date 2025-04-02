import csv
import tkinter as tk
from tkinter import ttk

def load_courses_from_csv(file_path):
    courses = []
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                courses.append(row)
        print(f"Chargement de {len(courses)} cours depuis {file_path}")
    except Exception as e:
        print(f"Erreur lors du chargement du fichier CSV : {e}")
    return courses

def display_courses(courses):
    root = tk.Tk()
    root.title("UNILyse - Liste des Cours")

    # Création du Treeview
    tree = ttk.Treeview(root, columns=("Faculté", "Semestre", "Cursus", "Crédits", "Nom", "Globale", "Travail", "Difficulté", "Intérêt"), show="headings")

    # Définition des colonnes
    columns = ["Faculté", "Semestre", "Cursus", "Crédits", "Nom", "Globale", "Travail", "Difficulté", "Intérêt"]
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")

    # Insertion des données dans le Treeview
    for course in courses:
        try:
            tree.insert("", "end", values=(
                course.get('Faculté', 'N/A'),
                course.get('Semestre', 'N/A'),
                course.get('Cursus', 'N/A'),
                course.get('Crédits', 'N/A'),
                course.get('Nom', 'N/A'),
                course.get('Globale', '0'),
                course.get('Travail', '0'),
                course.get('Difficulté', '0'),
                course.get('Intérêt', '0')
            ))
        except KeyError as e:
            print(f"Erreur d'insertion pour le cours : {course} - Clé manquante : {e}")

    tree.pack(expand=True, fill='both')
    root.mainloop()

# Chemin absolu vers le fichier CSV
csv_file_path = r"C:\Users\mgabr\OneDrive\Bureau\UNILyse\scraping\cours_extraits.csv"
courses = load_courses_from_csv(csv_file_path)
display_courses(courses)
from flask import Flask, render_template, jsonify
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/last-update')
def last_update():
    try:
        filepath = r"C:\Users\mgabr\OneDrive\Bureau\UNILyse\scraping\cours_extraits.csv"
        timestamp = os.path.getmtime(filepath)
        date = datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M:%S')
        return jsonify(date)
    except Exception as e:
        return jsonify("inconnue"), 500

if __name__ == '__main__':
    app.run(debug=True)
