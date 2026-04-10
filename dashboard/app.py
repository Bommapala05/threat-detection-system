# dashboard/app.py

import streamlit as st
import sqlite3
import pandas as pd
import pydeck as pdk
import random
import sys
import os

# Import DB functions
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db import authenticate_user, create_user, init_db
from config import DB_PATH


# Initialize database schema (creates users table if it doesn't exist)
init_db()

st.set_page_config(page_title="Threat Dashboard", layout="wide")

# =========================
# SESSION STATE INIT
# =========================
def get_query_param(key):
    if hasattr(st, "query_params"):
        return st.query_params.get(key, None)
    return st.experimental_get_query_params().get(key, [None])[0]

def set_query_param(key, value):
    if hasattr(st, "query_params"):
        st.query_params[key] = value
    else:
        st.experimental_set_query_params(**{key: value})

def clear_query_params():
    if hasattr(st, "query_params"):
        st.query_params.clear()
    else:
        st.experimental_set_query_params()

if 'logged_in' not in st.session_state:
    if get_query_param('auth') == 'active':
        st.session_state['logged_in'] = True
        st.session_state['username'] = get_query_param('user') or 'Node User'
    else:
        st.session_state['logged_in'] = False

if 'username' not in st.session_state:
    st.session_state['username'] = None

# =========================
# 🎨 HACKER UI STYLE & MATRIX BACKGROUND
# =========================
matrix_str = "".join([str(random.randint(0, 1)) for _ in range(3000)])

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

.stApp {{
    background-color: #02040a;
}}

.stApp::before {{
    content: "{matrix_str}{matrix_str}{matrix_str}";
    position: fixed;
    top: -200vh;
    left: 0;
    width: 100vw;
    height: 400vh;
    color: rgba(0, 255, 159, 0.12);
    font-size: 20px;
    font-family: 'Share Tech Mono', monospace;
    line-height: 1.2;
    word-break: break-all;
    z-index: 0;
    pointer-events: none;
    animation: rain 25s linear infinite;
}}

@keyframes rain {{
    0% {{ transform: translateY(0); }}
    100% {{ transform: translateY(50vh); }}
}}

h1, h2, h3, p, span, div {{
    font-family: 'Share Tech Mono', monospace !important;
}}

h1, h2, h3 {{
    color: #00ff9f;
    text-shadow: 0 0 10px #00ff9f;
}}

@keyframes pulse-border {{
  0% {{ box-shadow: 0 0 5px #00ff9f; }}
  50% {{ box-shadow: 0 0 15px #00ff9f, 0 0 20px #00ff9f; }}
  100% {{ box-shadow: 0 0 5px #00ff9f; }}
}}

[data-testid="stMetric"] {{
    background-color: rgba(2, 6, 23, 0.85) !important;
    padding: 20px;
    border-radius: 5px;
    border: 1px solid #00ff9f;
    animation: pulse-border 3s infinite;
    backdrop-filter: blur(10px);
}}

.stDataFrame {{
    border: 1px solid #00ff9f;
    box-shadow: 0 0 10px #00ff9f;
    background-color: rgba(2, 6, 23, 0.85) !important;
}}

.radar-container {{
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 20px;
}}
.radar {{
  position: relative;
  width: 150px;
  height: 150px;
  border-radius: 50%;
  border: 2px solid #00ff9f;
  background: 
    linear-gradient(90deg, rgba(0,255,159,0.1) 49%, #00ff9f 50%, rgba(0,255,159,0.1) 51%),
    linear-gradient(0deg, rgba(0,255,159,0.1) 49%, #00ff9f 50%, rgba(0,255,159,0.1) 51%),
    rgba(0, 255, 159, 0.05);
  box-shadow: 0 0 20px #00ff9f, inset 0 0 20px #00ff9f;
}}
.radar::before {{
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 75px;
  height: 75px;
  background: linear-gradient(45deg, rgba(0,255,159,0.9) 0%, transparent 60%);
  transform-origin: 0% 0%;
  border-radius: 0 100% 0 0;
  animation: scan 2s linear infinite;
}}
@keyframes scan {{
  0% {{ transform: rotate(0deg); }}
  100% {{ transform: rotate(360deg); }}
}}

/* Glowing Title (No Splitting) */
.glitch {{
  color: #00ff9f;
  font-size: 2.2em;
  font-weight: bold;
  text-shadow: 0 0 10px #00ff9f, 0 0 20px #00ff9f;
  margin-bottom: 0;
  white-space: nowrap;
  animation: gentle-flicker 3s infinite alternate;
}}
@keyframes gentle-flicker {{
  0% {{ text-shadow: 0 0 5px #00ff9f, 2px 0 #ff003c, -2px 0 #0051ff; }}
  50% {{ text-shadow: 0 0 10px #00ff9f; }}
  100% {{ text-shadow: 0 0 15px #00ff9f, -2px 0 #ff003c, 2px 0 #0051ff; }}
}}

/* CRT Scanline Overlay */
.stApp::after {{
    content: " ";
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.15) 50%);
    background-size: 100% 4px;
    z-index: 100;
    pointer-events: none;
}}
.scan-line {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 5px;
    background-color: rgba(0, 255, 159, 0.4);
    box-shadow: 0 0 15px rgba(0, 255, 159, 1);
    opacity: 0.5;
    animation: crt-scan 6s linear infinite;
    z-index: 101;
    pointer-events: none;
}}
@keyframes crt-scan {{
    0% {{ top: -10vh; }}
    100% {{ top: 110vh; }}
}}

/* Terminal Emulator */
.term-container {{
    background-color: rgba(0, 0, 0, 0.7);
    border: 1px solid #00ff9f;
    box-shadow: 0 0 10px #00ff9f;
    padding: 15px;
    height: 300px;
    overflow-y: auto;
    font-family: 'Share Tech Mono', monospace;
    color: #00ff9f;
    font-size: 14px;
    backdrop-filter: blur(5px);
}}
.term-line {{
    border-bottom: 1px solid rgba(0,255,159,0.2);
    padding: 4px 0;
}}
.term-critical {{
    color: #ff003c;
    text-shadow: 0 0 5px #ff003c;
    font-weight: bold;
}}
.term-high {{
    color: #ffd700;
}}

/* Tab Styling */
.stTabs [data-baseweb="tab-list"] {{
    gap: 20px;
}}
.stTabs [data-baseweb="tab"] {{
    height: 50px;
    white-space: pre-wrap;
    background-color: transparent;
    border-radius: 4px 4px 0px 0px;
    gap: 1px;
    padding-top: 10px;
    padding-bottom: 10px;
    color: rgba(0,255,159, 0.6);
}}
.stTabs [aria-selected="true"] {{
    background-color: rgba(0,255,159,0.1);
    border-bottom: 2px solid #00ff9f !important;
    color: #00ff9f !important;
}}
</style>
""", unsafe_allow_html=True)


# =========================
# AUTHENTICATION LOGIC
# =========================
def show_login_page():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 class='glitch' style='text-align:center;'>🛡️ SYSTEM ACCESS TERMINAL</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00ff9f; opacity: 0.8;'>PLEASE AUTHENTICATE TO INITIALIZE NEURAL LINK</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔒 LOGIN", "📝 REGISTER"])
        
        with tab1:
            st.markdown("### Establish Connection")
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Initialize Link"):
                if username and password:
                    if authenticate_user(username, password):
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = username
                        set_query_param("auth", "active")
                        set_query_param("user", username)
                        st.rerun()
                    else:
                        st.error("ACCESS DENIED: Invalid credentials.")
                else:
                    st.warning("Please enter username and password.")
                    
        with tab2:
            st.markdown("### Establish New Node")
            new_user = st.text_input("New Username", key="reg_user")
            new_pass = st.text_input("New Password", type="password", key="reg_pass")
            if st.button("Create Profile"):
                if new_user and new_pass:
                    if create_user(new_user, new_pass):
                        st.success("NODE ESTABLISHED! You can now authenticate via Login.")
                    else:
                        st.error("REGISTRATION FAILED: Username might already exist.")
                else:
                    st.warning("Please provide both username and password.")

# =========================
# MAIN DASHBOARD
# =========================
def show_dashboard():
    # 🧠 TITLE & RADAR
    col_radar, col_title, col_user = st.columns([1, 4.5, 1.2])
    with col_radar:
        st.markdown('<div class="radar-container"><div class="radar"></div></div>', unsafe_allow_html=True)
    with col_title:
        st.markdown("""
        <div style="text-align: center; width: 100%;">
            <h1 class="glitch" data-text="🛡️ CYBER THREAT COMMAND CENTER">🛡️ CYBER THREAT COMMAND CENTER</h1>
            <p style="color: rgba(255,255,255,0.6); font-family: 'Share Tech Mono', monospace; font-size: 14px; margin-top: 5px;">
                🔴 SYSTEM STATUS: ACTIVE MONITORING | NEURAL NET: ONLINE | RADAR: SCANNING
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col_user:
        import streamlit.components.v1 as components
        components.html(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
        body {{ background-color: transparent; margin: 0; padding: 0; }}
        #cyber-hud {{
            color: #00ff9f; font-family: 'Share Tech Mono', monospace; font-size: 13px; 
            border: 1px solid #00ff9f; padding: 10px; background: rgba(0,255,159,0.05); 
            box-shadow: inset 0 0 10px rgba(0, 255, 159, 0.2); border-radius: 5px;
            margin-bottom: 10px;
        }}
        </style>
        <div id="cyber-hud">
            <span style="opacity:0.7">AUTH:</span> <b style="color:#fff;">{st.session_state['username']}</b><br>
            <span style="opacity:0.7">NODE:</span> <b style="color:#fff;">127.0.0.1</b><br>
            <span style="opacity:0.7">SYNC:</span> <b style="color:#ff003c; text-shadow: 0 0 5px #ff003c;" id="time-span"></b>
        </div>
        <script>
        function updateTime() {{
            var now = new Date();
            var offsetMs = now.getTimezoneOffset() * 60 * 1000;
            var localNow = new Date(now.getTime() - offsetMs);
            document.getElementById('time-span').innerText = 
                localNow.toISOString().replace('T', ' ').substring(0, 19) + ":" + now.getMilliseconds().toString().padStart(3,'0');
        }}
        setInterval(updateTime, 47);
        updateTime();
        </script>
        """, height=85)
        
        if st.button("🔌 Sever Link (Logout)"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = None
            clear_query_params()
            st.rerun()

    # DB fetching
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql("SELECT * FROM alerts", conn)
    except:
        st.error("Database error. Make sure threats.db exists.")
        st.stop()
        
    try:
        blocked_df = pd.read_sql("SELECT * FROM blocked_ips", conn)
    except:
        blocked_df = pd.DataFrame(columns=["ip", "reason", "timestamp"])

    if df.empty:
        st.warning("No alerts yet. Run main.py first to populate the database.")
        st.stop()
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # -------------------------
    # 🗂️ TABBED INTERFACE
    # -------------------------
    tab_overview, tab_critical, tab_dist, tab_map = st.tabs([
        "📊 Overview & Terminal", 
        "🔥 Critical Threats", 
        "📈 Threat Distribution", 
        "🌍 Global Attacker Map"
    ])
    
    # TAB 1: OVERVIEW & TERMINAL
    with tab_overview:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🚨 Total Alerts", len(df))
        col2.metric("🌐 Unique Attackers", df["ip"].nunique())
        col3.metric("🔥 High Severity", len(df[df["severity"] == "HIGH"]))
        col4.metric("⛔ Blocked IPs", len(blocked_df))
        
        st.markdown("<br>", unsafe_allow_html=True)

        if not blocked_df.empty:
            st.subheader("⛔ Active OS Level Blocks")
            st.dataframe(blocked_df.tail(10), use_container_width=True)
            st.markdown("<br>", unsafe_allow_html=True)
        
        
        st.subheader("💻 Live Terminal Log")
        term_lines = []
        for _, row in df.tail(50).iterrows():
            color_class = "term-critical" if row['severity'] == "CRITICAL" else ("term-high" if row['severity'] == "HIGH" else "")
            term_lines.append(f"<div class='term-line'><span style='opacity:0.5'>sys-log :: {row['ip']} ::</span> <span class='{color_class}'>[{row['severity']}] {row['reason']}</span> -> {row['country']}</div>")

        term_html = f"<div class='term-container'>{''.join(term_lines[::-1])}</div>"
        st.markdown(term_html, unsafe_allow_html=True)
            
    # TAB 2: CRITICAL THREATS
    with tab_critical:
        st.subheader("🔥 Critical Threats")
        critical_df = df[df["severity"] == "CRITICAL"]
        if not critical_df.empty:
            st.dataframe(critical_df.tail(10), use_container_width=True)
        else:
            st.info("No critical threats detected")
    
    # TAB 3: THREAT DISTRIBUTION
    with tab_dist:
        st.subheader("📊 Threat Distribution")
        st.markdown(
            "**Color Legend:** <span style='color:#ff003c'>■ CRITICAL</span> | <span style='color:#ffd700'>■ HIGH</span> | "
            "<span style='color:#00ff9f'>■ MEDIUM</span> | <span style='color:#0051ff'>■ LOW</span>", 
            unsafe_allow_html=True
        )
        import altair as alt
        
        severity_counts = df["severity"].value_counts().reset_index()
        severity_counts.columns = ["severity", "count"]

        # Ensure all categories are represented
        all_severities = pd.DataFrame({"severity": ["CRITICAL", "HIGH", "MEDIUM", "LOW"]})
        severity_counts = pd.merge(all_severities, severity_counts, on="severity", how="left").fillna(0)
        severity_counts["count"] = severity_counts["count"].astype(int)

        # Sort by count descending so highest values are first
        severity_counts = severity_counts.sort_values(by="count", ascending=False).reset_index(drop=True)

        # Map colors based on severity
        color_map = {
            "CRITICAL": "#ff003c", # Red
            "HIGH": "#ffd700",     # Yellow
            "MEDIUM": "#00ff9f",   # Green
            "LOW": "#0051ff"       # Blue
        }
        severity_counts["color"] = severity_counts["severity"].map(lambda x: color_map.get(str(x).upper(), "#ffffff"))

        # Build strict Altair chart to enforce exact color bindings & sort order
        chart = alt.Chart(severity_counts).mark_bar().encode(
            x=alt.X("severity", sort=None, title="Severity Level"),
            y=alt.Y("count", title="Event Count"),
            color=alt.Color("color", scale=None)  # scale=None forces literal hex rendering
        ).properties(
            height=400
        )
        
        st.altair_chart(chart, use_container_width=True)
        
    # TAB 4: GLOBAL ATTACKER MAP
    with tab_map:
        st.subheader("🌍 3D Threat Topography")
        st.markdown(
            "**Map Legend:** "
            "<span style='color:rgb(255,0,60)'>🔴 Attack Source (Red)</span> "
            "➔ <span style='color:rgb(0,255,159)'>🟢 Defense Node (Green)</span>",
            unsafe_allow_html=True
        )
        map_df = df.dropna(subset=["lat", "lon"]).copy()
        map_df = map_df[map_df["lat"] != 0]

        # Defense server coordinates
        DEFENSE_LON = 78.4867
        DEFENSE_LAT = 17.3850

        if not map_df.empty:
            map_df["target_lon"] = DEFENSE_LON
            map_df["target_lat"] = DEFENSE_LAT

            globe_view = pdk.View(type="_GlobeView", controller=True)

            st.pydeck_chart(pdk.Deck(
                views=[globe_view],
                map_style=pdk.map_styles.DARK,
                initial_view_state=pdk.ViewState(
                    latitude=DEFENSE_LAT,
                    longitude=DEFENSE_LON,
                    zoom=0.5,
                    pitch=30,
                ),
                layers=[
                    pdk.Layer(
                        "ArcLayer",
                        data=map_df,
                        get_source_position="[lon, lat]",
                        get_target_position="[target_lon, target_lat]",
                        get_source_color=[255, 0, 60, 200],
                        get_target_color=[0, 255, 159, 255],
                        auto_highlight=True,
                        width_scale=2,
                        get_width=2,
                        pitch=30
                    ),
                    pdk.Layer(
                        "ScatterplotLayer",
                        data=map_df,
                        get_position='[lon, lat]',
                        get_radius=200000,
                        get_fill_color='[255, 0, 60, 200]', 
                        pickable=True,
                    ),
                    pdk.Layer(
                        "ScatterplotLayer",
                        data=[{"lon": DEFENSE_LON, "lat": DEFENSE_LAT}],
                        get_position='[lon, lat]',
                        get_radius=400000,
                        get_fill_color='[0, 255, 159, 255]',
                        pickable=True,
                    )
                ],
            ))
        else:
            st.info("No valid geo data to display.")

    # =========================
    # 🧠 FOOTER
    # =========================
    st.markdown("""
    <hr style="border-color: rgba(0, 255, 159, 0.3); margin-top: 50px;">
    <div style="display: flex; justify-content: space-between; align-items: center; color: rgba(0, 255, 159, 0.7); font-family: 'Share Tech Mono', monospace; font-size: 13px; padding: 10px 20px;">
        <div>&copy; 2026 Secured System | Advanced Threat Intelligence</div>
        <div>
            <a href="#" style="color: #00ff9f; text-decoration: none; margin-right: 15px; opacity: 0.8;">System Docs</a>
            <a href="#" style="color: #00ff9f; text-decoration: none; margin-right: 15px; opacity: 0.8;">API Access</a>
            <a href="#" style="color: #00ff9f; text-decoration: none; opacity: 0.8;">Enterprise Support</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Application entry point
if not st.session_state['logged_in']:
    show_login_page()
else:
    show_dashboard()