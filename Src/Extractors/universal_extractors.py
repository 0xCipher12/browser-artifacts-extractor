import sqlite3
import shutil
import csv
from pathlib import Path
from Src.utils import webkit_to_datetime

def extract_universal_downloads(browser_name: str, profile_dir: Path, output_dir: Path):
    history_db_path = profile_dir / "History"
    if not history_db_path.exists():
        return

    safe_name = browser_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
    temp_db_path = output_dir / f"temp_{safe_name}_downloads.db"
    
    try:
        shutil.copy2(history_db_path, temp_db_path)
    except PermissionError:
        return

    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()

    query = "SELECT target_path, tab_url, received_bytes, total_bytes, start_time, state FROM downloads;"
    extracted = []
    try:
        cursor.execute(query)
        for row in cursor.fetchall():
            target_path, tab_url, received_bytes, total_bytes, start_time, state = row
            state_map = {0: "Complete", 1: "In Progress", 2: "Cancelled", 3: "Interrupted"}
            extracted.append({
                "browser": browser_name,
                "target_path": target_path,
                "source_url": tab_url,
                "received_bytes": received_bytes,
                "total_bytes": total_bytes,
                "start_time": webkit_to_datetime(start_time),
                "state": state_map.get(state, "Unknown")
            })
    except sqlite3.Error:
        pass
    finally:
        conn.close()
        if temp_db_path.exists():
            temp_db_path.unlink()

    if extracted:
        output_csv = output_dir / f"{safe_name}_downloads_report.csv"
        with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["browser", "target_path", "source_url", "received_bytes", "total_bytes", "start_time", "state"])
            writer.writeheader()
            writer.writerows(extracted)
        print(f"[+] [{browser_name}] Extracted {len(extracted)} download records.")

def extract_universal_cookies(browser_name: str, profile_dir: Path, output_dir: Path):
    # Cookies are usually in Network/Cookies or directly in Cookies
    cookies_path = profile_dir / "Network" / "Cookies"
    if not cookies_path.exists():
        cookies_path = profile_dir / "Cookies"
        if not cookies_path.exists():
            return

    safe_name = browser_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
    temp_db_path = output_dir / f"temp_{safe_name}_cookies.db"
    
    try:
        shutil.copy2(cookies_path, temp_db_path)
    except PermissionError:
        return

    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()

    query = "SELECT host_key, name, path, expires_utc, is_secure, is_httponly FROM cookies;"
    extracted = []
    try:
        cursor.execute(query)
        for row in cursor.fetchall():
            host_key, name, path, expires_utc, is_secure, is_httponly = row
            extracted.append({
                "browser": browser_name,
                "host_key": host_key,
                "cookie_name": name,
                "path": path,
                "expires_utc": webkit_to_datetime(expires_utc),
                "is_secure": bool(is_secure),
                "is_httponly": bool(is_httponly)
            })
    except sqlite3.Error:
        pass
    finally:
        conn.close()
        if temp_db_path.exists():
            temp_db_path.unlink()

    if extracted:
        output_csv = output_dir / f"{safe_name}_cookies_report.csv"
        with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["browser", "host_key", "cookie_name", "path", "expires_utc", "is_secure", "is_httponly"])
            writer.writeheader()
            writer.writerows(extracted)
        print(f"[+] [{browser_name}] Extracted {len(extracted)} cookie records.")