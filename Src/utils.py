import os
import platform
from datetime import datetime
from pathlib import Path

def webkit_to_datetime(webkit_timestamp: int) -> str:
    """
    Converts a Chromium WebKit timestamp (microseconds since Jan 1, 1601)
    into a human-readable UTC datetime string.
    """
    WEBKIT_OFFSET_SECONDS = 11_644_473_600
    try:
        seconds = (webkit_timestamp / 1_000_000) - WEBKIT_OFFSET_SECONDS
        if seconds < 0:
            return "Invalid/Zero"
        dt = datetime.fromtimestamp(seconds, tz=datetime.now().astimezone().tzinfo)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, OverflowError, OSError):
        return "Unknown"

def get_browser_profiles() -> dict:
    """
    Robustly detects browser profiles across Windows for Chrome, Edge, Brave, 
    Opera, Vivaldi, and any generic Chromium-based browser.
    """
    profiles = {}
    current_os = platform.system()

    if current_os == "Windows":
        local_appdata = os.environ.get("LOCALAPPDATA")
        roaming_appdata = os.environ.get("APPDATA")
        
        local_path = Path(local_appdata) if local_appdata else None
        roaming_path = Path(roaming_appdata) if roaming_appdata else None

        # 1. Check known major browser paths explicitly
        if local_path:
            known_browsers = {
                "Google Chrome": local_path / "Google" / "Chrome" / "User Data" / "Default",
                "Microsoft Edge": local_path / "Microsoft" / "Edge" / "User Data" / "Default",
                "Brave Browser": local_path / "BraveSoftware" / "Brave-Browser" / "User Data" / "Default",
                "Vivaldi": local_path / "Vivaldi" / "User Data" / "Default",
            }
            for name, path in known_browsers.items():
                if path.exists() and (path / "History").exists():
                    profiles[name] = path

        if roaming_path:
            opera_path = roaming_path / "Opera Software" / "Opera Stable"
            if opera_path.exists() and (opera_path / "History").exists():
                profiles["Opera"] = opera_path

        # 2. Dynamic scan for any other Chromium-based browsers in LocalAppData
        if local_path:
            try:
                for entry in local_path.iterdir():
                    if entry.is_dir() and entry.name not in {"Google", "Microsoft", "BraveSoftware", "Vivaldi", "Temp", "Packages", "Application Data"}:
                        user_data_dir = entry / "User Data"
                        if user_data_dir.exists() and user_data_dir.is_dir():
                            default_profile = user_data_dir / "Default"
                            if default_profile.exists() and (default_profile / "History").exists():
                                profiles[f"{entry.name} (Default)"] = default_profile
            except Exception as e:
                print(f"[-] Error during dynamic browser scan: {e}")

    return profiles