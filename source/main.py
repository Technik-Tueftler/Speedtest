from configParser import get_configuration
import time
from fritzconnection.lib.fritzstatus import FritzStatus


read_successful, cfg = get_configuration("fritzbox")


def main():
    fc = FritzStatus(address=cfg["adress"], password=cfg["password"])
    while True:
        upstream_raw, downstream_raw = fc.transmission_rate
        print(f"Upstream: {round((upstream_raw))}Byte/s -- Downstream: {round((downstream_raw))}Byte/s")
        print(f"Upstream: {round((upstream_raw*8))}Bit/s -- Downstream: {round((downstream_raw*8))}Bit/s")
        print(f"Upstream: {round((upstream_raw*8/1024))}KBit/s -- Downstream: {round((downstream_raw*8/1024))}KBit/s")
        print(f"Upstream: {round((upstream_raw*8/1024/1024))}MBit/s -- Downstream: {round((downstream_raw*8/1024/1024))}MBit/s")
        print("-----------------------------------------------------------")
        time.sleep(2)


if __name__ == '__main__':
    main()

