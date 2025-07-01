# --- Analyse des styles dominants de liaison par jour de tirage ---
from itertools import combinations
from collections import Counter
import matplotlib.pyplot as plt

st.subheader("📌 Styles dominants de liaison par jour de tirage")

# Récupérer les grilles générées automatiquement (hors Fusion)
grilles_base = {
    res['Grille']: res['Numéros']
    for res in resultats
    if res['Grille'] in ["Grille 1", "Grille 2", "Grille 3"]
}

# Initialiser les liaisons détectées par jour
liaisons_par_jour = {'Monday': [], 'Wednesday': [], 'Saturday': []}

# Parcourir les 180 derniers tirages filtrés
for row in recents.itertuples():
    jour = row.Jour
    if jour not in liaisons_par_jour:
        continue
    actual_nums = row.Main_Numbers

    # Comparer chaque paire de grilles
    for g1, g2 in combinations(grilles_base.keys(), 2):
        nums1 = grilles_base[g1]
        nums2 = grilles_base[g2]
        communs = set(nums1).intersection(nums2).intersection(actual_nums)
        for n in communs:
            pos1 = nums1.index(n) + 1
            pos2 = nums2.index(n) + 1
            liaisons_par_jour[jour].append((pos1, pos2))

# Affichage des styles dominants par jour
for jour in ['Monday', 'Wednesday', 'Saturday']:
    st.markdown(f"### 🗓️ Style dominant - {jour}")
    compte = Counter(liaisons_par_jour[jour])
    top = compte.most_common(3)

    if not top:
        st.info("Aucune liaison détectée pour ce jour.")
        continue

    # Tableau des liaisons les plus fréquentes
    df_top = pd.DataFrame(top, columns=["Liaison (Grille A → B)", "Fréquence"])
    st.dataframe(df_top)

    # Schéma visuel du style dominant
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
