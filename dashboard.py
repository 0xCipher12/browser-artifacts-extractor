import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Multi-Browser Forensic Dashboard", layout="wide")

st.title("🕵️‍♂️ Full-Spectrum Multi-Browser Forensic Dashboard")
st.markdown("Interactive analysis suite for extracted browser artifacts and carved binary data.")

output_dir = Path("Output")

# Sidebar Navigation & Global Browser Filter
st.sidebar.title("Navigation")
choice = st.sidebar.radio("Select View", ["Overview / Metrics", "Master Timeline", "Browsing History", "Downloads", "Cookies", "Carved Artifacts"])

st.sidebar.markdown("---")
st.sidebar.title("Data Source")
upload_mode = st.sidebar.radio("Load Reports From:", ["Local Output/ Folder", "Upload CSV Reports"])

dfs_history, dfs_downloads, dfs_cookies, dfs_carved, df_timeline = None, None, None, None, None

if upload_mode == "Upload CSV Reports":
    st.sidebar.info("Upload your extracted CSV files from the Output folder.")
    uploaded_files = st.sidebar.file_uploader("Upload CSVs", accept_multiple_files=True, type=["csv"])
    
    history_list, downloads_list, cookies_list, carved_list = [], [], [], []
    
    if uploaded_files:
        for file in uploaded_files:
            fname = file.name.lower()
            if "history" in fname:
                history_list.append(pd.read_csv(file))
            elif "downloads" in fname:
                downloads_list.append(pd.read_csv(file))
            elif "cookies" in fname:
                cookies_list.append(pd.read_csv(file))
            elif "carved" in fname:
                carved_list.append(pd.read_csv(file))
            elif "timeline" in fname:
                df_timeline = pd.read_csv(file)
        
        df_history = pd.concat(history_list, ignore_index=True) if history_list else None
        df_downloads = pd.concat(downloads_list, ignore_index=True) if downloads_list else None
        df_cookies = pd.concat(cookies_list, ignore_index=True) if cookies_list else None
        df_carved = pd.concat(carved_list, ignore_index=True) if carved_list else None
else:
    # Load from local Output folder
    def load_combined_report(pattern):
        dfs = []
        if output_dir.exists():
            for file_path in output_dir.glob(pattern):
                try:
                    dfs.append(pd.read_csv(file_path))
                except Exception:
                    continue
        return pd.concat(dfs, ignore_index=True) if dfs else None

    df_history = load_combined_report("*_history_report.csv")
    df_downloads = load_combined_report("*_downloads_report.csv")
    df_cookies = load_combined_report("*_cookies_report.csv")
    df_carved = load_combined_report("*_carved_artifacts_report.csv")
    
    timeline_path = output_dir / "chrome_master_timeline.csv"
    if timeline_path.exists():
        df_timeline = pd.read_csv(timeline_path)

# Browser filter setup
available_browsers = []
if df_history is not None and "browser" in df_history.columns:
    available_browsers = df_history["browser"].unique().tolist()

selected_browsers = st.sidebar.multiselect("Filter by Browser", available_browsers, default=available_browsers)

def filter_by_browser(df):
    if df is not None and "browser" in df.columns and selected_browsers:
        return df[df["browser"].isin(selected_browsers)]
    return df

f_history = filter_by_browser(df_history)
f_downloads = filter_by_browser(df_downloads)
f_cookies = filter_by_browser(df_cookies)
f_carved = filter_by_browser(df_carved)
f_timeline = filter_by_browser(df_timeline)

if choice == "Overview / Metrics":
    st.header("Executive Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("History Visits", len(f_history) if f_history is not None else 0)
    with col2:
        st.metric("Downloads", len(f_downloads) if f_downloads is not None else 0)
    with col3:
        st.metric("Cookies", len(f_cookies) if f_cookies is not None else 0)
    with col4:
        st.metric("Carved Artifacts", len(f_carved) if f_carved is not None else 0)

elif choice == "Master Timeline":
    st.header("🕒 Unified Chronological Master Timeline")
    if f_timeline is not None:
        search = st.text_input("Search timeline events:")
        filtered_df = f_timeline[f_timeline.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)] if search else f_timeline
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.warning("Master timeline report not found or uploaded.")

elif choice == "Browsing History":
    st.header("🌐 Browsing History Records")
    if f_history is not None:
        search = st.text_input("Search history (URL or Title):")
        filtered_df = f_history[f_history.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)] if search else f_history
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.warning("History reports not found or uploaded.")

elif choice == "Downloads":
    st.header("📥 Download Records")
    if f_downloads is not None:
        st.dataframe(f_downloads, use_container_width=True)
    else:
        st.warning("Downloads reports not found or uploaded.")

elif choice == "Cookies":
    st.header("🍪 Extracted Cookies")
    if f_cookies is not None:
        search = st.text_input("Search host key / cookie name:")
        filtered_df = f_cookies[f_cookies.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)] if search else f_cookies
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.warning("Cookies reports not found or uploaded.")

elif choice == "Carved Artifacts":
    st.header("🔍 Low-Level Binary Carved Artifacts (Deleted/Residual)")
    if f_carved is not None:
        search = st.text_input("Search carved URLs:")
        filtered_df = f_carved[f_carved.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)] if search else f_carved
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.warning("Carved artifacts reports not found or uploaded.")