import os
import psutil
import time


class NetworkCollector:
    def __init__(self, interface=None):
        # Default kept as None so the env var NETWORK_INTERFACE (if set) wins,
        # and falling back to a Linux-typical NIC name only when both are absent.
        # This preserves the original default of "wlp2s0" for existing setups
        # while making the value overridable per-node without editing code.
        self.interface = interface or os.getenv("NETWORK_INTERFACE") or "wlp2s0"
        self.last_rx = 0
        self.last_tx = 0
        self.last_time = 0
        self._warned_fallback = False

    def get_metrics(self):
        net_io_pernic = psutil.net_io_counters(pernic=True)

        if self.interface in net_io_pernic:
            net_io = net_io_pernic[self.interface]
        else:
            if not self._warned_fallback:
                print(
                    f"[network] Interface '{self.interface}' not found; "
                    "falling back to aggregate counters across all NICs. "
                    "Set NETWORK_INTERFACE in .env to silence this warning."
                )
                self._warned_fallback = True
            net_io = psutil.net_io_counters(pernic=False)

        current_time = time.time()
        current_rx = net_io.bytes_recv
        current_tx = net_io.bytes_sent

        if self.last_time == 0:
            self.last_rx = current_rx
            self.last_tx = current_tx
            self.last_time = current_time
            return {"rx_mbps": 0.0, "tx_mbps": 0.0}

        delta_time = current_time - self.last_time
        delta_rx = current_rx - self.last_rx
        delta_tx = current_tx - self.last_tx

        if delta_time <= 0:
            return {"rx_mbps": 0.0, "tx_mbps": 0.0}

        rx_mbps = (delta_rx * 8) / (delta_time * 1000 * 1000)
        tx_mbps = (delta_tx * 8) / (delta_time * 1000 * 1000)

        self.last_rx = current_rx
        self.last_tx = current_tx
        self.last_time = current_time

        return {
            "rx_mbps": round(rx_mbps, 2),
            "tx_mbps": round(tx_mbps, 2)
        }

if __name__ == "__main__":
    collector = NetworkCollector(interface="vmbr0") 

    print("Lần 1 (Khởi tạo, mong đợi ra 0):", collector.get_metrics())
    
    print("Đang chờ 2 giây để thu thập dữ liệu...")
    time.sleep(2) 
    
    print("Lần 2 (Sau 2 giây, mong đợi có tốc độ chuẩn):", collector.get_metrics())