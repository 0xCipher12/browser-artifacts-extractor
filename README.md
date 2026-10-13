# Pro-Grade Chrome Browser Forensic Extractor & Carver

A robust, Python-based digital forensics utility designed to extract active and deleted artifacts from Chromium-based browsers (starting with Google Chrome).

## Features
- **Active Artifact Extraction**: Parses SQLite databases (`History`, `Cookies`) and JSON files (`Bookmarks`) for active browsing data, downloads, and sessions.
- **Safe Database Snapshotting**: Bypasses OS-level file locks by safely copying database instances and WAL/SHM companion files before querying.
- **Low-Level Binary Carving**: Scans unallocated SQLite space and database freelists using regular expression heuristics to recover residual/deleted URLs and items (`700+` unique artifacts recovered).
- **Chronological Timeline Generation**: Merges history visits, downloads, and artifacts into a unified, time-sorted master forensic timeline report (`chrome_master_timeline.csv`).
- **Cross-Platform Profile Detection**: Automatically locates user profiles across Windows environments.

## Project Structure