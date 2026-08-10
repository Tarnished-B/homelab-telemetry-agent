# Homelab Telemetry Stack

A real-time monitoring system for Proxmox/Linux servers, designed with production-oriented practices. This system extracts, transports, and visualizes hardware metrics, ensuring automatic recovery from power loss, network drops, or database issues.

## Dashboard Preview

<img width="1749" height="999" alt="image" src="https://github.com/user-attachments/assets/83ca7e29-af13-4993-8135-8cf5c71779cc" />
*(Screenshot of the real-time Proxmox hardware monitoring dashboard)*

## Architecture

Data flows vertically as follows:

`[Python Agent] -> MQTT -> [Node-RED] -> PostgreSQL -> Grafana`

* **Python Agent (Client):** Runs as a background systemd service on the Proxmox Host, extracts hardware metrics (CPU, RAM, NVMe Temp, Network TX/RX), and packages them into JSON payloads.
* **MQTT Broker:** High-speed message transport layer.
* **Node-RED:** Acts as the data pipeline, subscribing to MQTT, processing payloads, and inserting them into the database. Equipped with Catch Nodes to prevent pipeline crashes during database downtime.
* **PostgreSQL:** Relational database used to store timestamped telemetry data.
* **Grafana:** Visualization dashboard featuring dynamic device filtering (`device_id`) and Telegram alerting.

## Project Structure

```text
homelab-telemetry-agent/
├── monitor/
│   ├── collectors/
│   │   ├── cpu.py
│   │   ├── memory.py
│   │   ├── disk.py
│   │   └── network.py
│   ├── publisher/
│   │   └── mqtt_client.py
│   └── main.py
├── .env.example
├── .gitignore
├── requirements.txt
├── homelab-agent.service
└── README.md
```

## Highlights

* **Fault-Tolerant:** Implements code-level `try-except` blocks and a robust `Restart=always` systemd policy. Automatically recovers after Proxmox reboots or temporary disconnections.
* **Secure Configuration (Single Source of Truth):** No hardcoded credentials or external yaml files. All sensitive IPs, ports, device IDs, and intervals are managed centrally via a `.env` file.
* **Multi-Node Ready:** The Grafana dashboard is pre-configured with Variable Dropdowns. You can deploy this agent across multiple nodes (Raspberry Pis, VMs, LXCs) and seamlessly filter data per device without overlapping metrics.
* **Telegram Alerts:** Real-time push notifications integrated via Grafana Alerting. Automatically notifies you when CPU usage exceeds 85% or NVMe temperature crosses 70°C, and sends a "Resolved" message when the system stabilizes.

## Deployment Guide

### 1. Prerequisites

* Python 3.x
* Pre-configured MQTT Broker, Node-RED, PostgreSQL, and Grafana instances.

### 2. Node Agent Setup

Clone the repository and install dependencies:

```bash
git clone <your-github-link>
cd homelab-telemetry-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Security & Agent Configuration

Create a `.env` file from the provided example. **Never commit `.env` or other files containing credentials to version control.**

```bash
cp .env.example .env
nano .env
```

Populate it with your environment details:

```ini
MQTT_HOST=10.10.10.101
MQTT_PORT=1883
MQTT_TOPIC=homelab/telemetry/pve
MQTT_USERNAME=
MQTT_PASSWORD=
DEVICE_ID=homelab-pve
AGENT_INTERVAL=5
OS_TYPE=linux
```

Available variables:

| Variable | Required | Default | Description |
|---|---|---|---|
| `MQTT_HOST` | Yes | `127.0.0.1` | MQTT broker address |
| `MQTT_PORT` | No | `1883` | MQTT broker port |
| `MQTT_TOPIC` | Yes | `homelab/telemetry/default` | Publish topic |
| `MQTT_USERNAME` | No | _empty_ | Set to enable auth |
| `MQTT_PASSWORD` | No | _empty_ | Set to enable auth |
| `DEVICE_ID` | Yes | `unknown_device` | Unique ID for this node (used by Grafana variable) |
| `AGENT_INTERVAL` | No | `5` | Collection interval in seconds |
| `OS_TYPE` | No | `linux` | OS label included in payload |
| `NETWORK_INTERFACE` | No | `wlp2s0` | NIC to monitor. Defaults to `wlp2s0` because the reference setup runs Proxmox over WiFi on a mini-PC/laptop. Set to `vmbr0`/`eth0`/`eno1` for wired/LAN nodes. Falls back to aggregate counters when missing. |

### 4. Systemd Service Setup

Copy the configuration file `homelab-agent.service` to `/etc/systemd/system/`.
Start and enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable homelab-agent.service
sudo systemctl start homelab-agent.service
```

## Disaster Recovery

* **Database Disconnects:** Node-RED catches database errors without crashing the flow. Incoming telemetry continues to be published by the agent; messages that cannot be persisted during an outage may be lost unless MQTT buffering/persistence is configured.
* **Power Loss / Proxmox Reboot:** Zero manual intervention required. Systemd waits for the network and delays startup by 20 seconds (`ExecStartPre=/bin/sleep 20`) to allow the Proxmox environment to initialize.

## Challenges & Lessons Learned

* **Configuration Drift:** Initially, the project used both `.yaml` files and `.env` variables, leading to hardcoded values overriding dynamic ones during deployment. **Lesson:** Enforce a "Single Source of Truth" by migrating all configurations strictly to `.env`.
* **Ghost Data in Dashboards:** When decommissioning a test LXC node, its `device_id` remained in Grafana's dropdown menu because the historical data still existed in PostgreSQL. **Lesson:** Grafana queries the database for variables. Removing inactive devices requires either executing a SQL `DELETE` query or modifying the Grafana variable SQL to filter by active `$__timeFilter`.
* **Alerting Logic Precision:** Configuring Grafana Alerting required separating CPU and NVMe metrics into distinct Evaluation Groups. Relying on a single threshold for multiple data series caused false positives. **Lesson:** Always apply strict `Reduce (Last)` and precise `Threshold` conditions mapped to individual data streams to avoid alert fatigue.

---

# Homelab Telemetry Stack (Tiếng Việt)

Hệ thống giám sát (Monitoring) thời gian thực dành cho máy chủ Proxmox/Linux, được xây dựng theo kiến trúc lấy cảm hứng từ các hệ thống Production. Hệ thống không chỉ thu thập dữ liệu mà còn được thiết kế để tự động phục hồi sau sự cố mất điện, rớt mạng hoặc lỗi database.

## Hình ảnh thực tế

<img width="1749" height="999" alt="image" src="https://github.com/user-attachments/assets/d4678397-083d-4a36-9abe-e41140578212" />
*(Giao diện theo dõi thông số phần cứng Proxmox theo thời gian thực)*

## Kiến trúc

`[Python Agent] -> MQTT -> [Node-RED] -> PostgreSQL -> Grafana`

* **Python Agent:** Chạy ngầm bằng `systemd` trên Proxmox Host, đọc thông số phần cứng (CPU, RAM, Nhiệt độ NVMe, Network TX/RX) và đóng gói thành JSON.
* **MQTT Broker:** Trạm trung chuyển bản tin tốc độ cao.
* **Node-RED:** Data Pipeline, hứng dữ liệu từ MQTT, xử lý và đẩy vào Database. Có Catch Node để luồng không crash khi database lỗi.
* **PostgreSQL:** Lưu trữ dữ liệu telemetry theo thời gian.
* **Grafana:** Dashboard trực quan hóa dữ liệu, hỗ trợ lọc theo `device_id` và gửi cảnh báo.

## Hướng dẫn triển khai

### Chuẩn bị

* Python 3.x
* Đã dựng sẵn MQTT Broker, Node-RED, PostgreSQL và Grafana.

### Cài đặt Agent trên Node

```bash
git clone <link-github-cua-ban>
cd homelab-telemetry-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Cấu hình bảo mật & hệ thống

**Tuyệt đối không commit file `.env` hoặc các file chứa thông tin nhạy cảm lên Git.**

```bash
cp .env.example .env
nano .env
```

```ini
MQTT_HOST=10.10.10.101
MQTT_PORT=1883
MQTT_TOPIC=homelab/telemetry/pve
MQTT_USERNAME=
MQTT_PASSWORD=
DEVICE_ID=homelab-pve
AGENT_INTERVAL=5
OS_TYPE=linux
```

Bảng biến:

| Biến | Bắt buộc | Mặc định | Mô tả |
|---|---|---|---|
| `MQTT_HOST` | Có | `127.0.0.1` | Địa chỉ MQTT broker |
| `MQTT_PORT` | Không | `1883` | Port MQTT |
| `MQTT_TOPIC` | Có | `homelab/telemetry/default` | Topic publish |
| `MQTT_USERNAME` | Không | _trống_ | Điền nếu broker yêu cầu auth |
| `MQTT_PASSWORD` | Không | _trống_ | Điền nếu broker yêu cầu auth |
| `DEVICE_ID` | Có | `unknown_device` | ID duy nhất cho node (Grafana dùng làm biến) |
| `AGENT_INTERVAL` | Không | `5` | Chu kỳ thu thập (giây) |
| `OS_TYPE` | Không | `linux` | Nhãn OS trong payload |
| `NETWORK_INTERFACE` | Không | `wlp2s0` | Card mạng cần đo. Mặc định `wlp2s0` vì setup tham chiếu chạy Proxmox qua WiFi trên mini-PC/laptop. Node dùng dây LAN thì đổi sang `vmbr0`/`eth0`/`eno1`. Không có sẽ fallback tổng hợp. |

### Thiết lập Systemd Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable homelab-agent.service
sudo systemctl start homelab-agent.service
```

## Cẩm nang cứu hộ

* **Mất kết nối Database:** Node-RED bắt lỗi qua Catch Node. Agent vẫn publish; tin nhắn gửi đi trong lúc DB chết có thể mất nếu chưa cấu hình buffer MQTT.
* **Mất điện / Reboot Proxmox:** Không cần can thiệp. Systemd đợi mạng và delay 20 giây để Proxmox kịp khởi tạo.

## Thách thức & bài học

* **Configuration Drift:** Ban đầu dùng song song `.yaml` và `.env`, giá trị hardcode đè lên cấu hình động lúc deploy. **Bài học:** Áp dụng "Single Source of Truth" — toàn bộ config chỉ qua `.env`.
* **Ghost Data:** Khi xóa một LXC test, tên vẫn hiện trong dropdown Grafana vì data lịch sử còn trong DB. **Bài học:** Chạy `DELETE` trong DB hoặc lọc biến SQL Grafana theo `$__timeFilter`.
* **Alerting Logic Precision:** Cần tách luồng CPU và NVMe ra Evaluation Groups riêng. **Bài học:** Thiết lập `Reduce (Last)` + `Threshold` độc lập cho từng chỉ số để tránh alert fatigue.