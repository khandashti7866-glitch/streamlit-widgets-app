# app.py
# Android-optimized "Widgets" dashboard using Streamlit
# Run with: streamlit run app.py
# Notes: open the app in Chrome on an Android device and "Add to Home screen" for a native-like experience.

import streamlit as st
from datetime import datetime, timedelta
import time
import json
import uuid

st.set_page_config(page_title="Android Widgets", layout="wide", initial_sidebar_state="collapsed")

# --- Styles (mobile-first)
st.markdown(
    """
    <style>
    /* Page background and spacing */
    html, body, .block-container { padding: 8px 8px 24px 8px; }
    body { background: linear-gradient(180deg, #f7f9fc 0%, #ffffff 100%); }
    .widget-card {
        background: white;
        border-radius: 14px;
        padding: 14px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.06);
        margin-bottom: 12px;
    }
    .widget-title { font-size: 18px; font-weight: 700; margin-bottom: 6px; }
    .small-muted { color: #6b7280; font-size: 12px; }
    .big-number { font-size: 36px; font-weight: 700; }
    .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
    @media (max-width: 600px) {
        .grid { grid-template-columns: 1fr; }
        .widget-title { font-size: 16px; }
        .big-number { font-size: 32px; }
    }
    .pill-btn {
        display:inline-block;
        padding:8px 12px;
        border-radius:999px;
        border: none;
        font-weight:600;
        cursor:pointer;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Header
st.markdown("<div style='display:flex;justify-content:space-between;align-items:center;'>"
            "<div><h2 style='margin:0'>Android Widgets</h2>"
            "<div class='small-muted'>Optimized for Android (Open in Chrome → Add to Home screen)</div></div>"
            "<div style='text-align:right'><small class='small-muted'>Touch-friendly • Offline-ish UI</small></div>"
            "</div>", unsafe_allow_html=True)

# --- Initialize session state
if "notes" not in st.session_state:
    st.session_state.notes = []
if "counters" not in st.session_state:
    st.session_state.counters = {}
if "stopwatch" not in st.session_state:
    st.session_state.stopwatch = {"running": False, "start": None, "elapsed": 0.0}
if "shortcuts" not in st.session_state:
    # Example shortcuts (user can add their own)
    st.session_state.shortcuts = [
        {"id": str(uuid.uuid4()), "label": "Gmail", "url": "https://mail.google.com"},
        {"id": str(uuid.uuid4()), "label": "Maps", "url": "https://maps.google.com"}
    ]

# --- Utility functions
def now_clock():
    return datetime.now().strftime("%I:%M:%S %p")

def human_delta(seconds):
    td = timedelta(seconds=int(seconds))
    total = str(td)
    # format hh:mm:ss
    return total

# --- Layout: widget grid
with st.container():
    cols = st.columns([1, 1])

    # Left column widgets
    with cols[0]:
        st.markdown("<div class='widget-card'>", unsafe_allow_html=True)
        st.markdown("<div class='widget-title'>Clock</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='big-number' id='clock'>{now_clock()}</div>", unsafe_allow_html=True)
        st.markdown("<div class='small-muted'>Updates every second client-side.</div>", unsafe_allow_html=True)

        # Inject small JS to update clock every second client-side for responsiveness
        st.components.v1.html(
            """
            <script>
            function updateClock(){
              const el = document.getElementById('clock');
              if(!el) return;
              const d = new Date();
              let hrs = d.getHours();
              let ampm = hrs >= 12 ? 'PM' : 'AM';
              hrs = ((hrs + 11) % 12 + 1);
              const mins = String(d.getMinutes()).padStart(2,'0');
              const secs = String(d.getSeconds()).padStart(2,'0');
              el.innerText = hrs + ':' + mins + ':' + secs + ' ' + ampm;
            }
            setInterval(updateClock, 1000);
            updateClock();
            </script>
            """,
            height=0,
            scrolling=False,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='widget-card'>", unsafe_allow_html=True)
        st.markdown("<div class='widget-title'>Stopwatch</div>", unsafe_allow_html=True)
        sw = st.session_state.stopwatch
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            if st.button("Start" if not sw["running"] else "Resume"):
                if not sw["running"]:
                    sw["start"] = time.time() - sw["elapsed"]
                    sw["running"] = True
        with col2:
            if st.button("Stop"):
                if sw["running"]:
                    sw["elapsed"] = time.time() - sw["start"]
                    sw["running"] = False
        with col3:
            if st.button("Reset"):
                sw["running"] = False
                sw["start"] = None
                sw["elapsed"] = 0.0

        # Show stopwatch value (updated each rerun)
        elapsed = (time.time() - sw["start"]) if sw["running"] and sw["start"] else sw["elapsed"]
        st.markdown(f"<div style='margin-top:8px; font-size:28px; font-weight:700'>{human_delta(elapsed)}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='widget-card'>", unsafe_allow_html=True)
        st.markdown("<div class='widget-title'>Quick Notes</div>", unsafe_allow_html=True)
        note_text = st.text_area("Write note...", key="note_input", placeholder="Tap here and type a quick note")
        coln1, coln2 = st.columns([3,1])
        with coln2:
            if st.button("Save Note"):
                text = st.session_state.get("note_input","").strip()
                if text:
                    st.session_state.notes.insert(0, {"id": str(uuid.uuid4()), "text": text, "ts": datetime.now().isoformat()})
                    st.session_state.note_input = ""
        # show recent notes
        for n in st.session_state.notes[:6]:
            ts = datetime.fromisoformat(n["ts"]).strftime("%b %d %H:%M")
            st.markdown(f"<div style='padding:6px 0;border-bottom:1px dashed #eee'><b>{n['text']}</b><div class='small-muted'>{ts}</div></div>", unsafe_allow_html=True)
        if st.button("Clear Notes"):
            st.session_state.notes = []
        st.markdown("</div>", unsafe_allow_html=True)

    # Right column widgets
    with cols[1]:
        st.markdown("<div class='widget-card'>", unsafe_allow_html=True)
        st.markdown("<div class='widget-title'>Counter Widgets</div>", unsafe_allow_html=True)
        # dynamic counters
        counter_id = st.selectbox("Select / create counter", options=["<new>"] + list(st.session_state.counters.keys()), key="counter_select")
        if counter_id == "<new>":
            new_name = st.text_input("New counter name", key="new_counter_name")
            if st.button("Create counter"):
                if new_name.strip():
                    st.session_state.counters[new_name] = 0
                    st.session_state.counter_select = new_name
        else:
            val = st.session_state.counters.get(counter_id, 0)
            c1, c2, c3 = st.columns([1,1,1])
            with c1:
                if st.button("−", key=f"dec_{counter_id}"):
                    st.session_state.counters[counter_id] = max(0, val - 1)
            with c2:
                st.markdown(f"<div style='text-align:center; font-size:28px; font-weight:700'>{val}</div>", unsafe_allow_html=True)
            with c3:
                if st.button("+", key=f"inc_{counter_id}"):
                    st.session_state.counters[counter_id] = val + 1
            if st.button("Delete counter"):
                del st.session_state.counters[counter_id]
                st.session_state.counter_select = "<new>"
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='widget-card'>", unsafe_allow_html=True)
        st.markdown("<div class='widget-title'>Battery & Device Info</div>", unsafe_allow_html=True)
        # We will display battery % using browser JS (works in many Android browsers)
        st.markdown("<div id='battery_area' class='small-muted'>Fetching battery data from browser...</div>", unsafe_allow_html=True)
        st.components.v1.html(
            """
            <div id="battery"><script>
            async function showBattery(){
                try{
                    if(navigator.getBattery){
                        const b = await navigator.getBattery();
                        function update(){
                            const pct = Math.round(b.level*100);
                            const charging = b.charging ? "charging" : "not charging";
                            document.getElementById('battery_area').innerText = pct + "% — " + charging;
                        }
                        b.addEventListener('levelchange', update);
                        b.addEventListener('chargingchange', update);
                        update();
                    } else {
                        // fallback approximate using navigator.connection (not battery but something)
                        document.getElementById('battery_area').innerText = "Battery API not available in this browser. For best results use Chrome on Android.";
                    }
                } catch(e){
                    document.getElementById('battery_area').innerText = "Battery access blocked by browser.";
                }
            }
            showBattery();
            </script></div>
            """,
            height=80,
            scrolling=False,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='widget-card'>", unsafe_allow_html=True)
        st.markdown("<div class='widget-title'>Shortcuts (Tap to open)</div>", unsafe_allow_html=True)
        # Show shortcuts as big pills
        for s in st.session_state.shortcuts:
            st.markdown(f"<a href='{s['url']}' target='_blank' style='text-decoration:none'><div class='pill-btn' style='border:1px solid #e6e6e6;padding:10px;margin:6px 0;border-radius:12px'>{s['label']}</div></a>", unsafe_allow_html=True)
        with st.expander("Manage Shortcuts"):
            add_label = st.text_input("Label", key="sc_label")
            add_url = st.text_input("URL", key="sc_url", placeholder="https://")
            if st.button("Add Shortcut"):
                if add_label.strip() and add_url.strip():
                    st.session_state.shortcuts.append({"id": str(uuid.uuid4()), "label": add_label.strip(), "url": add_url.strip()})
            # list and delete
            for s in st.session_state.shortcuts:
                c1, c2 = st.columns([4,1])
                c1.markdown(f"{s['label']} — <small class='small-muted'>{s['url']}</small>", unsafe_allow_html=True)
                if c2.button("Delete", key=f"del_{s['id']}"):
                    st.session_state.shortcuts = [x for x in st.session_state.shortcuts if x["id"] != s["id"]]
        st.markdown("</div>", unsafe_allow_html=True)

# --- Footer: export/import layout & data
st.markdown("<div style='margin-top:14px' class='widget-card'>", unsafe_allow_html=True)
st.markdown("<div class='widget-title'>Export / Import</div>", unsafe_allow_html=True)
colx, coly, colz = st.columns([1,1,2])
with colx:
    if st.button("Export JSON"):
        payload = {
            "notes": st.session_state.notes,
            "counters": st.session_state.counters,
            "shortcuts": st.session_state.shortcuts,
            "stopwatch": st.session_state.stopwatch
        }
        st.download_button("Download JSON", data=json.dumps(payload, indent=2), file_name="widgets_export.json", mime="application/json")
with coly:
    uploaded = st.file_uploader("Import JSON", type=["json"])
    if uploaded is not None:
        try:
            data = json.load(uploaded)
            st.session_state.notes = data.get("notes", [])
            st.session_state.counters = data.get("counters", {})
            st.session_state.shortcuts = data.get("shortcuts", st.session_state.shortcuts)
            st.session_state.stopwatch = data.get("stopwatch", st.session_state.stopwatch)
            st.success("Imported successfully.")
        except Exception as e:
            st.error(f"Failed to import: {e}")
with colz:
    st.markdown("<div class='small-muted'>Tip: On Android open this page in Chrome → Menu → Add to Home screen to pin this app as a shortcut. Opening it from home will feel like a widget dashboard.</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- End
st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
