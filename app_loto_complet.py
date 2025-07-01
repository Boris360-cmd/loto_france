import streamlit as st
import pandas as pd
import requests
from io import StringIO
from collections import Counter
from datetime import datetime, timedelta
import altair as alt
import matplotlib.pyplot as plt
from itertools import combinations

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

# Interface principale
with st.spinner("Chargement des données réelles du Loto France..."):
    df = charger_donnees()

st.markdown("---")
choix_jour = st.selectbox("Choisissez un jour de tirage :", ["Monday", "Wednesday", "Saturday"])
aujourdhui = datetime.today()
delta = {"Monday": 0, "Wednesday": 2, "Saturday": 5}[choix_jour] - aujourdhui.weekday()
if delta < 0:
    delta += 7
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
st.download_button(":inbox_tray: Télécharger les grilles en CSV", data=csv, file_name="grilles_prochain_tirage.csv", mime="text/csv")

# Évaluation sur les 180 derniers tirages
st.markdown("---")
st.subheader(":bar_chart: Évaluation sur les 180 derniers tirages")
filtre_jour = st.selectbox("Filtrer l'évaluation par jour de tirage :", ["All", "Monday", "Wednesday", "Saturday"])
recents = df.tail(180)
if filtre_jour != "All":
    recents = recents[recents['Jour'] == filtre_jour]

eval_data = []
perf_dict = performance_chances(df)
for row in recents.itertuples():
    history = df[(df['Date'] < row.Date) & (df['Date'] >= row.Date - timedelta(days=180))]
    if len(history) < 5:
        continue
    all_numbers = [n for nums in history['Main_Numbers'] for n in nums]
    counter = Counter(all_numbers)
    g1 = [n for n, _ in counter.most_common(5)]
    recent = [n for nums in history.tail(3)['Main_Numbers'] for n in nums]
    g2_raw = [n for n, _ in Counter(recent).most_common() if n not in g1]
    g2 = g2_raw[:5] + [n for n in counter if n not in g1 and n not in g2_raw][:5 - len(g2_raw)]
    rare = [n for n, _ in counter.most_common()][-10:]
    freq = [n for n, _ in counter.most_common(10)]
    g3 = freq[:3] + rare[:2]
    fusion = [n for n, _ in Counter(g1 + g2 + g3).most_common(5)]

    actual_main = set(row.Main_Numbers)
    actual_chance = row.numero_chance
    for name, nums in [("Grille 1", g1), ("Grille 2", g2), ("Grille 3", g3), ("Fusion", fusion)]:
        match = len(set(nums) & actual_main)
        chance_hit = int(best_chance(nums, perf_dict) == actual_chance)
        eval_data.append({"Date": row.Date.date(), "Jour": row.Jour, "Grille": name, "Match": match, "Chance_OK": chance_hit})

df_eval = pd.DataFrame(eval_data)
perf_summary = df_eval.groupby("Grille").agg({"Match": "mean", "Chance_OK": "mean"}).round(2)
st.dataframe(perf_summary)

# Visualisation
df_eval['Date'] = pd.to_datetime(df_eval['Date'])
chart = alt.Chart(df_eval).mark_line(point=True).encode(
    x='Date:T',
    y='Match:Q',
    color='Grille:N'
).properties(title="Évolution des bons numéros par grille (180 derniers tirages)")
st.altair_chart(chart, use_container_width=True)

# --- Analyse des styles dominants ---
st.subheader("📌 Styles dominants de liaison par jour de tirage")
grilles_base = {
    res['Grille']: res['Numéros']
    for res in resultats
    if res['Grille'] in ["Grille 1", "Grille 2", "Grille 3"]
}
liaisons_par_jour = {'Monday': [], 'Wednesday': [], 'Saturday': []}

for row in recents.itertuples():
    jour = row.Jour
    if jour not in liaisons_par_jour:
        continue
    actual_nums = row.Main_Numbers
    for g1, g2 in combinations(grilles_base.keys(), 2):
        nums1 = grilles_base[g1]
        nums2 = grilles_base[g2]
        communs = set(nums1).intersection(nums2).intersection(actual_nums)
        for n in communs:
            pos1 = nums1.index(n) + 1
            pos2 = nums2.index(n) + 1
            liaisons_par_jour[jour].append((pos1, pos2))

for jour in ['Monday', 'Wednesday', 'Saturday']:
    st.markdown(f"### 🗓️ Style dominant - {jour}")
    compte = Counter(liaisons_par_jour[jour])
    top = compte.most_common(3)
    if not top:
        st.info("Aucune liaison détectée pour ce jour.")
        continue
    df_top = pd.DataFrame(top, columns=["Liaison (Grille A → B)", "Fréquence"])
    st.dataframe(df_top)

    fig, ax = plt.subplots(figsize=(5, 2))
    for i in range(1, 6):
        ax.plot(i, 1, 'o', color='gray')
        ax.text(i, 1.1, f'{i}', ha='center', va='bottom', fontsize=9)
        ax.plot(i, 0, 'o', color='gray')
        ax.text(i, -0.2, f'{i}', ha='center', va='top', fontsize=9)
    for pos1, pos2 in [liaison for liaison, _ in top]:
        ax.plot([pos1, pos2], [1, 0], color='blue', linewidth=2)
    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(-0.5, 1.5)
    ax.axis('off')
    st.pyplot(fig)

st.markdown("---")
st.caption("© Application basée sur les données OpenData du Loto France.")
