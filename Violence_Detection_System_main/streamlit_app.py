import streamlit as st
import requests
import tempfile
import os
import pandas as pd

# =================================================
# CONFIG
# =================================================

st.set_page_config(
    page_title="AI Violence Detection – Surveillance Dashboard",
    page_icon="🚨",
    layout="wide"
)

# Backend URL (works locally + deployment)
BASE = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")


# =================================================
# HELPERS
# =================================================

def backend_alive():
    try:
        r = requests.get(f"{BASE}/health", timeout=3)
        return r.status_code == 200
    except:
        return False


def get_json(endpoint):
    try:
        r = requests.get(f"{BASE}{endpoint}", timeout=5)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None


def severity_badge(sev):

    if sev == "HIGH":
        return "🟥 HIGH"

    if sev == "MEDIUM":
        return "🟨 MEDIUM"

    if sev == "LOW":
        return "🟩 LOW"

    return "⚪ UNKNOWN"


# =================================================
# SIDEBAR
# =================================================

st.sidebar.title("🚨 AI Violence Detection")

page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "🚨 Alerts",
        "📈 Analytics",
        "⚙️ System Status"
    ]
)


# =================================================
# DASHBOARD
# =================================================

if page == "📊 Dashboard":

    st.title("📊 Surveillance Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Backend Status",
        "ONLINE" if backend_alive() else "OFFLINE"
    )

    col2.metric(
        "Detection Mode",
        "AI + Motion"
    )

    col3.metric(
        "System",
        "ACTIVE"
    )

    st.divider()

    left, right = st.columns([1, 2])

    # -------------------------------------------
    # INPUT PANEL
    # -------------------------------------------

    with left:

        st.subheader("🎥 Video Input")

        uploaded = st.file_uploader(
            "Upload Video",
            type=["mp4", "avi", "mov", "mkv"]
        )

        video_url = st.text_input(
            "OR Paste Video URL"
        )

        analyze_btn = st.button(
            "🔍 Analyze Video",
            use_container_width=True
        )

    # -------------------------------------------
    # PREVIEW PANEL
    # -------------------------------------------

    with right:

        st.subheader("Preview")

        if uploaded:
            st.video(uploaded)

        elif video_url:
            st.info("Video will be analyzed from URL")

        else:
            st.info("Upload a video or paste a URL")

    # -------------------------------------------
    # ANALYSIS
    # -------------------------------------------

    if analyze_btn:

        if not backend_alive():

            st.error("Backend is offline")
            st.stop()

        files = {}
        data = {}

        if uploaded:

            tmp = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp4"
            )

            tmp.write(uploaded.read())
            tmp.close()

            files["video"] = open(tmp.name, "rb")

        elif video_url:

            data["video_url"] = video_url

        else:

            st.warning("Provide video or URL")
            st.stop()

        with st.spinner("Analyzing video..."):

            res = requests.post(
                f"{BASE}/analyze",
                files=files if files else None,
                data=data if data else None,
                timeout=600
            )

        if files:
            files["video"].close()
            os.unlink(tmp.name)

        result = res.json()

        if "error" in result:

            st.error(result["error"])
            st.stop()

        st.divider()

        # -------------------------------------------
        # RESULT DISPLAY
        # -------------------------------------------

        if result["is_violent"]:
            st.error("🚨 VIOLENCE DETECTED")
        else:
            st.success("✅ NO VIOLENCE DETECTED")

        m1, m2, m3 = st.columns(3)

        m1.metric(
            "Motion Score",
            round(result["motion_score"], 2)
        )

        m2.metric(
            "Confidence",
            f"{int(result['confidence'] * 100)}%"
        )

        m3.markdown(
            f"### {severity_badge(result['severity'])}"
        )

        # Evidence image
        if result.get("evidence_frame"):

            st.subheader("📸 Evidence Snapshot")

            st.image(
                result["evidence_frame"],
                width=300
            )

            with st.expander("View Full Image"):
                st.image(
                    result["evidence_frame"],
                    use_column_width=True
                )


# =================================================
# ALERTS PANEL
# =================================================

elif page == "🚨 Alerts":

    st.title("🚨 Alerts Panel")

    alerts = get_json("/alerts")

    if not alerts:
        st.info("No incidents recorded yet")
        st.stop()

    df = pd.DataFrame(alerts)

    st.download_button(
        "⬇️ Export Alerts CSV",
        df.to_csv(index=False),
        "alerts.csv",
        "text/csv"
    )

    selected = st.multiselect(
        "Severity Filter",
        ["HIGH", "MEDIUM", "LOW"],
        default=["HIGH", "MEDIUM", "LOW"]
    )

    df = df[df["severity"].isin(selected)]

    incident_index = st.selectbox(
        "Select Incident",
        df.index,
        format_func=lambda i:
        f"{df.loc[i, 'timestamp']} | {df.loc[i, 'severity']}"
    )

    incident = df.loc[incident_index]

    st.subheader("Incident Details")

    c1, c2 = st.columns(2)

    with c1:

        st.markdown(f"**Timestamp:** {incident['timestamp']}")
        st.markdown(f"**Source:** {incident['source']}")
        st.markdown(f"**Severity:** {incident['severity']}")
        st.markdown(f"**Confidence:** {int(incident['confidence']*100)}%")

    with c2:

        if incident.get("evidence_frame"):

            st.image(
                incident["evidence_frame"],
                use_column_width=True
            )

        else:

            st.info("No evidence image available")


# =================================================
# ANALYTICS
# =================================================

elif page == "📈 Analytics":

    st.title("📈 Analytics Dashboard")

    data = get_json("/analytics")

    if not data:

        st.error("Analytics unavailable")
        st.stop()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Violent Incidents",
        data["violence_distribution"]["violent"]
    )

    c2.metric(
        "Non Violent",
        data["violence_distribution"]["non_violent"]
    )

    c3.metric(
        "High Severity",
        data["severity_distribution"].get("HIGH", 0)
    )

    st.divider()

    st.subheader("Severity Distribution")

    st.bar_chart(
        pd.DataFrame.from_dict(
            data["severity_distribution"],
            orient="index"
        )
    )

    if data["incidents_over_time"]:

        st.subheader("Incidents Over Time")

        st.line_chart(
            pd.DataFrame.from_dict(
                data["incidents_over_time"],
                orient="index"
            )
        )


# =================================================
# SYSTEM STATUS
# =================================================

else:

    st.title("⚙️ System Status")

    if backend_alive():

        st.success("Backend running normally")

    else:

        st.error("Backend not reachable")
