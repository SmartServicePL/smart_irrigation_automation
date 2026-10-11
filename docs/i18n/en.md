# Smart Irrigation Automation - English UI Guide

Use this page when configuring the Polish blueprint in Home Assistant.

## Main Settings

| Polish label | English |
| --- | --- |
| Wspólne encje pogody i sensory | Shared weather entities and sensors |
| Encja pogody do prognozy | Forecast weather entity |
| Korzystaj z danych MeteoFusion HA | Use MeteoFusion HA data |
| MeteoFusion - minimalna pewność prognozy | MeteoFusion - minimum forecast confidence |
| Opcjonalne sensory lokalne i nadpisania | Optional local sensors and overrides |
| Lokalna encja pogody | Local weather entity |
| Czujnik deszczu | Rain sensor |
| Opad zmierzony - najlepiej ostatnie 24 h | Measured rain - preferably the last 24 h |
| Temperatura ogrodu | Garden temperature |
| Wiatr | Wind |
| UV / słońce | UV / sun |
| Dzienne ET0 / ewapotranspiracja | Daily ETo / evapotranspiration |
| Wilgotność gleby | Soil moisture |
| Wilgotność gleby blokująca podlewanie | Soil moisture threshold that blocks irrigation |
| Ustawienia ogólne | General settings |
| Liczba sekcji | Number of sections |
| Przekazuj wyliczony czas do sterownika Rain Bird | Send calculated runtime to Rain Bird controller |
| Nadzór czasu pracy sekcji | Section runtime watchdog |

## Section Settings

| Polish label | English |
| --- | --- |
| Sekcja X - encja | Section X - entity |
| Sekcja X - nazwa | Section X - name |
| Sekcja X - rodzaj gleby | Section X - soil type |
| Sekcja X - co rośnie | Section X - plant type |
| Sekcja X - zraszacze | Section X - sprinklers |
| Sekcja X - własny opad zraszaczy | Section X - custom precipitation rate |
| Sekcja X - korekta czasu | Section X - runtime adjustment |
| Sekcja X - online | Section X - online sensor |
| Sekcja X - bateria | Section X - battery sensor |

## Soil Types

| Polish option | English |
| --- | --- |
| Piaszczysta / bardzo lekka | Sandy / very light |
| Lekka ogrodowa | Light garden soil |
| Zwykła ziemia ogrodowa | Standard garden soil |
| Humusowa / próchniczna | Humus-rich / compost-rich soil |
| Czarnoziem / czarna ziemia | Chernozem / black soil |
| Gliniasta / ciężka | Clayey / heavy |
| Bardzo ciężka / zbita glina | Very heavy / compacted clay |

## Plants

| Polish option | English |
| --- | --- |
| Trawa | Grass |
| Kwiaty | Flowers |
| Warzywa | Vegetables |
| Krzewy | Shrubs |

## Schedule, Logs and Helper

| Polish label | English |
| --- | --- |
| Start podlewania | Start mode |
| Główna godzina podlewania | Start time |
| Względem wschodu słońca | Sunrise |
| Względem zachodu słońca | Sunset |
| Przesunięcie względem słońca | Sun offset |
| Awaryjny start po pominiętej godzinie | Recovery start after a missed main time |
| Miesiąc startu sezonu | Season start month |
| Miesiąc końca sezonu | Season end month |
| Minimalna dawka do startu | Minimum dose to start |
| Maksymalna dawka jednego podlewania | Maximum dose per watering |
| Minimalny czas sekcji | Minimum section runtime |
| Maksymalny czas sekcji | Maximum section runtime |
| Przerwa między sekcjami | Pause between sections |
| Włącz dodatkowe przeliczenia | Enable additional recalculations |
| Helper - następne podlewanie | Helper - next watering |
| Helper - trwały bilans wody | Helper - persistent water balance |
| Włącz logbook.log | Enable logbook.log |
| Twórz powiadomienie persistent_notification | Create persistent_notification |

## Weather Blocks

| Polish label | English |
| --- | --- |
| Blokady pogodowe | Weather blocks |
| Prognozowany deszcz blokujący | Forecast rain that blocks irrigation |
| Prawdopodobieństwo deszczu blokujące | Rain probability that blocks irrigation |
| Ile deszczu odjąć od dawki | Share of measured rain credited |
| Minimalna temperatura | Minimum temperature |
| Temperatura upału | Hot-weather temperature |
| Maksymalny wiatr | Maximum wind |
| Minimalna bateria sekcji | Minimum section battery |
| Sprawność instalacji | Irrigation efficiency |
