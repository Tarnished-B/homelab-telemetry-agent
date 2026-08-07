import json
import paho.mqtt.client as mqtt

class MQTTPublisher:
    def __init__(self, host, port, topic):
        self.host = host
        self.port = port
        self.topic = topic
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    def connect(self):
        print(f"Đang kết nối tới MQTT Broker tại {self.host}:{self.port}...")
        try:
            self.client.connect(self.host, self.port, 60)
            self.client.loop_start()
            print("Kết nối MQTT thành công!")
        except Exception as e:
            print(f"Lỗi kết nối MQTT: {e}")

    def publish(self, payload_dict):
        try:
            json_payload = json.dumps(payload_dict)
            self.client.publish(self.topic, json_payload)
            print(f"Đã gửi gói tin (size: {len(json_payload)} bytes) lên topic: {self.topic}")
        except Exception as e:
            print(f"Lỗi khi gửi dữ liệu: {e}")

if __name__ == "__main__":
    import time
    publisher = MQTTPublisher("10.10.10.101", 1883, "homelab/telemetry/test")
    publisher.connect()

    time.sleep(1)

    test_data = {"test_message": "Hello World From Window", "value": 123}
    publisher.publish(test_data)

    time.sleep(1)