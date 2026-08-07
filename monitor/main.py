import time
import yaml

from collectors.cpu import get_cpu_metrics
from collectors.disk import get_disk_metrics
from collectors.memory import get_memory_metrics
from collectors.network import NetworkCollector

from publisher.mqtt_client import MQTTPublisher

def load_config(config_path="config/config.yaml"):
    with open(config_path, "r") as file:
        return yaml.safe_load(file)

def main():

    print("Đang khởi tạo Homelab Telemetry Agent...")
    config = load_config()
    agent_id = config['agent']['device_id']
    interval = config['agent']['interval_seconds']

    net_collector = NetworkCollector()
    publisher = MQTTPublisher(
        host=config['mqtt']['host'],
        port=config['mqtt']['port'],
        topic=config['mqtt']['topic']
    )
    publisher.connect()

    print(f"Bắt đầu thu thập dữ liệu mỗi {interval} giây. Nhấn Ctrl+C để thoát.")

    while True:
        try:
            cpu_data = get_cpu_metrics()
            mem_data = get_memory_metrics()
            disk_data = get_disk_metrics()
            net_data = net_collector.get_metrics()

            payload = {
                "version": 1,
                "device_id": agent_id,
                "os": "windows",
                "timestamp": int(time.time()),
                "metrics": {
                    "cpu": cpu_data,
                    "mem": mem_data,
                    "disk": disk_data,
                    "net": net_data
                }
            }

            publisher.publish(payload)

            time.sleep(interval)

        except KeyboardInterrupt:
            print("\nĐã dừng chương trình theo yêu cầu của người dùng.")
            break
        except Exception as e:
            print(f"Lỗi trong vòng lặp chính: {e}")
            time.sleep(interval)

if __name__ == "__main__":
    main()