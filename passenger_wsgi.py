"""
WSGI Entry Point pour o2switch (Passenger)
"""
import sys
import os

# Ajouter le répertoire de l'application au path
sys.path.insert(0, os.path.dirname(__file__))

# Importer l'application Flask
from app import app as application

# Passenger cherche l'objet 'application'
# C'est l'équivalent de app.run() mais géré par Passenger

if __name__ == '__main__':
    application.run()


