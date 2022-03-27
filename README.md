Speedtest is an app that performs an Internet speed test at adjustable time intervals. The averaged value of the online service is not taken as the result, but the peak value from the Fritzbox is read in the local network. In this way, you get an approximately real value when, for example, streaming is running in the local network and the network is additionally loaded.

[English readme](https://github.com/Technik-Tueftler/Speedtest/blob/main/README.md)
 • [deutsche readme](https://github.com/willmcgugan/rich/blob/master/README.de.md)

## Function overview 
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

## Installation / Execution
1. locally runs the program by executing the main file. To do this, simply copy the repository and run `main.py`. Currently, first environment variables must be loaded into the IDE or environment. The program was tested and developed under Python 3.10. However, it should be backward compatible up to at least 3.8.
2. via a Docker container. See documentation: <https://hub.docker.com/r/techniktueftler/speedtest>

## Environment variables
|Variable|Explanation|Unit|Default value|
|---|---|---|---|
|IP_FRITZBOX|IP address or hostname of the Fritzbox in the local network|-|fritz.box|
|S_TIME_CHECK_LOW_NETWORK_LOAD|Runtime of measurement to check network load|seconds|10|
|MBIT_THR_FROM_NETWORK_DOWNLOAD_TO_RUN|Limit value for the download when checking the network load. If this is exceeded, no speed test is performed.|Mbit/s|10|
|MBIT_THR_FROM_NETWORK_UPLOAD_TO_RUN|Limit for the upload when checking the network load. If this is exceeded, no speed test is performed.|Mbit/s|2|
|TEST_REPETITION_TIME|Repeat time of the speed test.|seconds|21600|
|TEST_REPEAT_TIME|Repeat time for the test if the network load test failed. Example, if the network load has exceeded the limits |seconds|3600|
|DB_CONNECTOR|Connection string for configuring the database connection. See chapter Database Connections.|-|sqlite:///./Speedtest/files/measurements.sqlite3|


## Database connection
Currently the following databases are supported, which can be initialized via a connection string.

|Database|Example|
|---|---|
|MariaDB|mariadb+mariadbconnector://user_name:Password123!@127.0.0.1:3306/database_name|
|SQLite|sqlite:///path_to_file/database_name.sqlite3|

If no connection string is specified, the program automatically creates an SQLite file and saves it:  
`Start locally via main.py:` Speedtest/files/  
`Start as Docker container without specifying the volume:` /user/app/Speedtest/files/  
`Start as Docker container with volume specified:` /spec_path/  

## Database structure
|name|type|null|standard|explanation|unit|
|---|---|---|---|---|---|
|id|int(11)|No|AUTO_INCREMENT|Unique ID of the entry|-|
|timestamp|timestamp|No|ON UPDATE CURRENT_TIMESTAMP()|Time of finished and entered measurement|-|
|max_download_fritzbox|int(11)|Yes|NULL|Maximum value for download from Fritzbox|Bits/s|
|max_upload_fritzbox|int(11)|Yes|NULL|Maximum value for upload from Fritzbox|Bits/s|
|avg_download_speedtest|int(11)|Yes|NULL|Returned value for download from www.speedtest.net|Bits/s|
|avg_upload_speedtest|int(11)|Yes|NULL|Returned value for upload of www.speedtest.net|bits/s|
|ping_speedtest|int(11)|Yes|NULL|Returned value for the response time of www.speedtest.net. This value varies widely and is usually very high. The assumption is that the program runtime is also included here and does not reflect the true response time.|ms|
