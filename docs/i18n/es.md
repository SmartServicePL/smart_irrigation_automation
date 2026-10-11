# Smart Irrigation Automation - Guía de interfaz en español

Usa esta página al configurar el blueprint polaco en Home Assistant.

## Ajustes principales

| Etiqueta en polaco | Español |
| --- | --- |
| Wspolne encje pogody i sensory | Entidades meteorológicas y sensores compartidos |
| Encja pogody do prognozy | Entidad meteorológica para la previsión |
| Korzystaj z danych MeteoFusion HA | Usar datos de MeteoFusion HA |
| MeteoFusion - minimalna pewnosc prognozy | MeteoFusion - confianza mínima de la previsión |
| Opcjonalne sensory lokalne i nadpisania | Sensores locales y sustituciones opcionales |
| Lokalna encja pogody | Entidad meteorológica local |
| Czujnik deszczu | Sensor de lluvia |
| Opad zmierzony - najlepiej ostatnie 24 h | Lluvia medida - preferiblemente ultimas 24 h |
| Temperatura ogrodu | Temperatura del jardín |
| Wiatr | Viento |
| UV / slonce | UV / sol |
| Dzienne ET0 / ewapotranspiracja | ETo diaria / evapotranspiración |
| Wilgotnosc gleby | Humedad del suelo |
| Wilgotnosc gleby blokujaca podlewanie | Umbral de humedad del suelo que bloquea el riego |
| Ustawienia ogolne | Ajustes generales |
| Liczba sekcji | Número de zonas |
| Przekazuj wyliczony czas do sterownika Rain Bird | Enviar el tiempo calculado al controlador Rain Bird |
| Nadzor czasu pracy sekcji | Supervisión del tiempo de riego de la zona |

## Ajustes de zona

| Etiqueta en polaco | Español |
| --- | --- |
| Sekcja X - encja | Zona X - entidad |
| Sekcja X - nazwa | Zona X - nombre |
| Sekcja X - rodzaj gleby | Zona X - tipo de suelo |
| Sekcja X - co rosnie | Zona X - cultivo / plantas |
| Sekcja X - zraszacze | Zona X - aspersores |
| Sekcja X - wlasny opad zraszaczy | Zona X - tasa de precipitación personalizada |
| Sekcja X - korekta czasu | Zona X - ajuste de duración |
| Sekcja X - online | Zona X - sensor de conexión |
| Sekcja X - bateria | Zona X - sensor de batería |

## Tipos de suelo

| Opción en polaco | Español |
| --- | --- |
| Piaszczysta / bardzo lekka | Arenoso / muy ligero |
| Lekka ogrodowa | Suelo de jardín ligero |
| Zwykla ziemia ogrodowa | Suelo de jardín normal |
| Humusowa / prochniczna | Suelo rico en humus / compost |
| Czarnoziem / czarna ziemia | Chernozem / tierra negra |
| Gliniasta / ciezka | Arcilloso / pesado |
| Bardzo ciezka / zbita glina | Arcilla muy pesada / compactada |

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
| Glowna godzina podlewania | Hora de inicio |
| Wzgledem wschodu slonca | Amanecer |
| Wzgledem zachodu slonca | Atardecer |
| Przesuniecie wzgledem slonca | Desplazamiento respecto al sol |
| Awaryjny start po pominietej godzinie | Inicio de recuperacion tras omitir la hora principal |
| Miesiac startu sezonu | Mes de inicio de temporada |
| Miesiac konca sezonu | Mes de fin de temporada |
| Minimalna dawka do startu | Dosis mínima para iniciar |
| Maksymalna dawka jednego podlewania | Dosis máxima por riego |
| Minimalny czas sekcji | Duración mínima de la zona |
| Maksymalny czas sekcji | Duración máxima de la zona |
| Przerwa miedzy sekcjami | Pausa entre zonas |
| Wlacz dodatkowe przeliczenia | Activar recálculos adicionales |
| Helper - nastepne podlewanie | Helper - próximo riego |
| Helper - trwaly bilans wody | Helper - balance hídrico persistente |
| Wlacz logbook.log | Activar logbook.log |
| Tworz powiadomienie persistent_notification | Crear persistent_notification |

## Bloqueos meteorológicos

| Etiqueta en polaco | Español |
| --- | --- |
| Blokady pogodowe | Bloqueos meteorológicos |
| Prognozowany deszcz blokujacy | Lluvia prevista que bloquea el riego |
| Prawdopodobienstwo deszczu blokujace | Probabilidad de lluvia que bloquea el riego |
| Ile deszczu odjac od dawki | Parte de la lluvia medida que se descuenta |
| Minimalna temperatura | Temperatura mínima |
| Temperatura upalu | Temperatura de calor |
| Maksymalny wiatr | Viento máximo |
| Minimalna bateria sekcji | Batería mínima de la zona |
| Sprawnosc instalacji | Eficiencia de la instalación |
