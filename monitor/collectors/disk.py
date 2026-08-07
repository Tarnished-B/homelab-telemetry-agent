import psutil

def get_disk_metrics():

    partition_data = []
    partitions = psutil.disk_partitions(all = False)

    for partition in partitions:
        if partition.fstype == '' or 'loop' in partition.device:
            continue

        try:
            usage = psutil.disk_usage(partition.mountpoint)
            partition_data.append({
                "mount": partition.mountpoint,
                "usage_percent": usage.percent
            })
        except PermissionError:
            continue

    nvme_temp = 0.0
    if hasattr(psutil, "sensors_temperatures"):
        temps = psutil.sensors_temperature()
        for sensor_name, entries in temps.items():
            if 'nvme' in sensor_name.lower():
                if len(entries) > 0:
                    nvme_temp = entries[0].current
                    break

    return {
        "partitions": partition_data,
        "nvme_temp_c": nvme_temp
    }

if __name__ == "__main__":
    print(get_disk_metrics())