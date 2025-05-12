from datetime import datetime


def write_log(message: str, level: str = "INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level.upper()}] {message}\n"

    with open("SystemLog//Log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(log_entry)
