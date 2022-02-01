#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import pathlib
import json
from configparser import ConfigParser
import logging
from datetime import datetime

PROJECT_NAME = "Speedtest"
absolute_project_path = pathlib.Path(sys.argv[0].split(PROJECT_NAME, 1)[0], PROJECT_NAME)
PATH_TO_INIT_FILE = pathlib.Path(absolute_project_path, "files", "login_data.priv")
PATH_TO_FILE_CONFIG_FILE = pathlib.Path(absolute_project_path, "files", "config.json")
PATH_TO_FILE_DEBUG_FILE = pathlib.Path(absolute_project_path, "files", "debug.log")

configuration_data = dict()

logger = logging.getLogger("Debug-Log")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(PATH_TO_FILE_DEBUG_FILE)
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)
logger.debug(f"Programmstart: {datetime.today().strftime('%Y-%m-%d %H:%M:%S')}")


def load_configuration():
    global configuration_data
    with open(PATH_TO_FILE_CONFIG_FILE, encoding='utf-8') as file:
        configuration_data = json.load(file)


load_configuration()


def get_dict(section, option):
    if section not in configuration_data: return {}
    if option not in configuration_data[section]: return {}
    return configuration_data[section][option]


def get_string_element(section, option):
    if section not in configuration_data: return ""
    if option not in configuration_data[section]: return ""
    return str(configuration_data[section][option])


def get_int_element(section, option):
    if section not in configuration_data: return 0
    if option not in configuration_data[section]: return 0
    try:
        return int(configuration_data[section][option])
    except Exception:
        return 0


def get_string_list(section, option):
    if section not in configuration_data: return []
    if option not in configuration_data[section]: return []
    return configuration_data[section][option]


def get_string_list_only_section(section):
    if section not in configuration_data: return []
    return configuration_data[section]


def get_configuration(section):
    dict_config = {}
    if os.path.isfile(PATH_TO_INIT_FILE):
        config = ConfigParser()
        config.read(PATH_TO_INIT_FILE)
        if config.has_section(section):
            for element in config.items(section):
                dict_config[element[0]] = element[1]
        else:
            print("No section: " + str(section))
            return False, dict_config

        if len(dict_config) != 0:
            return True, dict_config
        else:
            print("Empty section")
            return False, dict_config
    else:
        print("File or directory not exist, adapt configParser.PATH_TO_INIT_FILE")
        return False, dict_config


def main():
    read_successful, cfg = get_configuration("database")
    print("Erfolgreich: " + str(read_successful) + " / " + str(cfg['user']))


if __name__ == "__main__":
    main()
