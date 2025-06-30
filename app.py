import streamlit as st
import pandas as pd
import requests
from io import StringIO
from collections import Counter
from datetime import datetime, timedelta
import altair as alt

st.set_page_config(page_title="Grilles Loto - Numéro Chance Performant", layout="centered")
st.title("🎯 Générateur de Grilles Loto France")
st.markdown("Basé sur les données réelles et la performance historique du numéro Chance")

@st.cache_data(show_spinner=False)
def charger_donnees():
    url = "https://data.opendatasoft.com/explore/dataset/resultats-loto-2019-a-aujourd-hui%40agrall/download/?format=csv"
    response = requests.get(url)
    df = pd.read_csv(StringIO(response.text), sep=';')
    df['Date'] = pd.to_datetime(df['date_de_tirage'], errors='coerce')
    df['Main_Numbers'] = df[['boule_1', 'boule_2', 'boule_3', 'boule_4', 'boule_5']].values.tolist()
    df['Jour'] = df['Date'].dt.day_name()
    return df[['Date', 'Jour', 'Main_Numbers', 'numero_chance']].dropna().sort_values('Date').reset_index(drop=True)

def performance_chances(hist):
    return hist["numero_chance"].value_counts().to_dict()

def best_chance(grille, perf_dict):
    candidats = [n for n in grille if 1 <= n <= 10]
    return max(candidats, key=lambda n: perf_dict.get(n, 0)) if candidats else 1

def generer_grilles(df, date_obj):
    history = df[(df['Date'] < date_obj) & (df['Date'] >= date_obj - timedelta(days=180))]
    if len(history) < 5:
        return []

    perf_dict = performance_chances(history)
    all_numbers = [n for nums in history['Main_Numbers'] for n in nums]
    counter = Counter(all_numbers)
    g1 = [n for n, _ in counter.most_common(5)]

    recent = [n for nums in history.tail(3)['Main_Numbers'] for n in nums]
    g2_raw = [n for n, _ in Counter(recent).most_common() if n not in g1]
    g2 = (g2_raw + [n for n in counter if n not in g1 and n not in g2_raw])[:5]

    rare = [n for n, _ in counter.most_common()][-10:]
    freq = [n for n, _ in counter.most_common(10)]
    g3 = freq[:3] + rare[:2]

    fusion = [n for n, _ in Counter(g1 + g2 + g3).most_common(5)]

    resultats = []
    for label, nums in zip(["Grille 1", "Grille 2", "Grille 3"], [g1, g2, g3]):
        resultats.append({
            "Grille": label,
            "Numéros": sorted(nums),
            "Chance": best_chance(nums, perf_dict)
        })
    resultats.append({
        "Grille": "Fusion",
        "Numéros": sorted(fusion),
        "Chance": best_chance(fusion, perf_dict)
    })
    return resultats

# Interface
with st.spinner("Chargement des données réelles du Loto France..."):
    df = charger_donnees()

st.markdown("---")
choix_jour = st.selectbox("Choisissez un jour de tirage :", ["Monday", "Wednesday", "Saturday"])

# ✅ CORRECTION ICI : calcul précis du prochain jour de tirage
aujourdhui = datetime.today()
delta = {"Monday": 0, "Wednesday": 2, "Saturday": 5}[choix_jour] - aujourdhui.weekday()
if delta < 0:
    delta += 7  # vise le prochain jour correspondant
date_prochaine = aujourdhui + timedelta(days=delta)

st.markdown(f"### 🔮 Tirage prévu le **{date_prochaine.date()}** ({choix_jour})")
resultats = generer_grilles(df, date_prochaine)

df_grilles = pd.DataFrame(resultats)
for res in resultats:
    st.markdown(f"- **{res['Grille']}** : {res['Numéros']} | **Chance** : {res['Chance']}")

# Affichage visuel des grilles
st.markdown("<style>.bulle {display: inline-block; background: #004aad; color: white; border-radius: 50%; padding: 0.4em 0.65em; margin: 0.15em; font-weight: bold; font-size: 1.2em;} .chance {background: red !important;}</style>", unsafe_allow_html=True)

for res in resultats:
    nums_html = ''.join([f'<span class="bulle">{n}</span>' for n in res['Numéros']])
    chance_html = f'<span class="bulle chance">{res["Chance"]}</span>'
    st.markdown(f"<strong>{res['Grille']}</strong><br>{nums_html} {chance_html}<hr>", unsafe_allow_html=True)

# Export CSV
csv = df_grilles.to_csv(index=False).encode('utf-8')
st.download_button("📥 Télécharger les grilles en CSV", data=csv, file_name="grilles_prochain_tirage.csv", mime="text/csv")

# Évaluation sur les 180 derniers tirages avec filtre par jour
st.markdown("---")
st.subheader("📊 Évaluation sur les 180 derniers tirages")
filtre_jour = st.selectbo_
