Speedtest ist eine App, welche in einstellbaren Zeitintervallen einen Internet Geschwindigkeitstest durchführt. Dabei wird nicht der gemittelte Wert des online Services als Ergebnis genommen, sondern im lokalen Netzwerk den Spitzenwert aus der Fritzbox gelesen. So erhält man einen annähernd realen Wert, wenn im lokalen Netz zum Beispiel gerade ein Streaming läuft und so das Netzwerk zusätzlich belastet.

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
1. Lokal läuft das Programm durch Ausführen der `main.py`. Aktuell muss noch darauf geachtet werden, dass die Umgebungsvariablen in die IDE oder in die Umgebung geladen werden.
2. Über einen Docker Container. Siehe Dokumentation: <https://hub.docker.com/r/techniktueftler/speedtest>

## Umgebungsvariablen
|Variable|Erklärung|Einheit|Standardwert|
|---|---|---|---|
|IP_FRITZBOX|IP Adresse oder Hostname der Fritzbox im lokalen Netzwerk|-|fritz.box|
|S_TIME_CHECK_LOW_NETWORK_LOAD|Laufzeit der Messung zum prüfen der Netzwerklast|Sekunden|10|
|MBIT_THR_FROM_NETWORK_DOWNLOAD_TO_RUN|Grenzwert für den download beim prüfen der Netzwerklast. Wird dieser Überschritten, wird kein Speedtest durchgeführt.|Mbit/s|10|
|MBIT_THR_FROM_NETWORK_UPLOAD_TO_RUN|Grenzwert für den upload beim prüfen der Netzwerklast. Wird dieser Überschritten, wird kein Speedtest durchgeführt.|Mbit/s|2|
|TEST_REPETITION_TIME|Wiederholungszeit des Speedtests.|Sekunden|21600|
|TEST_REPEAT_TIME|Wiederholungszeit für den Test, wenn die Prüfung der Netzwerklast fehlgeschlagen ist. Beispiel, wenn die Netzwerklast die Grenzwerte überschritten hat.|Sekunden|3600|
|DB_CONNECTOR|Verbindungsschlüpfi zum konfigurieren der Datenbankverbindung. Siehe hierzu Kapitel Datenbankverbindungen.|-|sqlite:///./Speedtest/files/measurements.sqlite3|










--> zum ausklappen, damit der Witz möglichst lange lebt * Verbindungsschlüpfi ist ein [...] p_servus