import sqlite3
import shutil
import csv
from pathlib import Path
from Src.utils import get_chrome_profile_dir, webkit_to_datetime

def extract_chrome_cookies(output_dir: Path) -> Path | None:
    profile_dir = get_chrome_profile_dir()
    if not profile_dir:
        print("[-] Chrome profile not found.")
        return None

    cookies_db_path = profile_dir / "Network" / "Cookies"
    if not cookies_db_path.exists():
        cookies_db_path = profile_dir / "Cookies"
        if not cookies_db_path.exists():
            print("[-] Chrome Cookies database not found.")
            return None

    temp_db_path = output_dir / "temp_cookies.db"
    
    try:
        shutil.copy2(cookies_db_path, temp_db_path)
        for ext in ["-wal", "-shm"]:
            companion = Path(str(cookies_db_path) + ext)
            if companion.exists():
                shutil.copy2(companion, Path(str(temp_db_path) + ext))
    except PermissionError:
        print("[-] ERROR: Chrome is currently open and locking the Cookies file.")
        print("[*] Please close Google Chrome completely and run the script again.")
        return None

    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()

    query = """
        SELECT 
            host_key, 
            name, 
            path, 
            expires_utc, 
            is_secure, 
            is_httponly 
        FROM cookies;
    """

    extracted_cookies = []
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            host_key, name, path, expires_utc, is_secure, is_httponly = row
            readable_expiry = webkit_to_datetime(expires_utc)

            extracted_cookies.append({
                "host_key": host_key,
                "cookie_name": name,
                "path": path,
                "expires_utc": readable_expiry,
                "is_secure": bool(is_secure),
                "is_httponly": bool(is_httponly)
            })
    except sqlite3.Error as e:
        print(f"[-] SQLite Error during cookies extraction: {e}")
    finally:
        conn.close()
        if temp_db_path.exists():
            temp_db_path.unlink()
        for ext in ["-wal", "-shm"]:
            comp = Path(str(temp_db_path) + ext)
            if comp.exists():
                comp.unlink()

    output_csv = output_dir / "chrome_cookies_report.csv"
    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["host_key", "cookie_name", "path", "expires_utc", "is_secure", "is_httponly"])
        writer.writeheader()
        writer.writerows(extracted_cookies)

    print(f"[+] Extracted {len(extracted_cookies)} cookie records.")
    print(f"[+] Saved cookies report to: {output_csv}")
    return output_csv