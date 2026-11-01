# Étape 1.3 — Choix des vocabulaires 

Préfixes : `igeo:` = http://rdf.insee.fr/def/geo# · `dbo:` = http://dbpedia.org/ontology/ · `wgs84:` = http://www.w3.org/2003/01/geo/wgs84_pos# · `ex:` = espace de noms du projet (propriétés personnalisées)

| Colonne | Information représentée | Terme RDF | Remarque |
|---|---|---|---|
| code_insee | Code INSEE de la commune | igeo:codeINSEE | vérifié sur l'endpoint INSEE |
| nom_standard | Nom de la commune | igeo:nom (+ rdfs:label @fr) | |
| reg_code | Code de la région | igeo:codeINSEE | |
| reg_nom | Nom de la région | igeo:nom | |
| dep_code | Code du département | igeo:codeINSEE | |
| dep_nom | Nom du département | igeo:nom | |
| canton_code | Code du canton | igeo:codeINSEE | |
| canton_nom | Nom du canton | igeo:nom | |
| epci_code | Code de l'EPCI (SIREN) | igeo:codeINSEE | ressource de classe igeo:Intercommunalite |
| epci_nom | Nom de l'EPCI | igeo:nom | |
| code_postal | Code postal principal | dbo:postalCode | présent sur LOV |
| codes_postaux | Ensemble des codes postaux | ex:codesPostaux | personnalisé ; **un triplet par code** (3 419 communes en ont plusieurs) |
| code_aire_attraction | Code de l'aire d'attraction | igeo:codeINSEE | « 000 » = hors attraction : aucune ressource créée |
| nom_aire_attraction | Nom de l'aire d'attraction | igeo:nom | |
| categorie_aire_attraction | Catégorie de l'aire | ex:categorieAireAttraction | personnalisé ; absente pour « 000 » |
| population | Population totale | dbo:populationTotal | xsd:integer |
| superficie_km2 | Superficie | dbo:areaTotal | convertie en m² (unité DBpedia) |
| densite | Densité de population | dbo:populationDensity | xsd:double |
| altitude_minimale | Altitude minimale | dbo:minimumElevation | mètres |
| altitude_moyenne | Altitude moyenne | dbo:elevation | mètres |
| altitude_maximale | Altitude maximale | dbo:maximumElevation | mètres |
| latitude_mairie | Latitude de la mairie | wgs84:lat | |
| longitude_mairie | Longitude de la mairie | wgs84:long | |
| grille_densite | Code de la grille de densité | ex:grilleDensite | personnalisé |
| grille_densite_texte | Libellé de la grille de densité | **exclu du mapping** | libellé déductible du code (table de correspondance) ; évite de dupliquer l'information |
| niveau_equipements_services | Niveau d'équipements et services | ex:niveauEquipements | personnalisé |
| niveau_equipements_services_texte | Libellé du niveau | **exclu du mapping** | idem : déductible du code |
| qpv_nombre | Nombre de quartiers prioritaires | ex:nombreQPV | personnalisé |
| gentile | Gentilé des habitants | dbo:demonym | littéral @fr ; vide pour 10 841 communes |
| url_wikipedia | Page Wikipédia | foaf:isPrimaryTopicOf | IRI ; absente pour 60 communes |
| url_villedereve | Page Ville de rêve | rdfs:seeAlso | IRI créée seulement si la cellule est non vide |

## Classes
| Entité | Classe |
|---|---|
| Commune | igeo:Commune |
| Département | igeo:Departement |
| Région | igeo:Region |
| Canton | igeo:Canton |
| EPCI | igeo:Intercommunalite |
| Aire d'attraction | igeo:AireDAttractionDesVilles2020 |
