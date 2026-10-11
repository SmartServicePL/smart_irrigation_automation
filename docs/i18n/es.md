# Smart Irrigation Automation - Guía de interfaz en español

Usa esta página al configurar el blueprint polaco en Home Assistant.

## Ajustes principales

| Etiqueta en polaco | Español |
| --- | --- |
| Wspólne encje pogody i sensory | Entidades meteorológicas y sensores compartidos |
| Encja pogody do prognozy | Entidad meteorológica para la previsión |
| Korzystaj z danych MeteoFusion HA | Usar datos de MeteoFusion HA |
| MeteoFusion - minimalna pewność prognozy | MeteoFusion - confianza mínima de la previsión |
| Opcjonalne sensory lokalne i nadpisania | Sensores locales y sustituciones opcionales |
| Lokalna encja pogody | Entidad meteorológica local |
| Czujnik deszczu | Sensor de lluvia |
| Opad zmierzony - najlepiej ostatnie 24 h | Lluvia medida - preferiblemente ultimas 24 h |
| Temperatura ogrodu | Temperatura del jardín |
| Wiatr | Viento |
| UV / słońce | UV / sol |
| Dzienne ET0 / ewapotranspiracja | ETo diaria / evapotranspiración |
| Wilgotność gleby | Humedad del suelo |
| Wilgotność gleby blokująca podlewanie | Umbral de humedad del suelo que bloquea el riego |
| Ustawienia ogólne | Ajustes generales |
| Liczba sekcji | Número de zonas |
| Przekazuj wyliczony czas do sterownika Rain Bird | Enviar el tiempo calculado al controlador Rain Bird |
| Nadzór czasu pracy sekcji | Supervisión del tiempo de riego de la zona |

## Ajustes de zona

| Etiqueta en polaco | Español |
| --- | --- |
| Sekcja X - encja | Zona X - entidad |
| Sekcja X - nazwa | Zona X - nombre |
| Sekcja X - rodzaj gleby | Zona X - tipo de suelo |
| Sekcja X - co rośnie | Zona X - cultivo / plantas |
| Sekcja X - zraszacze | Zona X - aspersores |
| Sekcja X - własny opad zraszaczy | Zona X - tasa de precipitación personalizada |
| Sekcja X - korekta czasu | Zona X - ajuste de duración |
| Sekcja X - online | Zona X - sensor de conexión |
| Sekcja X - bateria | Zona X - sensor de batería |

## Tipos de suelo

| Opción en polaco | Español |
| --- | --- |
| Piaszczysta / bardzo lekka | Arenoso / muy ligero |
| Lekka ogrodowa | Suelo de jardín ligero |
| Zwykła ziemia ogrodowa | Suelo de jardín normal |
| Humusowa / próchniczna | Suelo rico en humus / compost |
| Czarnoziem / czarna ziemia | Chernozem / tierra negra |
| Gliniasta / ciężka | Arcilloso / pesado |
| Bardzo ciężka / zbita glina | Arcilla muy pesada / compactada |

## Plantas

| Opción en polaco | Español |
| --- | --- |
| Trawa | Césped |
| Kwiaty | Flores |
| Warzywa | Hortalizas |
| Krzewy | Arbustos |

## Programación, registros y helper

| Etiqueta en polaco | Español |
| --- | --- |
| Start podlewania | Modo de inicio |
| Główna godzina podlewania | Hora de inicio |
| Względem wschodu słońca | Amanecer |
| Względem zachodu słońca | Atardecer |
| Przesunięcie względem słońca | Desplazamiento respecto al sol |
| Awaryjny start po pominiętej godzinie | Inicio de recuperacion tras omitir la hora principal |
| Miesiąc startu sezonu | Mes de inicio de temporada |
| Miesiąc końca sezonu | Mes de fin de temporada |
| Minimalna dawka do startu | Dosis mínima para iniciar |
| Maksymalna dawka jednego podlewania | Dosis máxima por riego |
| Minimalny czas sekcji | Duración mínima de la zona |
| Maksymalny czas sekcji | Duración máxima de la zona |
| Przerwa między sekcjami | Pausa entre zonas |
| Włącz dodatkowe przeliczenia | Activar recálculos adicionales |
| Helper - następne podlewanie | Helper - próximo riego |
| Helper - trwały bilans wody | Helper - balance hídrico persistente |
| Włącz logbook.log | Activar logbook.log |
| Twórz powiadomienie persistent_notification | Crear persistent_notification |

## Bloqueos meteorológicos

| Etiqueta en polaco | Español |
| --- | --- |
| Blokady pogodowe | Bloqueos meteorológicos |
| Prognozowany deszcz blokujący | Lluvia prevista que bloquea el riego |
| Prawdopodobieństwo deszczu blokujące | Probabilidad de lluvia que bloquea el riego |
| Ile deszczu odjąć od dawki | Parte de la lluvia medida que se descuenta |
| Minimalna temperatura | Temperatura mínima |
| Temperatura upału | Temperatura de calor |
| Maksymalny wiatr | Viento máximo |
| Minimalna bateria sekcji | Batería mínima de la zona |
| Sprawność instalacji | Eficiencia de la instalación |
