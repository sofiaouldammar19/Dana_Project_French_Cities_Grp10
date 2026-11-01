

# Projet Web sémantique — French Cities

## 1. Présentation du projet

Ce projet consiste à transformer des données ouvertes concernant les communes françaises en données RDF, afin de les représenter sous forme de graphe de connaissances et de pouvoir les interroger avec le langage SPARQL.

Le travail réalisé jusqu'à présent comprend :
- La récupération et le nettoyage des données des communes françaises.
- La création de mappings avec Tarql pour transformer les données CSV en RDF.
- La génération des fichiers RDF au format N-Triples.
- Le chargement des données dans Apache Jena Fuseki.
- La vérification du graphe et l'exécution de requêtes SPARQL.

## 2. Source des données

Le fichier CSV utilisé est :

`data/communes-france-2026-clean2.csv`

Il contient les informations relatives aux communes françaises. Les données ont été nettoyées avec **OpenRefine** avant leur transformation.

Le fichier contient notamment :
- Le code INSEE.
- Le nom de la commune.
- Les codes postaux.
- Le département et la région.
- La population et la superficie.
- La densité de population.
- Les coordonnées géographiques.
- Les informations sur les équipements et les aires d'attraction.

Le fichier contient **34 868 communes**.

## 3. Technologies utilisées

| Technologie | Utilisation |
|---|---|
| OpenRefine | Nettoyage et préparation des données CSV |
| Tarql | Transformation des données CSV en RDF |
| RDF | Modélisation des données sous forme de triplets |
| N-Triples | Format de stockage des données RDF |
| Apache Jena Fuseki | Stockage et interrogation du graphe RDF |
| SPARQL | Interrogation des données |

## 4. Organisation du projet

```text
Dana_Project_French_Cities_Grp10/
│
├── data/
│   └── communes-france-2026-clean2.csv
│
├── mapping/
│   ├── mapping.sparql
│   ├── postaux.sparql
│   └── tableau-1.3-vocabulaires.md
│
├── communes.nt
├── postaux.nt
├── communes-complet.nt
│
└── README.md
```

## 5. Transformation des données avec Tarql

Deux mappings ont été créés pour transformer les données CSV en RDF.

### 5.1. Mapping principal : `mapping.sparql`

Ce mapping permet de créer les ressources RDF correspondant aux communes et aux différentes entités territoriales.

Il génère notamment :
- Les communes.
- Les départements.
- Les régions.
- Les cantons.
- Les EPCI.
- Les aires d'attraction.

Il associe également aux communes leurs différentes propriétés : nom, code INSEE, population, superficie, densité, coordonnées géographiques, etc.

### 5.2. Mapping des codes postaux : `postaux.sparql`

Ce deuxième mapping permet de gérer les communes qui possèdent plusieurs codes postaux.

Il utilise une fonction de séparation des valeurs pour produire un triplet RDF distinct pour chaque code postal.

Cela permet de représenter correctement les relations entre les communes et leurs différents codes postaux.

### 5.3. Génération des fichiers RDF

Pour exécuter le mapping principal :

```bash
tarql --ntriples mapping/mapping.sparql data/communes-france-2026-clean2.csv > communes.nt
```

Pour exécuter le mapping des codes postaux :

```bash
tarql --ntriples mapping/postaux.sparql data/communes-france-2026-clean2.csv > postaux.nt
```

Les deux fichiers sont ensuite fusionnés et les doublons supprimés :

```bash
sort -u communes.nt postaux.nt -o communes-complet.nt
```

Le fichier final `communes-complet.nt` contient le graphe RDF complet.

## 6. Modélisation RDF

Les ressources du projet utilisent l'espace de noms suivant :

```text
https://sofiaouldammar19.github.io/Dana_Project_French_Cities_Grp10/
```

Deux chemins sont utilisés :
- `/id/` pour identifier les ressources.
- `/def/` pour identifier les propriétés personnalisées.

Le projet réutilise plusieurs vocabulaires existants, notamment :
- `igeo:` pour les informations géographiques.
- `dbo:` pour les propriétés de DBpedia.
- `rdfs:` pour les labels et les relations.
- `foaf:` pour les relations avec les ressources Web.
- `wgs84:` pour les coordonnées géographiques.

Des propriétés personnalisées sont également utilisées lorsque les vocabulaires existants ne couvrent pas les informations nécessaires.

## 7. Chargement des données dans Apache Jena Fuseki

Le fichier RDF final est chargé dans Apache Jena Fuseki.

L'interface de Fuseki est accessible à l'adresse :

```text
http://localhost:3030/
```

Le dataset utilisé est :

```text
/communes
```

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
|---|---|
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
|---|---:|
| Nombre de communes | 34 868 |
| Nombre de triplets concernant les codes postaux | 48 324 |
| Nombre de codes postaux pour la commune 97101 | 13 |
| Nombre total de triplets dans le graphe | 866 032 |

Une correction a également été effectuée sur le nom de la région **Auvergne-Rhône-Alpes**, afin de résoudre un problème d'encodage des caractères.


