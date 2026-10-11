# Smart Irrigation Automation - Guide d'interface en français

Utilisez cette page lors de la configuration du blueprint polonais dans Home Assistant.

## Paramètres principaux

| Libellé polonais | Français |
| --- | --- |
| Wspólne encje pogody i sensory | Entités météo et capteurs partagés |
| Encja pogody do prognozy | Entité météo pour les prévisions |
| Stacja pogodowa i czujniki (opcjonalnie) | Station météo et capteurs (facultatif) |
| Lokalna encja pogody | Entité météo locale |
| Czujnik deszczu | Capteur de pluie |
| Opad zmierzony - najlepiej ostatnie 24 h | Pluie mesuree - de preference sur les dernieres 24 h |
| Temperatura ogrodu | Température du jardin |
| Wiatr | Vent |
| UV / słońce | UV / soleil |
| Dzienne ET0 / ewapotranspiracja | ETo journalière / évapotranspiration |
| Wilgotność gleby | Humidité du sol |
| Wilgotność gleby blokująca podlewanie | Seuil d'humidite du sol bloquant l'arrosage |
| Ustawienia ogólne | Paramètres généraux |
| Liczba sekcji | Nombre de zones |
| Przekazuj wyliczony czas do sterownika Rain Bird | Envoyer la durée calculée au contrôleur Rain Bird |
| Nadzór czasu pracy sekcji | Surveillance de la durée d'arrosage de la zone |

## Paramètres de zone

| Libellé polonais | Français |
| --- | --- |
| Sekcja X - encja | Zone X - entité |
| Sekcja X - nazwa | Zone X - nom |
| Sekcja X - rodzaj gleby | Zone X - type de sol |
| Sekcja X - co rośnie | Zone X - végétation |
| Sekcja X - zraszacze | Zone X - arroseurs |
| Sekcja X - własny opad zraszaczy | Zone X - taux de précipitation personnalisé |
| Sekcja X - korekta czasu | Zone X - correction de durée |
| Sekcja X - online | Zone X - capteur de connexion |
| Sekcja X - bateria | Zone X - capteur de batterie |

## Types de sol

| Option polonaise | Français |
| --- | --- |
| Piaszczysta / bardzo lekka | Sableux / très léger |
| Lekka ogrodowa | Terre de jardin légère |
| Zwykła ziemia ogrodowa | Terre de jardin normale |
| Humusowa / próchniczna | Terre riche en humus / compost |
| Czarnoziem / czarna ziemia | Tchernozem / terre noire |
| Gliniasta / ciężka | Argileux / lourd |
| Bardzo ciężka / zbita glina | Argile très lourde / compactée |

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
| Główna godzina podlewania | Heure de démarrage |
| Względem wschodu słońca | Lever du soleil |
| Względem zachodu słońca | Coucher du soleil |
| Przesunięcie względem słońca | Décalage par rapport au soleil |
| Awaryjny start po pominiętej godzinie | Demarrage de secours apres l'heure principale manquee |
| Miesiąc startu sezonu | Mois de début de saison |
| Miesiąc końca sezonu | Mois de fin de saison |
| Minimalna dawka do startu | Dose minimale pour démarrer |
| Maksymalna dawka jednego podlewania | Dose maximale par arrosage |
| Minimalny czas sekcji | Durée minimale de zone |
| Maksymalny czas sekcji | Durée maximale de zone |
| Przerwa między sekcjami | Pause entre les zones |
| Włącz dodatkowe przeliczenia | Activer les recalculs supplémentaires |
| Helper - następne podlewanie | Helper - prochain arrosage |
| Helper - trwały bilans wody | Helper - bilan hydrique persistant |
| Włącz logbook.log | Activer logbook.log |
| Twórz powiadomienie persistent_notification | Créer une persistent_notification |

## Blocages météo

| Libellé polonais | Français |
| --- | --- |
| Blokady pogodowe | Blocages météo |
| Prognozowany deszcz blokujący | Pluie prévue qui bloque l'arrosage |
| Prawdopodobieństwo deszczu blokujące | Probabilité de pluie qui bloque l'arrosage |
| Ile deszczu odjąć od dawki | Part de la pluie mesurée déduite |
| Minimalna temperatura | Température minimale |
| Temperatura upału | Température de forte chaleur |
| Maksymalny wiatr | Vent maximal |
| Minimalna bateria sekcji | Batterie minimale de la zone |
| Sprawność instalacji | Efficacité de l'installation |
