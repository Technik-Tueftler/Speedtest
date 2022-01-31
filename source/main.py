from configParser import get_configuration
from configParser import get_int_element as int_cfg
import time
from fritzconnection.lib.fritzstatus import FritzStatus
import asyncio

read_successful, cfg = get_configuration("fritzbox")

fc = FritzStatus(address=cfg["address"], password=cfg["password"])


async def check_low_network_load() -> bool:
    total_upstream_raw, total_downstream_raw = 0, 0
    for _ in range(int_cfg("function_trigger", "loop_count")):
        upstream_raw, downstream_raw = fc.transmission_rate
        total_upstream_raw += upstream_raw
        total_downstream_raw += downstream_raw
        time.sleep(2)
    if int(total_upstream_raw*8/1024/1024/10) > int_cfg("function_trigger", "thr_upload_for_run"): return False
    if int(total_downstream_raw*8/1024/1024/10) > int_cfg("function_trigger", "thr_download_for_run"): return False
    return True


async def main():
    task2 = asyncio.create_task(check_low_network_load())
    if await task2 is True:
        print("Starte Programm")

if __name__ == "__main__":
    asyncio.run(main())
