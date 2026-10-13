from pathlib import Path
from Src.utils import get_browser_profiles
from Src.Extractors.chrome_history import extract_history
from Src.Extractors.deleted_carver import carve_deleted_history
from Src.Extractors.universal_extractors import extract_universal_downloads, extract_universal_cookies
from Src.Extractors.timeline import generate_master_timeline

def main():
    print("=" * 60)
    print("  FULL-SPECTRUM MULTI-BROWSER FORENSIC EXTRACTOR & CARVER")
    print("=" * 60)

    output_dir = Path("Output")
    output_dir.mkdir(exist_ok=True)

    profiles = get_browser_profiles()
    if not profiles:
        print("[-] No supported browser profiles detected.")
        return

    print(f"[+] Discovered Browsers/Profiles: {list(profiles.keys())}\n")

    for browser_name, profile_path in profiles.items():
        print(f"=== Processing: {browser_name} ===")
        extract_history(browser_name, profile_path, output_dir)
        extract_universal_downloads(browser_name, profile_path, output_dir)
        extract_universal_cookies(browser_name, profile_path, output_dir)
        carve_deleted_history(browser_name, profile_path, output_dir)
        print("-" * 40)

    generate_master_timeline(output_dir)

    print("\n" + "=" * 60)
    print("[+] FULL-SPECTRUM EXTRACTION COMPLETE. All reports saved to /Output")
    print("=" * 60)

if __name__ == "__main__":
    main()