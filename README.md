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

* **Database Disconnects:** Node-RED catches database errors without crashing the flow. Incoming telemetry continues to be published by the agent; messages that cannot be persisted during an outage may be lost unless MQTT buffering/persistence is configured.
* **Power Loss / Proxmox Reboot:** Zero manual intervention required. Systemd waits for the network and delays startup by 20 seconds (`ExecStartPre=/bin/sleep 20`) to allow the Proxmox environment to initialize.

## Challenges & Lessons Learned

* **Configuration Drift:** Initially, the project used both `.yaml` files and `.env` variables, leading to hardcoded values overriding dynamic ones during deployment. **Lesson:** Enforce a "Single Source of Truth" by migrating all configurations strictly to `.env`.
* **Ghost Data in Dashboards:** When decommissioning a test LXC node, its `device_id` remained in Grafana's dropdown menu because the historical data still existed in PostgreSQL. **Lesson:** Grafana queries the database for variables. Removing inactive devices requires either executing a SQL `DELETE` query or modifying the Grafana variable SQL to filter by active `$__timeFilter`.
* **Alerting Logic Precision:** Configuring Grafana Alerting required separating CPU and NVMe metrics into distinct Evaluation Groups. Relying on a single threshold for multiple data series caused false positives. **Lesson:** Always apply strict `Reduce (Last)` and precise `Threshold` conditions mapped to individual data streams to avoid alert fatigue.

---

# Homelab Telemetry Stack

Một hệ thống giám sát (Monitoring) thời gian thực dành cho máy chủ Proxmox/Linux, được xây dựng theo kiến trúc lấy cảm hứng từ các hệ thống Production (production-inspired). Hệ thống này không chỉ thu thập dữ liệu mà còn được thiết kế để tự động phục hồi sau sự cố mất điện, rớt mạng hoặc lỗi database.

## Hình ảnh thực tế (Dashboard Preview)

<img width="1749" height="999" alt="image" src="https://github.com/user-attachments/assets/d4678397-083d-4a36-9abe-e41140578212" />
*(Giao diện theo dõi thông số phần cứng Proxmox theo thời gian thực)*

## Kiến trúc hệ thống

Luồng dữ liệu trôi chảy theo chiều dọc như sau:

`[Python Agent] -> MQTT -> [Node-RED] -> PostgreSQL -> Grafana`

* **Python Agent (Client):** Chạy ngầm bằng `systemd` trên Proxmox Host, đọc thông số phần cứng (CPU, RAM, Nhiệt độ NVMe, Network TX/RX) và băm thành JSON.
* **MQTT Broker:** Trạm trung chuyển bản tin tốc độ cao.
* **Node-RED:** Đóng vai trò Data Pipeline, hứng dữ liệu từ MQTT, xử lý và đẩy vào Database. Được trang bị Catch Node để luồng không bị crash khi database có lỗi.
* **PostgreSQL:** Cơ sở dữ liệu quan hệ (Relational database) được sử dụng để lưu trữ dữ liệu telemetry theo thời gian.
* **Grafana:** Bảng điều khiển (Dashboard) trực quan hóa dữ liệu, hỗ trợ lọc theo từng thiết bị (`device_id`) và xử lý cảnh báo (Alerts).

## Cấu trúc thư mục

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

## Tính năng nổi bật

* **Khả năng tự phục hồi (Fault-Tolerant):** Tích hợp `Try-Catch` ở tầng code và cơ chế `Restart=always` của Systemd. Tự động kết nối lại khi Proxmox reboot.
* **Bảo mật & Tập trung (Single Source of Truth):** Loại bỏ hoàn toàn file cấu hình phụ. Toàn bộ IP, Port, Password, Device ID và chu kỳ quét được quản lý tập trung qua biến môi trường (`.env`).
* **Multi-Node Ready:** Dashboard Grafana được thiết kế sẵn Variable Dropdown. Cắm thêm bao nhiêu thiết bị (Raspberry Pi, VM, LXC) cũng tự động nhận diện và phân tách dữ liệu rõ ràng.
* **Cảnh báo Telegram:** Tích hợp sẵn luật cảnh báo trên Grafana. Tự động đẩy tin nhắn push về điện thoại khi CPU vượt ngưỡng 85% hoặc nhiệt độ NVMe trên 70°C, kèm thông báo "Resolved" khi hệ thống mát mẻ trở lại.

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

### 3. Cấu hình bảo mật & Hệ thống

Tạo file `.env` từ file mẫu. **Tuyệt đối không bao giờ commit file `.env` hoặc các file chứa thông tin nhạy cảm lên Git.**

```bash
cp .env.example .env
nano .env

```

Điền thông tin hệ thống của bạn vào:

```ini
MQTT_HOST=10.10.10.101
MQTT_PORT=1883
MQTT_TOPIC=homelab/telemetry/pve
MQTT_USERNAME=
MQTT_PASSWORD=
DEVICE_ID=homelab-pve
AGENT_INTERVAL=5

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

* **Mất kết nối Database:** Node-RED sẽ bắt lỗi qua Catch Node để không làm crash luồng. Agent vẫn tiếp tục publish dữ liệu; tuy nhiên, các bản tin gửi đi trong lúc DB chết có thể bị mất nếu chưa cấu hình lưu trữ/buffering trên MQTT.
* **Mất điện / Reboot Proxmox:** Không cần can thiệp thủ công. Systemd được cấu hình đợi mạng và delay thêm 20 giây (`ExecStartPre=/bin/sleep 20`) để môi trường Proxmox có thời gian khởi tạo các máy ảo/dịch vụ cần thiết.

## Thách thức & Bài học kinh nghiệm

* **Xung đột cấu hình (Configuration Drift):** Ban đầu, dự án sử dụng song song cả file `.yaml` và biến `.env`, dẫn đến việc các giá trị bị gán cứng (hardcode) đè lên cấu hình động lúc deploy. **Bài học:** Bắt buộc áp dụng nguyên tắc "Single Source of Truth" (Một nguồn chân lý duy nhất) bằng cách chuyển toàn bộ cấu hình sang `.env`.
* **Bóng ma dữ liệu (Ghost Data):** Khi xóa bỏ một node LXC test, tên của nó vẫn xuất hiện trong menu Dropdown của Grafana vì dữ liệu lịch sử vẫn tồn tại trong PostgreSQL. **Bài học:** Để menu hiển thị chính xác các thiết bị đang hoạt động, cần phải dọn dẹp trực tiếp trong DB (lệnh `DELETE`) hoặc thiết lập lại biến SQL trên Grafana để lọc theo thời gian thực (`$__timeFilter`).
* **Tinh chỉnh độ nhạy cảnh báo:** Việc cấu hình Grafana Alerting đòi hỏi phải tách biệt luồng dữ liệu CPU và NVMe. Nếu dùng chung một bẫy (Threshold) cho nhiều luồng dữ liệu sẽ gây ra hiện tượng spam tin nhắn sai lệch. **Bài học:** Cần nắm vững cơ chế rút gọn dữ liệu (`Reduce`) và thiết lập các điều kiện cảnh báo độc lập cho từng thông số để hệ thống hoạt động chính xác.
