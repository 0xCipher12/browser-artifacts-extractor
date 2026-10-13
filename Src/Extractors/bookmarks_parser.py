import json
import csv
from pathlib import Path
from Src.utils import get_chrome_profile_dir, webkit_to_datetime

def parse_bookmark_node(node, folder_path, extracted_bookmarks):
    if node.get("type") == "folder":
        current_path = f"{folder_path} / {node.get('name', 'Folder')}"
        for child in node.get("children", []):
            parse_bookmark_node(child, current_path, extracted_bookmarks)
    elif node.get("type") == "url":
        raw_time = int(node.get("date_added", 0))
        readable_time = webkit_to_datetime(raw_time) if raw_time > 0 else "Unknown"

        extracted_bookmarks.append({
            "folder_path": folder_path,
            "title": node.get("name", "No Title"),
            "url": node.get("url", ""),
            "date_added": readable_time
        })

def extract_chrome_bookmarks(output_dir: Path) -> Path | None:
    profile_dir = get_chrome_profile_dir()
    if not profile_dir:
        print("[-] Chrome profile not found.")
        return None

    bookmarks_file = profile_dir / "Bookmarks"
    if not bookmarks_file.exists():
        print("[*] Chrome Bookmarks file not found (No bookmarks in this profile).")
        return None

    try:
        with open(bookmarks_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[-] Error reading Bookmarks JSON: {e}")
        return None

    extracted_bookmarks = []
    roots = data.get("roots", {})
    
    for root_name, root_node in roots.items():
        parse_bookmark_node(root_node, f"Root/{root_name}", extracted_bookmarks)

    output_csv = output_dir / "chrome_bookmarks_report.csv"
    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["folder_path", "title", "url", "date_added"])
        writer.writeheader()
        writer.writerows(extracted_bookmarks)

    print(f"[+] Extracted {len(extracted_bookmarks)} bookmark records.")
    print(f"[+] Saved bookmarks report to: {output_csv}")
    return output_csv