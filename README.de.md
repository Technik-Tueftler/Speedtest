# Speedtest
[![Build new image and publish to dockerhub](https://github.com/Technik-Tueftler/Speedtest/actions/workflows/build.yml/badge.svg)](https://github.com/Technik-Tueftler/Speedtest/actions/workflows/build.yml)

Speedtest ist eine App, welche in einstellbaren Zeitintervallen einen Internet Geschwindigkeitstest durchführt. Dabei wird nicht der gemittelte Wert des online Services als Ergebnis genommen, sondern im lokalen Netzwerk den Spitzenwert aus der Fritzbox gelesen. So erhält man einen annähernd realen Wert, wenn im lokalen Netz zum Beispiel gerade ein Streaming läuft und so das Netzwerk zusätzlich belastet wird.

[English readme](https://github.com/Technik-Tueftler/Speedtest/blob/main/README.md)
 • [deutsche readme](https://github.com/Technik-Tueftler/Speedtest/blob/main/README.de.md)

## Funktionsübersicht
```mermaid
graph TB
    subgraph Main
        A([Start App]) --> |Timer = 1s| B[check local network load]
        B --> C{below limits?}
        C -->|no <br> Timer = TEST_REPEAT_TIME| B[[check local network load]]
        C -->|yes| D[[Fritzbox monitoring]] & E[[Online Speedtest]]
        D --> F{both finished?}
        E --> F
        F --> |yes <br> Timer = TEST_REPETITION_TIME| B
        F --> |no <br> runtime error| G([End App])
    end
```

```mermaid
graph TB
    subgraph check local network load
        H([Start subprocess]) --> |Timer = S_TIME_CHECK_LOW_NETWORK_LOAD| I[measure current network load]
        I --> |MBIT_THR_FROM_NETWORK_UPLOAD_TO_RUN > real upload <br> MBIT_THR_FROM_NETWORK_DOWNLOAD_TO_RUN > real download| J{Below limits?}
        J --> |yes -> low network load| K[/return network load/]
        J --> |no -> high network load| K
        K --> L([End subprocess])
    end
```

## Installation / Ausführung
1. Lokal läuft das Programm durch Ausführen der `main.py`. Aktuell muss noch darauf geachtet werden, dass die Umgebungsvariablen in die IDE oder in die Umgebung geladen werden. Hierzu einfach das Repository kopieren und die main.py starten. Getestet und entwickelt wurde das Programm unter Python 3.10. Es sollte aber bis mindestens 3.8 Rückwärtskompatibel sein.
2. Über einen Docker Container. Siehe Dokumentation: <https://hub.docker.com/r/techniktueftler/speedtest>

## Umgebungsvariablen
|Variable|Erklärung|Einheit|Standardwert|
|---|---|:-:|---|
|IP_FRITZBOX|IP Adresse oder Hostname der Fritzbox im lokalen Netzwerk|-|`fritz.box`|
|S_TIME_CHECK_LOW_NETWORK_LOAD|Laufzeit der Messung zum prüfen der Netzwerklast|Sekunden|`10`|
|MBIT_THR_FROM_NETWORK_DOWNLOAD_TO_RUN|Grenzwert für den download beim prüfen der Netzwerklast. Wird dieser Überschritten, wird kein Speedtest durchgeführt.|Mbit/s|`10`|
|MBIT_THR_FROM_NETWORK_UPLOAD_TO_RUN|Grenzwert für den upload beim prüfen der Netzwerklast. Wird dieser Überschritten, wird kein Speedtest durchgeführt.|Mbit/s|`2`|
|TEST_REPETITION_TIME|Wiederholungszeit des Speedtests.|Sekunden|`21600`|
|TEST_REPEAT_TIME|Wiederholungszeit für den Test, wenn die Prüfung der Netzwerklast fehlgeschlagen ist. Beispiel, wenn die Netzwerklast die Grenzwerte überschritten hat.|Sekunden|`3600`|
|DB_CONNECTOR|Verbindungsschlüpfi¹ zum konfigurieren der Datenbankverbindung. Siehe hierzu Kapitel Datenbankverbindungen.|-|`sqlite:///./Speedtest/files/measurements.sqlite3`|

## Datenbankverbindung
Aktuell werden folgende Datenbanken unterstützt, welche über einen *Verbindungsschlüpfi*¹ initialisiert werden können.

|Datenbank|Beispiel|
|---|---|
|MariaDB|`mariadb+mariadbconnector://user_name:Passwort123!@127.0.0.1:3306/datenbank_name`|
|SQLite|`sqlite:///pfad_zur_datei/datenbank.sqlite3`|
|PostgreSQL|`postgresql+psycopg2://user_name:Password123!@127.0.0.1/database_name`|

Wird kein Verbindungsschlüpfi angegeben, erstellt das Programm automatisch ein SQLite File und speichert es:

* Start lokal über main.py: `Speedtest/files/`
* Start als Docker Container ohne angabe des Volumes: `/user/app/Speedtest/files/`
* Start als Docker Container mit angabe des Volumes: `/angegebener_pfad/`

## Datenbankstruktur
|Name|Typ|Null|Standard|Erklärung|Einheit|
|---|:-:|:-:|---|---|:-:|
|id|int(11)|Nein|`AUTO_INCREMENT`|Eindeutige ID des Eintrages|-|
|timestamp|timestamp|Nein|`ON UPDATE CURRENT_TIMESTAMP()`|Zeitpunkt der beendeten und eingetragenen Messung|-|
|max_download_fritzbox|int(11)|Ja|`NULL`|Maximalwert für den Download aus der Fritzbox|Bits/s|
|max_upload_fritzbox|int(11)|Ja|`NULL`|Maximalwert für den Upload aus der Fritzbox|Bits/s|
|avg_download_speedtest|int(11)|Ja|`NULL`|Zurückgegebener Wert für den Download von www.speedtest.net|Bits/s|
|avg_upload_speedtest|int(11)|Ja|`NULL`|Zurückgegebener Wert für den Upload von www.speedtest.net|Bits/s|
|ping_speedtest|int(11)|Ja|`NULL`|Zurückgegebener Wert für die Antwortzeit von www.speedtest.net. Dieser Wert unterscheidet sich stark und ist meist sehr hoch. Die Vermutung ist, dass hier auch die Durchlaufzeit des Programmes enthalten ist und spiegelt nicht die wahre Antwortzeit wieder.|ms|

----
¹`Verbindungsschlüpfi` ist ein kreiertes Wort vom Verfasser p_servus und stellt die deutsche Übersetzung von `Connection string` dar.
