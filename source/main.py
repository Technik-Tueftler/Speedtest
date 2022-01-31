from configParser import get_configuration
from configParser import get_int_element as int_cfg
import time
from fritzconnection.lib.fritzstatus import FritzStatus

read_successful, cfg = get_configuration("fritzbox")

fc = FritzStatus(address=cfg["address"], password=cfg["password"])


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
    while True:
        upstream_raw, downstream_raw = fc.transmission_rate
        print(f"Upstream: {round((upstream_raw))}Byte/s -- Downstream: {round((downstream_raw))}Byte/s")
        print(f"Upstream: {round((upstream_raw * 8))}Bit/s -- Downstream: {round((downstream_raw * 8))}Bit/s")
        print(f"Upstream: {round((upstream_raw * 8 / 1024))}KBit/s -- Downstream: {round((downstream_raw * 8 / 1024))}KBit/s")
        print(f"Upstream: {round((upstream_raw * 8 / 1024 / 1024))}MBit/s -- Downstream: {round((downstream_raw * 8 / 1024 / 1024))}MBit/s")
        print("-----------------------------------------------------------")
        time.sleep(2)


if __name__ == '__main__':
    # main()
    check_low_network_load()
