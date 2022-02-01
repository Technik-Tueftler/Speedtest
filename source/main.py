#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from dataclasses import dataclass
import time
from configParser import get_configuration
from configParser import get_int_element as int_cfg
from fritzconnection.lib.fritzstatus import FritzStatus

read_successful, cfg = get_configuration("fritzbox")
fc = FritzStatus(address=cfg["address"], password=cfg["password"])


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
        if self._timer_run is False: return False
        if (time.time() - self._start_time) < self._runtime:
            print(time.time() - self._start_time)
            return True
        else:
            self._timer_run = False
            return False


def check_low_network_load() -> bool:
    total_upstream_raw, total_downstream_raw = 0, 0
    for _ in range(int_cfg("function_trigger", "loop_count")):
        upstream_raw, downstream_raw = fc.transmission_rate
        total_upstream_raw += upstream_raw
        total_downstream_raw += downstream_raw
        time.sleep(2)
    if int(total_upstream_raw*8/1024/1024/10) > int_cfg("function_trigger", "thr_upload_for_run"): return False
    if int(total_downstream_raw*8/1024/1024/10) > int_cfg("function_trigger", "thr_download_for_run"): return False
    return True


def main():
    pass


if __name__ == "__main__":
    main()
