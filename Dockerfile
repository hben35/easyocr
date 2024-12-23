# Utiliser une image de base avec Python
FROM python:3.9-slim

# Installer les dépendances nécessaires
RUN pip install easyocr flask flask-cors

# Copier le code de l'application
COPY app /app

# Définir le répertoire de travail
WORKDIR /app

# Exposer le port de l'application Flask
EXPOSE 5000

# Lancer l'application Flask
CMD ["python", "app.py"]
