"""Ajoute la colonne superficie_hectare (fichier brut) au CSV nettoye clean2.

superficie_km2 est arrondie au km2 dans la source (ex. Lannoy : 18 ha -> 0 km2,
12 communes a 0). superficie_hectare est 100 fois plus precise ; le mapping l'utilise pour
dbo:areaTotal (m2 = hectares x 10 000).
"""

import csv

BRUT = "data/communes-france-2026.csv"
CLEAN = "data/communes-france-2026-clean2.csv"

with open(BRUT, encoding="utf-8", newline="") as f:
    hectares = {r["code_insee"]: r["superficie_hectare"] for r in csv.DictReader(f)}

with open(CLEAN, encoding="utf-8", newline="") as f:
    fin_de_ligne = "\r\n" if f.readline().endswith("\r\n") else "\n"
    f.seek(0)
    reader = csv.DictReader(f)
    colonnes = list(reader.fieldnames)
    lignes = list(reader)

if "superficie_hectare" in colonnes:
    print("superficie_hectare deja presente : rien a faire.")
else:
    manquants = [r["code_insee"] for r in lignes if r["code_insee"] not in hectares]
    if manquants:
        raise SystemExit(
            f"Codes INSEE absents du fichier brut : {manquants[:10]} -> rien n'est modifie."
        )
    colonnes.insert(colonnes.index("superficie_km2") + 1, "superficie_hectare")
    for r in lignes:
        r["superficie_hectare"] = hectares[r["code_insee"]]
    with open(CLEAN, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=colonnes, lineterminator=fin_de_ligne)
        w.writeheader()
        w.writerows(lignes)
    vides = sum(1 for r in lignes if r["superficie_hectare"] == "")
    print(
        f"Colonne superficie_hectare ajoutee : {len(lignes)} communes, {vides} vides (Outre-mer, absent de la source)."
    )
