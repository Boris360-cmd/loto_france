# 🎯 Application Loto France - Générateur de Grilles & Analyse Visuelle

Cette application Streamlit permet de :

- Générer automatiquement des grilles de Loto basées sur les tirages réels.
- Calculer le numéro Chance le plus performant.
- Évaluer les grilles sur les **180 derniers tirages**.
- Visualiser les performances par grille dans le temps.
- 🧠 Analyser les **styles dominants de liaison** entre grilles et tirages réels pour chaque jour (lundi, mercredi, samedi).

## 🚀 Lancer l'application

```bash
streamlit run app_loto_complet.py
```

## 📦 Dépendances

Liste des packages nécessaires (déjà dans `requirements.txt`) :

- streamlit
- pandas
- requests
- matplotlib
- altair

## 📁 Fichiers

- `app_loto_complet.py` : Script principal de l'application.
- `requirements.txt` : Dépendances Python.
- `README.md` : Ce fichier.

## 🔍 Données utilisées

Les données des tirages proviennent de l’OpenData officiel :
> https://data.opendatasoft.com/explore/dataset/resultats-loto-2019-a-aujourd-hui%40agrall/

---

Développé avec ❤️ pour explorer les patterns gagnants dans le Loto France.
