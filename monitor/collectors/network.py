import psutil
import time

class NetworkCollector:
    def __init__(self):
        self.last_rx = 0
        self.last_tx = 0
        self.last_time = 0

    def get_metrics(self):
        net_io = psutil.net_io_counters()
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

        rx_mbps = (delta_rx * 8) / (delta_time * 1024 * 1024)
        tx_mbps = (delta_tx * 8) / (delta_time * 1024 * 1024)

        self.last_rx = current_rx
        self.last_tx = current_tx
        self.last_time = current_time

        return {
            "rx_mbps": round(rx_mbps, 2),
            "tx_mbps": round(tx_mbps, 2)
        }

if __name__ == "__main__":
    collector = NetworkCollector()

    print("Lần 1 (Khởi tạo, mong đợi ra 0):", collector.get_metrics())
    
    print("Đang chờ 2 giây để thu thập dữ liệu...")
    time.sleep(2) 
    
    print("Lần 2 (Sau 2 giây, mong đợi có tốc độ):", collector.get_metrics())