import psutil

def get_cpu_metrics():
    cpu_percent = psutil.cpu_percent(interval = None)
    cpu_freq = psutil.cpu_freq().current

    temp_c = 0.0
    if hasattr(psutil, "sensors_temperatures"):
        temps = psutil.sensors_temperatures()
        if temps and 'coretemp' in temps:
            temp_c = temps['coretemp'][0].current

    return {
        "usage_percent": cpu_percent,
        "freq_mhz": cpu_freq,
        "temp_c": temp_c
    }

if __name__ == "__main__":
    print(get_cpu_metrics())