from flask_login import UserMixin
import os
import csv
import hashlib
import binascii

# Chemin du fichier CSV des utilisateurs
USERS_CSV = os.path.join(os.path.dirname(__file__), "../database/users.csv")

# Classe User qui hérite de UserMixin de Flask-Login
class User(UserMixin):
    def __init__(self, id, username, password_hash, email, role):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.role = role
    
    @staticmethod
    def get(user_id):
        """Retourne un utilisateur basé sur son id"""
        try:
            with open(USERS_CSV, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                for row in reader:
                    if row['id'] == user_id:
                        return User(
                            id=row['id'],
                            username=row['username'],
                            password_hash=row['password'],
                            email=row['email'],
                            role=row['role']
                        )
        except Exception as e:
            print(f"Erreur lors de la récupération de l'utilisateur : {e}")
        return None
    
    @staticmethod
    def find_by_username(username):
        """Retourne un utilisateur basé sur son nom d'utilisateur"""
        try:
            with open(USERS_CSV, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                for row in reader:
                    if row['username'] == username:
                        return User(
                            id=row['id'],
                            username=row['username'],
                            password_hash=row['password'],
                            email=row['email'],
                            role=row['role']
                        )
        except Exception as e:
            print(f"Erreur lors de la recherche de l'utilisateur par nom : {e}")
        return None
    
    @staticmethod
    def create(username, password, email, role='user'):
        """Crée un nouvel utilisateur et l'ajoute au fichier CSV"""
        # Vérifier si l'utilisateur existe déjà
        if User.find_by_username(username):
            return False
        
        # Générer un id utilisateur
        user_id = str(User.count_users() + 1)
        
        # Hasher le mot de passe
        password_hash = User.hash_password(password)
        
        try:
            # Vérifier si le fichier existe
            file_exists = os.path.isfile(USERS_CSV) and os.path.getsize(USERS_CSV) > 0
            
            # Ajouter l'utilisateur au fichier CSV
            with open(USERS_CSV, 'a', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ['id', 'username', 'password', 'email', 'role']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
                
                # Écrire l'en-tête si le fichier est vide ou n'existe pas
                if not file_exists:
                    writer.writeheader()
                
                writer.writerow({
                    'id': user_id,
                    'username': username,
                    'password': password_hash,
                    'email': email,
                    'role': role
                })
            
            return True
        except Exception as e:
            print(f"Erreur lors de la création de l'utilisateur : {e}")
            return False
    
    @staticmethod
    def count_users():
        """Compte le nombre d'utilisateurs dans le fichier CSV"""
        try:
            if not os.path.isfile(USERS_CSV) or os.path.getsize(USERS_CSV) == 0:
                return 0
            
            with open(USERS_CSV, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.reader(csvfile, delimiter=';')
                # Soustraire 1 pour l'en-tête
                return sum(1 for _ in reader) - 1
        except Exception as e:
            print(f"Erreur lors du comptage des utilisateurs : {e}")
            return 0
    
    @staticmethod
    def hash_password(password):
        """Hashe un mot de passe avec PBKDF2"""
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        return (salt + pwdhash).decode('ascii')
    
    @staticmethod
    def verify_password(stored_password, provided_password):
        """Vérifie un mot de passe par rapport à un hash stocké"""
        salt = stored_password[:64]
        stored_password = stored_password[64:]
        pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), 
                                      salt.encode('ascii'), 
                                      100000)
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        return pwdhash == stored_password
    
    def check_password(self, password):
        """Vérifie si le mot de passe fourni correspond au hash stocké"""
        return User.verify_password(self.password_hash, password)