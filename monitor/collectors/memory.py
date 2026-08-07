import psutil

def get_memory_metrics():
    mem = psutil.virtual_memory()
    used_gb = round(mem.used / (1024 ** 3), 2)
    total_gb = round(mem.total / (1024 ** 3), 2)
    return {
        "used_gb": used_gb,
        "total_gb": total_gb,
        "percent": mem.percent
    }

if __name__ == "__main__":
    print(get_memory_metrics())