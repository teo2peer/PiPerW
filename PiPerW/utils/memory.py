"""Memory pressure helpers for Pi Zero 2 W (512 MB RAM)."""
from PiPerW.helpers import Log


def available_mb():
    """Return MemAvailable in MiB from /proc/meminfo. -1 if unavailable."""
    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    kb = int(line.split()[1])
                    return kb // 1024
    except (OSError, ValueError) as e:
        Log.warning(f"memory.available_mb failed: {e!r}")
    return -1


def under_pressure(threshold_mb=80):
    """True when MemAvailable < threshold. Returns False if unknown."""
    mb = available_mb()
    return 0 <= mb < threshold_mb
