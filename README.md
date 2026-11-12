# Projet Web sémantique — French Cities

## 1. Présentation du projet

Ce projet consiste à transformer des données ouvertes concernant les communes françaises en données RDF, afin de les représenter sous forme de graphe de connaissances et de pouvoir les interroger avec le langage SPARQL.

Le travail réalisé jusqu'à présent comprend :

- La récupération et le nettoyage des données des communes françaises.
- Le choix des vocabulaires RDF pour chaque colonne et la définition d'un vocabulaire propre au projet (`vocab.ttl`).
- La création de mappings avec Tarql pour transformer les données CSV en RDF.
- La génération des fichiers RDF aux formats N-Triples et Turtle.
- Le chargement des données dans Apache Jena Fuseki.
- La vérification du graphe et l'exécution de requêtes SPARQL.

## 2. Source des données

Le fichier source est le jeu de données des communes de France publié sur data.gouv.fr (`data/communes-france-2026.csv`, 62 colonnes).

Le fichier CSV utilisé pour la transformation est :

`data/communes-france-2026-clean2.csv`

Il a été préparé en trois temps :

1. Sélection des colonnes utiles au projet (`data/communes-france-2026_filtre.csv`).
2. Nettoyage avec **OpenRefine** : codes à zéros initiaux restaurés, espaces supprimés, URLs Wikipédia corrigées. L'historique des opérations est conservé dans `mapping/openrefine_ops.json`.
3. Ajout de la colonne `superficie_hectare` depuis le fichier source avec le script `scripts/ajout_superficie_hectare.py`.

```bash
python scripts/ajout_superficie_hectare.py
```

Le fichier contient notamment :

- Le code INSEE.
- Le nom de la commune.
- Les codes postaux.
- Le canton ou ville, l'EPCI, le département et la région.
- La population et la superficie.
- La densité de population et l'altitude.
- Les coordonnées géographiques.
- La grille de densité, le niveau d'équipements et les aires d'attraction.

Le fichier contient **34 868 communes**.

## 3. Technologies utilisées

| Technologie | Utilisation |
| --- | --- |
| OpenRefine | Nettoyage et préparation des données CSV |
| Python | Ajout de la colonne `superficie_hectare` |
| Tarql 1.2 | Transformation des données CSV en RDF |
| Jena RIOT (fourni avec Tarql) | Conversion des fichiers N-Triples en Turtle |
| RDF, RDFS, SKOS | Modélisation des données et du vocabulaire du projet |
| N-Triples / Turtle | Formats des fichiers RDF générés |
| Apache Jena Fuseki 6 (Java 21) | Stockage et interrogation du graphe RDF |
| SPARQL | Interrogation des données |

## 4. Organisation du projet

```text
Dana_Project_French_Cities_Grp10/
│
├── data/
│   ├── communes-france-2026.csv          # fichier source (data.gouv.fr, 62 colonnes)
│   ├── communes-france-2026_filtre.csv   # colonnes retenues pour le projet
│   └── communes-france-2026-clean2.csv   # fichier nettoyé utilisé par Tarql
│
├── mapping/
│   ├── mapping.sparql                    # mapping Tarql principal
│   ├── postaux.sparql                    # mapping des codes postaux
│   ├── vocab.ttl                         # vocabulaire du projet (propriétés ex:, SKOS)
│   ├── tableau-1.3-vocabulaires.md       # choix des vocabulaires par colonne
│   ├── openrefine_ops.json               # historique des opérations OpenRefine
│   ├── communes.ttl                      # RDF généré (Turtle)
│   └── postaux.ttl                       # RDF généré (Turtle)
│
├── scripts/
│   └── ajout_superficie_hectare.py       # ajout de superficie_hectare dans clean2
│
├── communes.nt, postaux.nt               # générés localement, non versionnés (.gitignore)
├── LICENSE
└── README.md
```

## 5. Transformation des données avec Tarql

Deux mappings ont été créés pour transformer les données CSV en RDF. Les IRI des ressources sont construites à partir des codes INSEE.

### 5.1. Mapping principal : `mapping.sparql`

Ce mapping permet de créer les ressources RDF correspondant aux communes et aux différentes entités territoriales.

Il génère notamment :

- Les communes (`igeo:Commune`).
- Les départements (`igeo:Departement`).
- Les régions (`igeo:Region`).
- Les cantons ou villes (`igeo:CantonOuVille`) : le code `canton_code` de l'INSEE est celui du « canton ou ville », pas du canton électoral (Nantes = 4496).
- Les EPCI (`igeo:Intercommunalite`).
- Les aires d'attraction des villes (`igeo:AireDAttractionDesVilles2020`). Le code « 000 » (commune hors attraction) ne crée aucune ressource.

Il associe également aux communes leurs différentes propriétés : nom, code INSEE, population, superficie (convertie d'hectares en m² pour `dbo:areaTotal`), densité, altitudes, coordonnées géographiques, liens Wikipédia, etc.

La grille de densité et le niveau d'équipements sont reliés à des niveaux `skos:Concept` définis dans `vocab.ttl`, qui portent leur libellé. Les colonnes de libellés du CSV ne sont donc pas mappées, pour éviter de répéter le même texte pour chaque commune.

### 5.2. Mapping des codes postaux : `postaux.sparql`

Ce deuxième mapping permet de gérer les communes qui possèdent plusieurs codes postaux.

Il utilise la fonction `apf:strSplit` de Jena pour produire un triplet `ex:codesPostaux` distinct pour chaque code postal.

Cela permet de représenter correctement les relations entre les communes et leurs différents codes postaux.

### 5.3. Génération des fichiers RDF

Les commandes sont lancées depuis la racine du dépôt. Les mappings produisent d'abord des fichiers N-Triples :

```bash
tarql --encoding UTF-8 --ntriples mapping/mapping.sparql data/communes-france-2026-clean2.csv > communes.nt
tarql --encoding UTF-8 --ntriples mapping/postaux.sparql data/communes-france-2026-clean2.csv > postaux.nt
```

L'option `--encoding UTF-8` est nécessaire : sans elle, Tarql devine l'encodage du CSV et certains noms accentués sont corrompus (ex. « Auvergne-Rh��ne-Alpes »).

Ils sont ensuite convertis en Turtle avec Jena RIOT (bibliothèque fournie avec Tarql), en reprenant les préfixes du mapping :

```bash
{ sed -n '/^PREFIX/p' mapping/mapping.sparql; cat communes.nt; } > communes-tmp.ttl
java -cp "<dossier tarql>/lib/*" riotcmd.riot --syntax=turtle --formatted=turtle communes-tmp.ttl > mapping/communes.ttl
rm communes-tmp.ttl
```

La même méthode est utilisée pour `postaux.nt` avec `mapping/postaux.sparql`.

Le mode Turtle de Tarql n'est pas utilisé directement, car il encode les caractères accentués des IRI (`%C3%A9` au lieu de `é`). Les fichiers Turtle contiennent exactement les mêmes triplets que les fichiers N-Triples (817 668 pour les communes, 48 324 pour les codes postaux).

## 6. Modélisation RDF

Les ressources du projet utilisent l'espace de noms suivant :

```text
https://sofiaouldammar19.github.io/Dana_Project_French_Cities_Grp10/
```

Deux chemins sont utilisés :

- `/id/` pour identifier les ressources (ex. `/id/commune/44109`, `/id/departement/44`).
- `/def/` pour le vocabulaire du projet : propriétés personnalisées et niveaux SKOS (ex. `/def/grille-densite/1`).

Une commune est reliée à ses entités territoriales par `igeo:subdivisionDirecteDe` :

```text
commune ──► département ──► région
   ├──────► canton ou ville
   ├──────► EPCI
   └──────► aire d'attraction des villes
```

Le projet réutilise plusieurs vocabulaires existants, notamment :

- `igeo:` (ontologie géographique de l'INSEE) pour les entités territoriales, les codes et les noms.
- `dbo:` pour les propriétés de DBpedia (population, superficie, altitude, gentilé…).
- `wgs84:` pour les coordonnées géographiques.
- `foaf:` et `rdfs:` pour les liens vers les pages Web et les libellés.
- `skos:` pour les niveaux de la grille de densité et du niveau d'équipements.
- `xsd:` pour le typage des valeurs.

Des propriétés personnalisées (`ex:`) sont utilisées lorsque les vocabulaires existants ne couvrent pas les informations nécessaires : `ex:grilleDensite`, `ex:niveauEquipements`, `ex:categorieAireAttraction`, `ex:nombreQPV` et `ex:codesPostaux`. Elles sont décrites dans `mapping/vocab.ttl` (libellé, commentaire, domaine, portée), avec les deux schémas de concepts SKOS (7 niveaux de grille de densité, 5 niveaux d'équipements).

Le détail du choix des vocabulaires colonne par colonne se trouve dans `mapping/tableau-1.3-vocabulaires.md`.

## 7. Chargement des données dans Apache Jena Fuseki

Fuseki 6 nécessite Java 21. L'interface de Fuseki est accessible à l'adresse :

```text
http://localhost:3030/
```

Le dataset utilisé est :

```text
/communes
```

Étapes de chargement :

1. Si le dataset contient déjà des données, le vider avec la requête `CLEAR DEFAULT` (sinon les anciens triplets s'ajoutent aux nouveaux).
2. Dans l'onglet **add data**, laisser le champ *graph* vide et charger les trois fichiers :
   - `mapping/communes.ttl`
   - `mapping/postaux.ttl`
   - `mapping/vocab.ttl` (description des propriétés `ex:` et libellés des niveaux SKOS)

Une fois le dataset ouvert, l'onglet **query** permet d'écrire et d'exécuter des requêtes SPARQL.

## 8. Requêtes SPARQL réalisées

### Requête 1 : récupérer les informations d'une commune

Cette requête permet de retrouver le nom d'une commune, son département et sa région à partir de son code INSEE.

```sparql
PREFIX igeo: <http://rdf.insee.fr/def/geo#>

SELECT ?nomCommune ?nomDepartement ?nomRegion
WHERE {
    ?commune igeo:codeINSEE "01001" ;
             igeo:nom ?nomCommune ;
             igeo:subdivisionDirecteDe ?departement .

    ?departement igeo:nom ?nomDepartement ;
                 igeo:subdivisionDirecteDe ?region .

    ?region igeo:nom ?nomRegion .
}
```

**Résultat attendu :**

| Information | Résultat |
| --- | --- |
| Commune | L'Abergement-Clémenciat |
| Département | Ain |
| Région | Auvergne-Rhône-Alpes |

### Requête 2 : récupérer tous les codes postaux d'une commune

Certaines communes possèdent plusieurs codes postaux. Cette requête permet de récupérer l'ensemble des codes postaux associés à une commune.

```sparql
PREFIX ex: <https://sofiaouldammar19.github.io/Dana_Project_French_Cities_Grp10/def/>

SELECT ?codePostal
WHERE {
    <https://sofiaouldammar19.github.io/Dana_Project_French_Cities_Grp10/id/commune/97101>
        ex:codesPostaux ?codePostal .
}
ORDER BY ?codePostal
```

**Résultat :**

La requête retourne 13 codes postaux pour la commune ayant le code INSEE `97101`.

## 9. Vérification des données

Plusieurs vérifications ont été effectuées après le chargement du graphe dans Fuseki.

| Vérification | Résultat |
| --- | ---: |
| Triplets de `communes.ttl` | 817 668 |
| Triplets de `postaux.ttl` | 48 324 |
| Triplets de `vocab.ttl` | 97 |
| **Nombre total de triplets dans le graphe** | **866 089** |
| Nombre de codes postaux pour la commune 97101 | 13 |
| Communes avec une superficie nulle | 0 |

Nombre de ressources par classe :

| Classe | Nombre |
| --- | ---: |
| `igeo:Commune` | 34 868 |
| `igeo:CantonOuVille` | 2 103 |
| `igeo:Intercommunalite` | 1 255 |
| `igeo:AireDAttractionDesVilles2020` | 699 |
| `igeo:Departement` | 101 |
| `igeo:Region` | 18 |
