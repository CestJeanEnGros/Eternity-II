from collections import defaultdict, Counter
from itertools import combinations
import sys

def analyser_instance(fichier):
    with open(fichier, 'r') as f:
        lignes = f.readlines()

    n = int(lignes[0].strip())
    tuiles = [tuple(map(int, ligne.strip().split())) for ligne in lignes[1:]]

    couleur_presence = defaultdict(int)
    tuiles_identiques = defaultdict(int)
    motifs_sets = defaultdict(list)
    paires_couleurs = Counter()

    for idx, tuile in enumerate(tuiles):
        # Comptage des couleurs
        for couleur in tuile:
            couleur_presence[couleur] += 1

        # Comptage des tuiles identiques
        tuiles_identiques[tuile] += 1

        # Tuiles avec mêmes couleurs, ordre différent
        sorted_motifs = tuple(sorted(tuile))
        motifs_sets[sorted_motifs].append(idx)

        # Comptage des combinaisons de couleurs (par paires)
        for c1, c2 in combinations(set(tuile), 2):
            paire = tuple(sorted((c1, c2)))
            paires_couleurs[paire] += 1

    print("🔢 Présence des couleurs sur les tuiles :")
    for couleur, count in sorted(couleur_presence.items()):
        print(f"  Couleur {couleur} : {count} fois")

    print("\n🧩 Tuiles complètement identiques :")
    for tuile, count in tuiles_identiques.items():
        if count > 1:
            print(f"  Tuile {tuile} : {count} fois")

    print("\n🔄 Tuiles avec mêmes couleurs mais dans un ordre différent :")
    for motifs, indices in motifs_sets.items():
        if len(indices) > 1:
            print(f"  Tuiles aux motifs {motifs} présentes aux indices : {indices}")

    print("\n🔗 Combinaisons de couleurs fréquentes (top 10) :")
    for (c1, c2), count in paires_couleurs.most_common(10):
        print(f"  ({c1}, {c2}) : {count} tuiles")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Utilisation : python analyse.py fichier_instance.txt")
    else:
        analyser_instance('instances/' + sys.argv[1])
