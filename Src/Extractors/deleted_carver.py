import shutil
import re
import csv
from pathlib import Path

def carve_deleted_history(browser_name: str, profile_dir: Path, output_dir: Path) -> Path | None:
    carved_artifacts = set()
    safe_name = browser_name.lower().replace(" ", "_").replace("(", "").replace(")", "")

    # Target databases to carve from
    db_files = ["History", "Cookies", "Web Data"]
    
    for db_file in db_files:
        db_path = profile_dir / db_file
        if not db_path.exists() and db_file == "Cookies":
            db_path = profile_dir / "Network" / "Cookies"

        if db_path.exists():
            temp_db = output_dir / f"temp_carve_{safe_name}_{db_file}.db"
            try:
                shutil.copy2(db_path, temp_db)
                with open(temp_db, "rb") as f:
                    content = f.read()
                
                # Regex for URLs and email/string patterns in unallocated space
                url_pattern = rb"https?://[^\s\"<>#%{}\\|\\^~\[\]`]+"
                for match in re.findall(url_pattern, content):
                    try:
                        carved_artifacts.add(match.decode("utf-8", errors="ignore"))
                    except Exception:
                        continue
            except Exception:
                pass
            finally:
                if temp_db.exists():
                    temp_db.unlink()

    output_csv = output_dir / f"{safe_name}_carved_artifacts_report.csv"
    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["browser", "carved_url"])
        writer.writeheader()
        for url in sorted(carved_artifacts):
            writer.writerow({"browser": browser_name, "carved_url": url})

    print(f"[+] [{browser_name}] Carved {len(carved_artifacts)} unique deleted/residual artifacts.")
    return output_csv