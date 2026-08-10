import psutil

# First call to psutil.cpu_percent(interval=None) always returns 0.0 because
# psutil needs a previous sample to compute the delta. We warm it up once at
# import time so the first measurement after the agent starts is meaningful.
psutil.cpu_percent(interval=None)

def get_cpu_metrics():
    cpu_percent = psutil.cpu_percent(interval=None)
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