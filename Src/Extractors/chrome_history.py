import sqlite3
import shutil
import csv
from pathlib import Path
from Src.utils import webkit_to_datetime

def extract_history(browser_name: str, profile_dir: Path, output_dir: Path) -> Path | None:
    history_db_path = profile_dir / "History"
    if not history_db_path.exists():
        print(f"[-] {browser_name}: History database not found.")
        return None

    safe_name = browser_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
    temp_db_path = output_dir / f"temp_{safe_name}_history.db"
    
    try:
        shutil.copy2(history_db_path, temp_db_path)
        for ext in ["-wal", "-shm"]:
            companion = Path(str(history_db_path) + ext)
            if companion.exists():
                shutil.copy2(companion, Path(str(temp_db_path) + ext))
    except PermissionError:
        print(f"[-] ERROR: {browser_name} is currently open and locking the History file.")
        return None

    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()

    query = """
        SELECT 
            urls.url, 
            urls.title, 
            urls.visit_count, 
            urls.typed_count, 
            visits.visit_time 
        FROM urls 
        JOIN visits ON urls.id = visits.url;
    """

    extracted_records = []
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            url, title, visit_count, typed_count, raw_time = row
            readable_time = webkit_to_datetime(raw_time)
            extracted_records.append({
                "browser": browser_name,
                "url": url,
                "title": title if title else "No Title",
                "visit_count": visit_count,
                "typed_count": typed_count,
                "visit_time": readable_time
            })
    except sqlite3.Error as e:
        print(f"[-] SQLite Error for {browser_name}: {e}")
    finally:
        conn.close()
        if temp_db_path.exists():
            temp_db_path.unlink()
        for ext in ["-wal", "-shm"]:
            comp = Path(str(temp_db_path) + ext)
            if comp.exists():
                comp.unlink()

    output_csv = output_dir / f"{safe_name}_history_report.csv"
    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["browser", "url", "title", "visit_count", "typed_count", "visit_time"])
        writer.writeheader()
        writer.writerows(extracted_records)

    print(f"[+] [{browser_name}] Extracted {len(extracted_records)} browsing history records.")
    return output_csv