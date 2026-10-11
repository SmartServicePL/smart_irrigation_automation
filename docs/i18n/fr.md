# Smart Irrigation Automation - Guide d'interface en français

Utilisez cette page lors de la configuration du blueprint polonais dans Home Assistant.

## Paramètres principaux

| Libellé polonais | Français |
| --- | --- |
| Wspolne encje pogody i sensory | Entités météo et capteurs partagés |
| Encja pogody do prognozy | Entité météo pour les prévisions |
| Korzystaj z danych MeteoFusion HA | Utiliser les données MeteoFusion HA |
| MeteoFusion - minimalna pewnosc prognozy | MeteoFusion - confiance minimale des prévisions |
| Opcjonalne sensory lokalne i nadpisania | Capteurs locaux et remplacements facultatifs |
| Lokalna encja pogody | Entité météo locale |
| Czujnik deszczu | Capteur de pluie |
| Opad zmierzony - najlepiej ostatnie 24 h | Pluie mesuree - de preference sur les dernieres 24 h |
| Temperatura ogrodu | Température du jardin |
| Wiatr | Vent |
| UV / slonce | UV / soleil |
| Dzienne ET0 / ewapotranspiracja | ETo journalière / évapotranspiration |
| Wilgotnosc gleby | Humidité du sol |
| Wilgotnosc gleby blokujaca podlewanie | Seuil d'humidite du sol bloquant l'arrosage |
| Ustawienia ogolne | Paramètres généraux |
| Liczba sekcji | Nombre de zones |
| Przekazuj wyliczony czas do sterownika Rain Bird | Envoyer la durée calculée au contrôleur Rain Bird |
| Nadzor czasu pracy sekcji | Surveillance de la durée d'arrosage de la zone |

## Paramètres de zone

| Libellé polonais | Français |
| --- | --- |
| Sekcja X - encja | Zone X - entité |
| Sekcja X - nazwa | Zone X - nom |
| Sekcja X - rodzaj gleby | Zone X - type de sol |
| Sekcja X - co rosnie | Zone X - végétation |
| Sekcja X - zraszacze | Zone X - arroseurs |
| Sekcja X - wlasny opad zraszaczy | Zone X - taux de précipitation personnalisé |
| Sekcja X - korekta czasu | Zone X - correction de durée |
| Sekcja X - online | Zone X - capteur de connexion |
| Sekcja X - bateria | Zone X - capteur de batterie |

## Types de sol

| Option polonaise | Français |
| --- | --- |
| Piaszczysta / bardzo lekka | Sableux / très léger |
| Lekka ogrodowa | Terre de jardin légère |
| Zwykla ziemia ogrodowa | Terre de jardin normale |
| Humusowa / prochniczna | Terre riche en humus / compost |
| Czarnoziem / czarna ziemia | Tchernozem / terre noire |
| Gliniasta / ciezka | Argileux / lourd |
| Bardzo ciezka / zbita glina | Argile très lourde / compactée |

## Plantes

| Option polonaise | Français |
| --- | --- |
| Trawa | Pelouse |
| Kwiaty | Fleurs |
| Warzywa | Légumes |
| Krzewy | Arbustes |

## Planning, journaux et helper

| Libellé polonais | Français |
| --- | --- |
| Start podlewania | Mode de démarrage |
| Glowna godzina podlewania | Heure de démarrage |
| Wzgledem wschodu slonca | Lever du soleil |
| Wzgledem zachodu slonca | Coucher du soleil |
| Przesuniecie wzgledem slonca | Décalage par rapport au soleil |
| Awaryjny start po pominietej godzinie | Demarrage de secours apres l'heure principale manquee |
| Miesiac startu sezonu | Mois de début de saison |
| Miesiac konca sezonu | Mois de fin de saison |
| Minimalna dawka do startu | Dose minimale pour démarrer |
| Maksymalna dawka jednego podlewania | Dose maximale par arrosage |
| Minimalny czas sekcji | Durée minimale de zone |
| Maksymalny czas sekcji | Durée maximale de zone |
| Przerwa miedzy sekcjami | Pause entre les zones |
| Wlacz dodatkowe przeliczenia | Activer les recalculs supplémentaires |
| Helper - nastepne podlewanie | Helper - prochain arrosage |
| Helper - trwaly bilans wody | Helper - bilan hydrique persistant |
| Wlacz logbook.log | Activer logbook.log |
| Tworz powiadomienie persistent_notification | Créer une persistent_notification |

## Blocages météo

| Libellé polonais | Français |
| --- | --- |
| Blokady pogodowe | Blocages météo |
| Prognozowany deszcz blokujacy | Pluie prévue qui bloque l'arrosage |
| Prawdopodobienstwo deszczu blokujace | Probabilité de pluie qui bloque l'arrosage |
| Ile deszczu odjac od dawki | Part de la pluie mesurée déduite |
| Minimalna temperatura | Température minimale |
| Temperatura upalu | Température de forte chaleur |
| Maksymalny wiatr | Vent maximal |
| Minimalna bateria sekcji | Batterie minimale de la zone |
| Sprawnosc instalacji | Efficacité de l'installation |
