# Homelab Telemetry Stack

A real-time monitoring system for Proxmox/Linux servers, built with a production-ready IoT architecture. This system is designed for high availability, ensuring automatic recovery from power loss, network drops, or database crashes.

## Architecture

Data flows vertically as follows:

`[Python Agent] -> MQTT -> [Node-RED] -> PostgreSQL -> Grafana`

* **Python Agent (Client):** Runs as a background systemd service on the Proxmox Host, extracts hardware metrics (CPU, RAM, NVMe Temp, Network TX/RX), and packages them into JSON payloads.
* **MQTT Broker:** High-speed message transport layer.
* **Node-RED:** Acts as the data pipeline, subscribing to MQTT, processing payloads, and inserting them into the database. Equipped with Catch Nodes to prevent pipeline congestion during database downtime.
* **PostgreSQL:** Time-series database for metric storage.
* **Grafana:** Visualization dashboard featuring dynamic device filtering (`device_id`).

## Highlights

* **Fault-Tolerant:** Implements code-level `try-except` blocks and a robust `Restart=always` systemd policy (with network-wait delays). Automatically recovers after Proxmox reboots or temporary disconnections.
* **Secure Configuration:** No hardcoded credentials. All sensitive IPs, ports, and passwords are managed via a `.env` file (excluded from version control via `.gitignore`).
* **Multi-Node Ready:** The Grafana dashboard is pre-configured with Variable Dropdowns. You can deploy this agent across multiple nodes (Raspberry Pis, VMs, LXCs) and seamlessly filter data per device without overlapping metrics.

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

### 3. Security Configuration

Create a `.env` file in the root directory (this file is ignored by Git) and populate it with your environment details:

```ini
MQTT_HOST=10.10.10.101
MQTT_PORT=1883
MQTT_TOPIC=homelab/telemetry/pve
# Add username/password if required

```

### 4. Systemd Service Setup

Copy the configuration file `homelab-agent.service` to `/etc/systemd/system/`.
Start and enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable homelab-agent.service
sudo systemctl start homelab-agent.service

```

## Disaster Recovery

* **Database Disconnects:** Node-RED will safely route errors through the Catch Node. The agent will continue publishing without crashing. Once the DB is online, the flow automatically resumes.
* **Power Loss / Proxmox Reboot:** Zero manual intervention required. The systemd service is configured to wait for the network and PVE-guests to fully initialize (`ExecStartPre=/bin/sleep 20`) before starting the agent.
* **Check Agent Status:**
```bash
sudo systemctl status homelab-agent

```


* **View Real-time Error Logs:**
```bash
journalctl -u homelab-agent -f

```



---

# Homelab Telemetry Stack

Một hệ thống giám sát (Monitoring) thời gian thực dành cho máy chủ Proxmox/Linux, được xây dựng theo kiến trúc IoT chuẩn Production. Hệ thống này không chỉ lấy dữ liệu mà còn được thiết kế để "sống dai", tự động phục hồi sau sự cố mất điện, rớt mạng hoặc sập database.

## Kiến trúc hệ thống

Luồng dữ liệu trôi chảy theo chiều dọc như sau:

`[Python Agent] -> MQTT -> [Node-RED] -> PostgreSQL -> Grafana`

* **Python Agent (Client):** Chạy ngầm bằng `systemd` trên Proxmox Host, đọc thông số phần cứng (CPU, RAM, Nhiệt độ NVMe, Network TX/RX) và băm thành JSON.
* **MQTT Broker:** Trạm trung chuyển bản tin tốc độ cao.
* **Node-RED:** Đóng vai trò Data Pipeline, hứng dữ liệu từ MQTT, xử lý và đẩy vào Database. Được trang bị Catch Node để luồng không bị kẹt khi database có lỗi.
* **PostgreSQL:** Lưu trữ dữ liệu dạng Time-series.
* **Grafana:** Bảng điều khiển (Dashboard) trực quan hóa dữ liệu, hỗ trợ lọc theo từng thiết bị (`device_id`).

## Tính năng nổi bật

* **Bất tử (Fault-Tolerant):** Tích hợp `Try-Catch` ở tầng code và cơ chế `Restart=always` (kèm delay chờ mạng) của Systemd. Tự động kết nối lại khi Proxmox reboot.
* **Bảo mật cấu hình:** Không hardcode thông tin nhạy cảm. Toàn bộ IP, Port, Password được quản lý qua biến môi trường (`.env`).
* **Multi-Node Ready:** Dashboard Grafana được thiết kế sẵn Variable Dropdown. Cắm thêm bao nhiêu thiết bị (Raspberry Pi, VM, LXC) cũng tự động nhận diện và phân tách dữ liệu rõ ràng.

## Hướng dẫn Triển khai

### 1. Chuẩn bị

* Python 3.x
* Đã dựng sẵn MQTT Broker, Node-RED, PostgreSQL và Grafana.

### 2. Cài đặt Agent trên Node

Clone repo về máy và cài đặt thư viện:

```bash
git clone <link-github-cua-ban>
cd homelab-telemetry-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```

### 3. Cấu hình bảo mật

Tạo file `.env` (file này đã được chặn bởi `.gitignore`) và điền thông tin hệ thống của bạn:

```ini
MQTT_HOST=10.10.10.101
MQTT_PORT=1883
MQTT_TOPIC=homelab/telemetry/pve
# Thêm username/password nếu có

```

### 4. Thiết lập chạy ngầm (Systemd Service)

Copy file cấu hình `homelab-agent.service` vào `/etc/systemd/system/`.
Khởi động service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable homelab-agent.service
sudo systemctl start homelab-agent.service

```

## Cẩm nang Cứu hộ

* **Mất kết nối Database:** Node-RED sẽ tự động nuốt lỗi qua Catch Node, Agent vẫn bơm dữ liệu bình thường. Khi DB lên lại, luồng sẽ tự động thông.
* **Mất điện / Reboot Proxmox:** Không cần làm gì cả. Systemd được config đợi mạng và PVE-guests khởi động xong (`ExecStartPre=/bin/sleep 20`) rồi mới chạy Agent.
* **Kiểm tra trạng thái Agent:**
```bash
sudo systemctl status homelab-agent

```


* **Xem log lỗi thực tế:**
```bash
journalctl -u homelab-agent -f

```
