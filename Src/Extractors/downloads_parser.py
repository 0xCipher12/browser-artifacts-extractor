import sqlite3
import shutil
import csv
from pathlib import Path
from Src.utils import get_chrome_profile_dir, webkit_to_datetime

def extract_chrome_downloads(output_dir: Path) -> Path | None:
    profile_dir = get_chrome_profile_dir()
    if not profile_dir:
        print("[-] Chrome profile not found.")
        return None

    history_db_path = profile_dir / "History"
    if not history_db_path.exists():
        print("[-] Chrome History database not found.")
        return None

    temp_db_path = output_dir / "temp_downloads.db"
    shutil.copy2(history_db_path, temp_db_path)

    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()

    # Query the downloads table
    query = """
        SELECT 
            target_path, 
            tab_url, 
            received_bytes, 
            total_bytes, 
            start_time, 
            state 
        FROM downloads;
    """

    extracted_downloads = []
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            target_path, tab_url, received_bytes, total_bytes, start_time, state = row
            readable_time = webkit_to_datetime(start_time)
            
            # State translation map for Chrome downloads
            state_map = {0: "Complete", 1: "In Progress", 2: "Cancelled", 3: "Interrupted"}
            download_state = state_map.get(state, f"Unknown ({state})")

            extracted_downloads.append({
                "target_path": target_path,
                "source_url": tab_url,
                "received_bytes": received_bytes,
                "total_bytes": total_bytes,
                "start_time": readable_time,
                "state": download_state
            })
    except sqlite3.Error as e:
        print(f"[-] SQLite Error during downloads extraction: {e}")
    finally:
        conn.close()
        if temp_db_path.exists():
            temp_db_path.unlink()

    output_csv = output_dir / "chrome_downloads_report.csv"
    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["target_path", "source_url", "received_bytes", "total_bytes", "start_time", "state"])
        writer.writeheader()
        writer.writerows(extracted_downloads)

    print(f"[+] Extracted {len(extracted_downloads)} download records.")
    print(f"[+] Saved downloads report to: {output_csv}")
    return output_csv