import time
import os
from dotenv import load_dotenv

from collectors.cpu import get_cpu_metrics
from collectors.disk import get_disk_metrics
from collectors.memory import get_memory_metrics
from collectors.network import NetworkCollector
from publisher.mqtt_client import MQTTPublisher

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(base_dir, '.env'))

def main():
    print("Đang khởi tạo Homelab Telemetry Agent...")
    
    mqtt_host = os.getenv("MQTT_HOST", "127.0.0.1")
    mqtt_port = int(os.getenv("MQTT_PORT", 1883))
    mqtt_topic = os.getenv("MQTT_TOPIC", "homelab/telemetry/default")
    agent_id = os.getenv("DEVICE_ID", "unknown_device")
    interval = int(os.getenv("AGENT_INTERVAL", 5))
    os_type = os.getenv("OS_TYPE", "linux")

    net_collector = NetworkCollector()
    publisher = MQTTPublisher(
        host=mqtt_host,
        port=mqtt_port,
        topic=mqtt_topic
    )
    publisher.connect()

    print(f"Bắt đầu thu thập dữ liệu mỗi {interval} giây. Nhấn Ctrl+C để thoát.")

    while True:
        try:
            payload = {
                "version": 1,
                "device_id": agent_id,
                "os": os_type,
                "timestamp": int(time.time()),
                "metrics": {
                    "cpu": get_cpu_metrics(),
                    "mem": get_memory_metrics(),
                    "disk": get_disk_metrics(),
                    "net": net_collector.get_metrics()
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