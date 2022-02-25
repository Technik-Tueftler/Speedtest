#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from dataclasses import dataclass
import requests.exceptions
import time
import os
import threading
import speedtest
from fritzconnection.lib.fritzstatus import FritzStatus
from datetime import datetime


@dataclass
class Timer:
    _runtime: float = 0
    _start_time: float = time.time()
    _timer_run: bool = False

    @property
    def start_time(self) -> float:
        return self._start_time

    @property
    def runtime(self) -> float:
        return self._runtime

    @runtime.setter
    def runtime(self, value: float) -> None:
        if value <= 0:
            raise ValueError(f"{value} <-> only positive numbers allowed")
        self._runtime = value

    def start_timer(self) -> None:
        self._start_time = time.time()
        self._timer_run = True

    def extend_timer(self, extend_time: float) -> None:
        self._runtime += extend_time

    @property
    def timer_run(self) -> bool:
        if self._timer_run is False:
            return False
        if (time.time() - self._start_time) < self._runtime:
            # print(time.time() - self._start_time)
            return True
        else:
            self._timer_run = False
            return False


def run_timer(communication_interface: dict) -> None:
    time_handler = Timer()
    time_handler.runtime = communication_interface["timer_runtime"]
    time_handler.start_timer()
    while time_handler.timer_run:
        time.sleep(0.1)


def check_low_network_load(communication_interface: dict) -> None:
    # print("Starte")
    timer = Timer()
    timer.runtime = communication_interface["S_TIME_CHECK_LOW_NETWORK_LOAD"]
    timer.start_timer()
    total_upstream_raw, total_downstream_raw = 0, 0
    loop_count = 0
    while timer.timer_run:
        upstream_raw, downstream_raw = communication_interface["fritzbox_connector"].transmission_rate
        total_upstream_raw += upstream_raw
        total_downstream_raw += downstream_raw
        loop_count += 1
        time.sleep(1)
    # print(f"Upstream: {total_upstream_raw * 8 / 1024 / 1024 / loop_count}")
    # print(f"Downstream: {total_downstream_raw * 8 / 1024 / 1024 / loop_count}")
    current_upstream_raw_in_mbit = int(total_upstream_raw * 8 / 1024 / 1024 / loop_count)
    if current_upstream_raw_in_mbit > communication_interface["MBIT_THR_FROM_NETWORK_UPLOAD_TO_RUN"]:
        communication_interface["low_stream_rate"] = False

    current_downstream_raw_in_mbit = int(total_downstream_raw * 8 / 1024 / 1024 / loop_count)
    if current_downstream_raw_in_mbit > communication_interface["MBIT_THR_FROM_NETWORK_UPLOAD_TO_RUN"]:
        communication_interface["low_stream_rate"] = False
    communication_interface["low_stream_rate"] = True


def receive_network_load_from_fritzbox(communication_interface: dict) -> None:
    total_downstream_raw = list()
    total_upstream_raw = list()
    while communication_interface["speed_test_running"]:
        upstream_raw, downstream_raw = communication_interface["fritzbox_connector"].transmission_rate
        total_downstream_raw.append(round(downstream_raw * 8))
        total_upstream_raw.append(round(upstream_raw * 8))
        time.sleep(1)
    communication_interface["max_download_fritzbox"] = max(total_downstream_raw)
    communication_interface["max_upload_fritzbox"] = max(total_upstream_raw)
    communication_interface["last_run_datetime"] = datetime.now(). \
        strftime("%y-%m-%d %H:%M:%S")


def measure_connection_speed(communication_interface: dict) -> None:
    connection = speedtest.Speedtest()
    connection.get_best_server()
    download = connection.download()
    upload = connection.upload()
    ping = connection.results.ping
    communication_interface["speed_test_running"] = False
    communication_interface["avg_download_speedtest"] = round(download)
    communication_interface["avg_upload_speedtest"] = round(upload)
    communication_interface["ping_speedtest"] = round(ping)


def main(env_data: dict) -> None:
    communication = {"speed_test_running": False, "low_stream_rate": False, "timer_runtime": 2,
                     "max_download_fritzbox": 0, "max_upload_fritzbox": 0,
                     "avg_download_speedtest": 0, "avg_upload_speedtest": 0,
                     "ping_speedtest": 0,
                     "last_run_datetime": datetime.now().strftime("%y-%m-%d %H:%M:%S")} | env_data
    while True:
        timer_thread = threading.Thread(target=run_timer, args=(communication,))
        timer_thread.start()
        timer_thread.join()

        network_check_thread = threading.Thread(target=check_low_network_load, args=(communication,))
        network_check_thread.start()
        network_check_thread.join()

        print(f'Messung möglich: {communication["low_stream_rate"]}')
        if not communication["low_stream_rate"]:
            print("Timer verlängert auf eine Stunde")
            # Verlängern des Timers um 1 Stunde
            communication["timer_runtime"] = 3600
        else:
            print("Neue Speedtest-Messung")
            communication["low_stream_rate"] = False
            communication["speed_test_running"] = True
            measure_network_load_thread = threading.Thread(target=receive_network_load_from_fritzbox,
                                                           args=(communication,))
            receive_network_load_thread = threading.Thread(target=measure_connection_speed, args=(communication,))
            measure_network_load_thread.start()
            receive_network_load_thread.start()
            measure_network_load_thread.join()
            receive_network_load_thread.join()
            print(communication)
            print("Messung beendet")


def check_and_verify_env_variables() -> dict:
    environment_data = dict()
    ip_addr_fritzbox = os.getenv("IP_FRITZBOX", "fritz.box")
    environment_data["all_verified"] = True

    try:
        fritzbox_connector = FritzStatus(address=ip_addr_fritzbox)
        environment_data["fritzbox_connector"] = fritzbox_connector
        environment_data["all_verified"] &= True
    except requests.exceptions.ConnectTimeout as _:
        if os.getenv("IP_FRITZBOX") is None:
            print(f"ERROR: No address was given. Therefore the default value {ip_addr_fritzbox} "
                  f"was set. However, no connection could be established. Please enter a "
                  f"valid PI address.")
        else:
            print(f"ERROR: Can't connect to fritzbox! Please check the given IP address: "
                  f"{ip_addr_fritzbox}.")
        environment_data["all_verified"] &= False

    try:
        check_time_for_low_network_load = int(os.getenv('S_TIME_CHECK_LOW_NETWORK_LOAD', 10))
        environment_data["S_TIME_CHECK_LOW_NETWORK_LOAD"] = check_time_for_low_network_load
        environment_data["all_verified"] &= True
    except ValueError as err:
        environment_data["all_verified"] &= False
        print(f"ERROR: The value for the variable S_TIME_CHECK_LOW_NETWORK_LOAD is not an integer")

    try:
        mbit_thr_from_network_download_to_run = int(os.getenv('MBIT_THR_FROM_NETWORK_DOWNLOAD_TO_RUN', 10))
        environment_data["MBIT_THR_FROM_NETWORK_DOWNLOAD_TO_RUN"] = mbit_thr_from_network_download_to_run
        environment_data["all_verified"] &= True
    except ValueError as err:
        environment_data["all_verified"] &= False
        print(f"ERROR: The value for the variable MBIT_THR_FROM_NETWORK_DOWNLOAD_TO_RUN "
              f"is not an integer")

    try:
        mbit_thr_from_network_upload_to_run = int(os.getenv('MBIT_THR_FROM_NETWORK_UPLOAD_TO_RUN', 2))
        environment_data["MBIT_THR_FROM_NETWORK_UPLOAD_TO_RUN"] = mbit_thr_from_network_upload_to_run
        environment_data["all_verified"] &= True
    except ValueError as err:
        environment_data["all_verified"] &= False
        print(f"ERROR: The value for the variable MBIT_THR_FROM_NETWORK_UPLOAD_TO_RUN "
              f"is not an integer")

    return environment_data


if __name__ == "__main__":
    verified_env_data = check_and_verify_env_variables()
    if verified_env_data["all_verified"] is not False:
        main(verified_env_data)

