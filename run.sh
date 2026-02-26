#!/bin/bash

# Nom du dossier de l'environnement virtuel
VENV_DIR="venv"

# Vérifie si on est déjà dans un virtualenv
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Environnement virtuel non actif."

    if [ -d "$VENV_DIR" ]; then
        echo "Activation de l'environnement virtuel..."
        source "$VENV_DIR/bin/activate"
    else
        echo "Erreur : le dossier '$VENV_DIR' n'existe pas."
        exit 1
    fi
else
    echo "Environnement virtuel déjà actif."
fi

# Nettoyage préventif des processus python main.py
pkill -f "python main.py" || true

# Lancer le programme Python
python main.py