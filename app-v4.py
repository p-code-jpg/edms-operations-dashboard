import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date

# Set matplotlib style for headless Streamlit rendering
plt.style.use('ggplot')

# ---------------------------------------------------------
# PAGE CONFIGURATION & CORPORATE STYLING
# ---------------------------------------------------------
st.set_page_config(
    page_title="IUM EDMS Operations Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for IUM Corporate Identity (#001F3F Deep Navy, #800020 Ceremonial Burgundy)
CUSTOM_CSS = """
<style>
    /* Main Background & Font */
    .main {
        background-color: #F8F9FA;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Header Banner */
    .ium-header {
        background: linear-gradient(135deg, #001F3F 0%, #003366 70%, #800020 100%);
        color: #FFFFFF;
        padding: 24px 30px;
        border-radius: 12px;
        border-bottom: 5px solid #800020;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        margin-bottom: 25px;
    }
    
    .ium-header h1 {
        font-family: 'Georgia', serif;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        color: #FFFFFF;
        letter-spacing: 0.5px;
    }
    
    .ium-header p {
        font-size: 1.05rem;
        margin-top: 6px;
        color: #E0E6ED;
        font-weight: 300;
    }
    
    /* Cards & Containers */
    .stat-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 18px 20px;
        border-left: 5px solid #001F3F;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin-bottom: 15px;
    }
    
    .stat-card-burgundy {
        border-left-color: #800020;
    }
    
    .stat-card-gold {
        border-left-color: #D4AF37;
    }
    
    /* Cure Notice Box */
    .cure-notice-box {
        background-color: #FFF3CD;
        border: 1px solid #FFEBAA;
        border-left: 6px solid #800020;
        color: #856404;
        padding: 15px;
        border-radius: 8px;
        margin-top: 10px;
        margin-bottom: 15px;
    }
    
    /* Section Headers */
    .section-title {
        color: #001F3F;
        font-family: 'Georgia', serif;
        border-bottom: 2px solid #800020;
        padding-bottom: 8px;
        margin-top: 15px;
        margin-bottom: 20px;
        font-size: 1.5rem;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #001F3F;
        color: #FFFFFF;
    }
    
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    
    /* Badge Styles */
    .badge-high {
        background-color: #800020;
        color: white;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .badge-medium {
        background-color: #D4AF37;
        color: black;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .badge-low {
        background-color: #28A745;
        color: white;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: bold;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------
# DATABASE INITIALIZATION & ROBUST QUERY ENGINE
# ---------------------------------------------------------
DB_FILE = "edms_operations.db"

def get_db_connection():
    """Establish connection to SQLite database with Row factory."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query, params=()):
    """Execute write query (INSERT, UPDATE, DELETE) with error handling."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"⚠️ Database Error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def fetch_all(query, params=()):
    """Execute read query and return list of dictionaries."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        st.error(f"⚠️ Database Read Error: {e}")
        return []
    finally:
        if conn:
            conn.close()

def init_db():
    """Create required tables and seed initial records if empty."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Executives Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS executives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                portfolio TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                academic_avg_pct REAL NOT NULL,
                status TEXT DEFAULT 'Active'
            )
        """)
        
        # 2. Subcommittees Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subcommittees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                portfolio_id INTEGER,
                academic_avg_pct REAL NOT NULL,
                status TEXT DEFAULT 'Active'
            )
        """)
        
        # 3. Tasks Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                portfolio_id INTEGER,
                assignee_name TEXT NOT NULL,
                priority TEXT NOT NULL,
                due_date TEXT NOT NULL,
                status TEXT DEFAULT 'Pending',
                cure_notice_sent INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)
        
        # 4. Biweekly Pulses Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS biweekly_pulses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_id INTEGER NOT NULL,
                submission_date TEXT NOT NULL,
                kpis_met TEXT,
                roadblocks TEXT,
                financial_inflow REAL DEFAULT 0.0,
                financial_outflow REAL DEFAULT 0.0,
                status TEXT DEFAULT 'Approved'
            )
        """)
        
        # 5. Central Files Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS central_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_category TEXT NOT NULL,
                doc_title TEXT NOT NULL,
                drive_url TEXT NOT NULL,
                upload_date TEXT NOT NULL
            )
        """)
        
        conn.commit()
        
        # Seed Initial Data if Executives table is empty
        cursor.execute("SELECT COUNT(*) FROM executives")
        if cursor.fetchone()[0] == 0:
            # Seed Executives
            exec_data = [
                ("Patience Jodt", "Chairperson", "p.jodt@ium.edu.na", "+264 81 123 4567", 68.5, "Active"),
                ("Tjipura Tjipura", "Vice Chairperson", "t.tjipura@ium.edu.na", "+264 81 234 5678", 65.0, "Active"),
                ("Daniella Kufuna", "Treasurer", "d.kufuna@ium.edu.na", "+264 81 345 6789", 72.0, "Active"),
                ("Rosalia Gabriel", "Events and Programs Officer", "r.gabriel@ium.edu.na", "+264 81 456 7890", 64.0, "Active"),
                ("Ina Uugwanga", "Public Relations Officer", "i.uugwanga@ium.edu.na", "+264 81 567 8901", 66.5, "Active"),
                ("Shafondjodje Ankome", "External Affairs and Partnerships", "s.ankome@ium.edu.na", "+264 81 678 9012", 61.5, "Active"),
                ("Egon Nauta", "Academics, Research and Innovations Officer", "e.nauta@ium.edu.na", "+264 81 789 0123", 69.0, "Active"),
            ]
            cursor.executemany("""
                INSERT INTO executives (full_name, portfolio, email, phone, academic_avg_pct, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, exec_data)
            
            # Seed Subcommittees
            sub_data = [
                ("David Shikongo", 1, 63.0, "Active"),
                ("Maria Kautondokwa", 2, 66.5, "Active"),
                ("Paulus Haimbodi", 3, 57.5, "Active"),
                ("Elizabeth Nangolo", 4, 71.0, "Active"),
            ]
            cursor.executemany("""
                INSERT INTO subcommittees (full_name, portfolio_id, academic_avg_pct, status)
                VALUES (?, ?, ?, ?)
            """, sub_data)
            
            # Seed Tasks
            task_data = [
                ("Compile Q3 Energy Transition Whitepaper", 7, "Egon Nauta", "High", "2026-10-10", "Overdue", 0, "2026-09-15"),
                ("Audit EDMS Annual Sponsorship Accounts", 3, "Daniella Kufuna", "High", "2026-10-25", "In Progress", 0, "2026-10-01"),
                ("Finalize Venue for Green Hydrogen Summit", 4, "Rosalia Gabriel", "Medium", "2026-11-01", "Pending", 0, "2026-10-05"),
                ("Submit Quarterly Governance Report", 2, "Tjipura Tjipura", "Low", "2026-10-15", "Overdue", 0, "2026-09-20"),
                ("Draft Partnership Proposal with Ministry of Energy", 6, "Shafondjodje Ankome", "High", "2026-10-30", "Pending", 0, "2026-10-10"),
                ("Launch EDMS Social Media Recruitment Campaign", 5, "Ina Uugwanga", "Medium", "2026-10-28", "In Progress", 0, "2026-10-12"),
            ]
            cursor.executemany("""
                INSERT INTO tasks (title, portfolio_id, assignee_name, priority, due_date, status, cure_notice_sent, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, task_data)
            
            # Seed Biweekly Pulses
            pulse_data = [
                (1, "2026-10-01", "Organized executive meeting & drafted constitutional amendments", "Minor delay in venue allocation", 1500.0, 200.0, "Approved"),
                (2, "2026-10-15", "Completed logistics review for Green Hydrogen Summit", "Awaiting driver confirmation from transport pool", 0.0, 450.0, "Approved"),
                (3, "2026-10-01", "Reconciled Q3 sponsorship funds & petty cash", "Outstanding receipts from PR team", 5000.0, 3200.0, "Approved"),
            ]
            cursor.executemany("""
                INSERT INTO biweekly_pulses (portfolio_id, submission_date, kpis_met, roadblocks, financial_inflow, financial_outflow, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, pulse_data)
            
            # Seed Central Files
            file_data = [
                ("01_Governance", "EDMS Constitution & Code of Conduct 2026", "https://drive.google.com/file/d/edms_const_2026", "2026-01-15"),
                ("02_Executive", "Executive Directive No. 02 of 2026 - Performance & Cure Notices", "https://drive.google.com/file/d/edms_exec_dir_02", "2026-02-01"),
                ("03_Finance", "EDMS Q3 Financial Statement & Bank Reconciliation", "https://drive.google.com/file/d/edms_fin_q3", "2026-09-30"),
                ("04_Membership", "Subcommittee & General Assembly Membership Roster", "https://drive.google.com/file/d/edms_members_2026", "2026-03-10"),
                ("05_Events", "Green Hydrogen Namibia Symposium Concept Note", "https://drive.google.com/file/d/edms_events_gh2", "2026-08-20"),
                ("06_Research", "Namibian Energy Sector Decarbonization Policy Brief", "https://drive.google.com/file/d/edms_res_decarb", "2026-07-12"),
                ("07_External", "MoU Agreement - IUM EDMS and Ministry of Mines & Energy", "https://drive.google.com/file/d/edms_mou_mme", "2026-05-05"),
            ]
            cursor.executemany("""
                INSERT INTO central_files (doc_category, doc_title, drive_url, upload_date)
                VALUES (?, ?, ?, ?)
            """, file_data)
            
            conn.commit()

    except sqlite3.Error as e:
        st.error(f"⚠️ Initialization Error: {e}")
    finally:
        if conn:
            conn.close()

# Run DB initialization
init_db()

# ---------------------------------------------------------
# AUTHENTICATION & SECURITY GATE
# ---------------------------------------------------------
DEFAULT_PASSCODE = "EDMS2026!"  # <-- DEFAULT MASTER PASSCODE (Change anytime!)

if 'master_passcode' not in st.session_state:
    st.session_state['master_passcode'] = DEFAULT_PASSCODE

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.markdown("""
    <div style="max-width: 520px; margin: 40px auto; padding: 30px; background-color: #FFFFFF; border-radius: 12px; border-top: 6px solid #800020; box-shadow: 0 4px 20px rgba(0,0,0,0.15); text-align: center;">
        <h2 style="color: #001F3F; font-family: 'Georgia', serif; margin-bottom: 4px;">⚡ IUM EDMS OPERATIONS</h2>
        <p style="color: #800020; font-weight: bold; margin-top: 0; font-size: 0.95rem;">EXECUTIVE SECURITY PORTAL</p>
        <hr style="border: 0; height: 1px; background: #E0E0E0; margin: 18px 0;"/>
        <p style="color: #495057; font-size: 0.95rem; line-height: 1.5;">
            This dashboard contains confidential IUM EDMS operations, financial pulses, and academic merit ledgers.<br/>
            Please enter the official Executive Passcode to unlock access.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        with st.form("login_form"):
            input_pass = st.text_input("Enter Executive Passcode", type="password", placeholder="••••••••")
            submit_login = st.form_submit_button("🔓 Unlock Dashboard", use_container_width=True)
            
            if submit_login:
                if input_pass == st.session_state['master_passcode']:
                    st.session_state['authenticated'] = True
                    st.success("✅ Passcode verified. Unlocking portal...")
                    st.rerun()
                else:
                    st.error("⚠️ Invalid Passcode. Access Restricted.")
        
        st.caption("🔒 Protected under Executive Directive No. 02 of 2026 | IUM EDMS")
    st.stop()


# ---------------------------------------------------------
# SIDEBAR NAVIGATION & SYSTEM METRICS
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚡ IUM EDMS")
    st.markdown("**Energy Development & Management Society**")
    st.markdown("---")
    
    panel_choice = st.radio(
        "NAVIGATION PANELS",
        [
            "📋 Task Delegation Engine",
            "⚡ Bi-Weekly Pulse Tracker (BEPC)",
            "📁 Central File Vault",
            "🎓 Academic Merit Ledger",
            "📧 Council Directory & Roster"
        ]
    )
    
    st.markdown("---")
    st.markdown("### 📊 System Quick Snapshot")
    
    execs = fetch_all("SELECT * FROM executives")
    tasks = fetch_all("SELECT * FROM tasks")
    overdue_count = sum(1 for t in tasks if t['status'] == 'Overdue')
    
    st.metric("Total Executives", len(execs))
    st.metric("Active Tasks", len(tasks))
    st.metric("Overdue Tasks", overdue_count, delta_color="inverse")
    
    st.markdown("---")
    st.markdown("---")
    st.markdown("### 🔒 Security Controls")
    
    with st.expander("🔑 Change Executive Passcode"):
        current_p = st.text_input("Current Passcode", type="password", key="cur_pass_input")
        new_p = st.text_input("New Passcode", type="password", key="new_pass_input")
        if st.button("Update Passcode"):
            if current_p != st.session_state['master_passcode']:
                st.error("Current passcode incorrect.")
            elif not new_p.strip():
                st.error("New passcode cannot be blank.")
            else:
                st.session_state['master_passcode'] = new_p.strip()
                st.success("Master passcode updated for this session!")
                
    if st.button("🔒 Lock / Log Out", use_container_width=True):
        st.session_state['authenticated'] = False
        st.rerun()
        
    st.caption("IUM Corporate System v2.6 | Executive Directive No. 02 Compliant")

# ---------------------------------------------------------
# DASHBOARD HEADER
# ---------------------------------------------------------
st.markdown("""
<div class="ium-header">
    <h1>IUM ENERGY DEVELOPMENT AND MANAGEMENT SOCIETY</h1>
    <p>Executive Operations, Governance & Academic Performance Management System</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# PANEL A: EXECUTIVE TASK DELEGATION ENGINE
# ---------------------------------------------------------
if panel_choice == "📋 Task Delegation Engine":
    st.markdown('<div class="section-title">Panel A: Executive Task Delegation Engine</div>', unsafe_allow_html=True)
    
    # 1. New Task Logging Form
    with st.expander("➕ Log & Assign New Executive Task", expanded=False):
        executives_list = fetch_all("SELECT id, full_name, portfolio FROM executives WHERE status = 'Active'")
        exec_options = {f"{e['portfolio']} - {e['full_name']}": e for e in executives_list}
        
        with st.form("new_task_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                task_title = st.text_input("Task Title / Deliverable *")
                selected_exec_str = st.selectbox("Assignee & Portfolio *", list(exec_options.keys()) if exec_options else ["None"])
            with col2:
                priority = st.selectbox("Priority Level", ["High", "Medium", "Low"])
                due_date = st.date_input("Due Date", value=date.today())
            
            submit_task = st.form_submit_button("Delegate Task")
            
            if submit_task:
                if not task_title.strip():
                    st.error("Please provide a valid task title.")
                elif not exec_options:
                    st.error("No active executives available.")
                else:
                    exec_info = exec_options[selected_exec_str]
                    created_str = datetime.now().strftime("%Y-%m-%d")
                    due_str = due_date.strftime("%Y-%m-%d")
                    
                    success = execute_query("""
                        INSERT INTO tasks (title, portfolio_id, assignee_name, priority, due_date, status, cure_notice_sent, created_at)
                        VALUES (?, ?, ?, ?, ?, 'Pending', 0, ?)
                    """, (task_title, exec_info['id'], exec_info['full_name'], priority, due_str, created_str))
                    
                    if success:
                        st.success(f"Task '{task_title}' successfully delegated to {exec_info['full_name']}!")
                        st.rerun()

    # 2. Task Summary & Analytics Visuals
    all_tasks = fetch_all("""
        SELECT t.*, e.portfolio 
        FROM tasks t
        LEFT JOIN executives e ON t.portfolio_id = e.id
        ORDER BY t.due_date ASC
    """)
    
    col_f1, col_f2, col_f3 = st.columns([2, 1, 1])
    with col_f1:
        status_filter = st.multiselect(
            "Filter by Status", 
            ["Pending", "In Progress", "Completed", "Overdue"],
            default=["Pending", "In Progress", "Overdue"]
        )
    with col_f2:
        priority_filter = st.selectbox("Filter by Priority", ["All Priorities", "High", "Medium", "Low"])
    with col_f3:
        if all_tasks:
            df_tasks_export = pd.DataFrame(all_tasks)
            csv_tasks = df_tasks_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Export Tasks (CSV)",
                data=csv_tasks,
                file_name=f"edms_tasks_{date.today().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
    filtered_tasks = [
        t for t in all_tasks 
        if t['status'] in status_filter and 
        (priority_filter == "All Priorities" or t['priority'] == priority_filter)
    ]
    
    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Tasks", len(all_tasks))
    m2.metric("Pending / In Progress", sum(1 for t in all_tasks if t['status'] in ['Pending', 'In Progress']))
    m3.metric("Completed", sum(1 for t in all_tasks if t['status'] == 'Completed'))
    m4.metric("Overdue", sum(1 for t in all_tasks if t['status'] == 'Overdue'), delta_color="inverse")
    
    # Interactive Task Analytics Chart
    if all_tasks:
        with st.expander("📊 Visual Task Analytics & Breakdown", expanded=False):
            df_t = pd.DataFrame(all_tasks)
            c_chart1, c_chart2 = st.columns(2)
            with c_chart1:
                st.markdown("**Tasks by Status**")
                status_counts = df_t['status'].value_counts()
                st.bar_chart(status_counts)
            with c_chart2:
                st.markdown("**Tasks by Priority**")
                priority_counts = df_t['priority'].value_counts()
                st.bar_chart(priority_counts)

    st.markdown("### 📋 Executive Task Control & Cure Notice Delegation")
    
    if not filtered_tasks:
        st.info("No tasks match the selected criteria.")
    else:
        for task in filtered_tasks:
            with st.container():
                st.markdown(f"""
                <div class="stat-card {'stat-card-burgundy' if task['status'] == 'Overdue' else 'stat-card'}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 1.1rem; font-weight: bold; color: #001F3F;">{task['title']}</span>
                        <span>
                            <span class="badge-{'high' if task['priority']=='High' else ('medium' if task['priority']=='Medium' else 'low')}">{task['priority']} Priority</span>
                            &nbsp;<b>Status:</b> {task['status']}
                        </span>
                    </div>
                    <div style="margin-top: 8px; color: #495057; font-size: 0.95rem;">
                        👤 <b>Assignee:</b> {task['assignee_name']} ({task['portfolio'] or 'Unassigned'}) &nbsp;|&nbsp; 
                        📅 <b>Due Date:</b> {task['due_date']} &nbsp;|&nbsp; 
                        🕒 <b>Created:</b> {task['created_at']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns([1.5, 1.5, 2])
                with c1:
                    new_status = st.selectbox(
                        "Update Status",
                        ["Pending", "In Progress", "Completed", "Overdue"],
                        index=["Pending", "In Progress", "Completed", "Overdue"].index(task['status']),
                        key=f"status_select_{task['id']}"
                    )
                    if new_status != task['status']:
                        execute_query("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task['id']))
                        st.toast(f"Updated status for task #{task['id']} to {new_status}")
                        st.rerun()
                        
                with c2:
                    if task['status'] == 'Overdue' or task['cure_notice_sent'] == 1:
                        if task['cure_notice_sent'] == 1:
                            st.warning("⚠️ 48-Hr Cure Notice Active")
                        else:
                            if st.button("🚩 Issue 48-Hour Cure Notice", key=f"cure_btn_{task['id']}"):
                                execute_query("UPDATE tasks SET cure_notice_sent = 1, status = 'Overdue' WHERE id = ?", (task['id'],))
                                st.rerun()
                                
                with c3:
                    if task['cure_notice_sent'] == 1:
                        st.markdown("""
                        <div class="cure-notice-box">
                            <b>EXECUTIVE DIRECTIVE NO. 02 OF 2026:</b><br/>
                            Official 48-Hour Cure Notice served to assignee. Rectification window active before Escalation to Council.
                        </div>
                        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# PANEL B: BI-WEEKLY EXECUTIVE PULSE CHECK (BEPC) TRACKER
# ---------------------------------------------------------
elif panel_choice == "⚡ Bi-Weekly Pulse Tracker (BEPC)":
    st.markdown('<div class="section-title">Panel B: Bi-Weekly Executive Pulse Check (BEPC) Tracker</div>', unsafe_allow_html=True)
    
    tab_pulse_submit, tab_pulse_matrix = st.tabs(["📝 Submit Fortnightly Pulse", "📊 Pulse Compliance & Financial Ledger"])
    
    with tab_pulse_submit:
        st.markdown("### Fortnightly Executive Report Submission")
        executives_list = fetch_all("SELECT id, full_name, portfolio FROM executives WHERE status = 'Active'")
        exec_options = {f"{e['portfolio']} ({e['full_name']})": e['id'] for e in executives_list}
        
        with st.form("bepc_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                selected_port = st.selectbox("Reporting Portfolio *", list(exec_options.keys()) if exec_options else ["None"])
                sub_date = st.date_input("Pulse Date", value=date.today())
            with col2:
                inflow = st.number_input("Financial Inflow (ZAR / N$)", min_value=0.0, step=100.0)
                outflow = st.number_input("Financial Outflow (ZAR / N$)", min_value=0.0, step=100.0)
                
            kpis = st.text_area("KPIs & Milestones Achieved *", placeholder="Detail operational deliverables completed this fortnight...")
            roadblocks = st.text_area("Roadblocks & Governance Escalations", placeholder="Detail operational bottlenecks or funding delays...")
            
            submit_pulse = st.form_submit_button("Submit BEPC Pulse Report")
            
            if submit_pulse:
                if not kpis.strip():
                    st.error("Please detail KPIs met during this reporting period.")
                elif not exec_options:
                    st.error("No active portfolios available.")
                else:
                    port_id = exec_options[selected_port]
                    date_str = sub_date.strftime("%Y-%m-%d")
                    
                    success = execute_query("""
                        INSERT INTO biweekly_pulses (portfolio_id, submission_date, kpis_met, roadblocks, financial_inflow, financial_outflow, status)
                        VALUES (?, ?, ?, ?, ?, ?, 'Approved')
                    """, (port_id, date_str, kpis, roadblocks, inflow, outflow))
                    
                    if success:
                        st.success("BEPC Pulse Report successfully recorded into the Executive Ledger!")
                        st.rerun()

    with tab_pulse_matrix:
        st.markdown("### Executive Pulse Financial & Compliance Overview")
        
        pulses = fetch_all("""
            SELECT p.*, e.full_name, e.portfolio
            FROM biweekly_pulses p
            JOIN executives e ON p.portfolio_id = e.id
            ORDER BY p.submission_date DESC
        """)
        
        if pulses:
            total_in = sum(p['financial_inflow'] for p in pulses)
            total_out = sum(p['financial_outflow'] for p in pulses)
            net_bal = total_in - total_out
            
            fc1, fc2, fc3, fc4 = st.columns([1, 1, 1, 1])
            fc1.metric("Total Inflow (N$)", f"N$ {total_in:,.2f}")
            fc2.metric("Total Outflow (N$)", f"N$ {total_out:,.2f}")
            fc3.metric("Net Operational Reserve", f"N$ {net_bal:,.2f}", delta=f"N$ {net_bal:,.2f}")
            
            with fc4:
                df_pulses_export = pd.DataFrame(pulses)
                csv_pulses = df_pulses_export.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Export Pulses (CSV)",
                    data=csv_pulses,
                    file_name=f"edms_pulses_{date.today().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            
            # Financial Trend Chart
            with st.expander("📈 Financial Inflow vs. Outflow Analytics", expanded=True):
                df_p = pd.DataFrame(pulses)
                df_chart = df_p[['submission_date', 'financial_inflow', 'financial_outflow']].groupby('submission_date').sum()
                st.line_chart(df_chart)
            
            st.markdown("#### Historical BEPC Submission Ledger")
            df_display = df_pulses_export[['id', 'portfolio', 'full_name', 'submission_date', 'kpis_met', 'roadblocks', 'financial_inflow', 'financial_outflow', 'status']]
            df_display.columns = ['Pulse ID', 'Portfolio', 'Executive Lead', 'Date', 'KPIs Met', 'Roadblocks', 'Inflow (N$)', 'Outflow (N$)', 'Status']
            
            st.dataframe(df_display, use_container_width=True)
        else:
            st.info("No bi-weekly pulse reports submitted yet.")

# ---------------------------------------------------------
# PANEL C: SOCIETY CENTRAL FILE VAULT
# ---------------------------------------------------------
elif panel_choice == "📁 Central File Vault":
    st.markdown('<div class="section-title">Panel C: Society Central File Vault</div>', unsafe_allow_html=True)
    
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        search_query = st.text_input("🔍 Search Governance & Operational Documents", placeholder="Type document title or keyword...")
    with col_s2:
        all_files = fetch_all("SELECT * FROM central_files ORDER BY doc_category ASC, upload_date DESC")
        if all_files:
            df_files_export = pd.DataFrame(all_files)
            csv_files = df_files_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Export Directory (CSV)",
                data=csv_files,
                file_name=f"edms_vault_directory_{date.today().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with st.expander("📤 Upload / Register New Central Document", expanded=False):
        categories = [
            "01_Governance",
            "02_Executive",
            "03_Finance",
            "04_Membership",
            "05_Events",
            "06_Research",
            "07_External"
        ]
        with st.form("new_file_form", clear_on_submit=True):
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                doc_title = st.text_input("Document Title *")
                doc_cat = st.selectbox("Official Category Folder *", categories)
            with col_u2:
                drive_url = st.text_input("Cloud / Google Drive Storage Link *", placeholder="https://drive.google.com/...")
                up_date = st.date_input("Document Date", value=date.today())
                
            submit_file = st.form_submit_button("Register Document in Vault")
            if submit_file:
                if not doc_title.strip() or not drive_url.strip():
                    st.error("Document Title and Storage Link are required.")
                else:
                    success = execute_query("""
                        INSERT INTO central_files (doc_category, doc_title, drive_url, upload_date)
                        VALUES (?, ?, ?, ?)
                    """, (doc_cat, doc_title, drive_url, up_date.strftime("%Y-%m-%d")))
                    if success:
                        st.success(f"Document '{doc_title}' registered under {doc_cat}!")
                        st.rerun()

    st.markdown("---")
    
    if search_query.strip():
        all_files = [f for f in all_files if search_query.lower() in f['doc_title'].lower() or search_query.lower() in f['doc_category'].lower()]

    categories_map = {
        "01_Governance": "🏛️ 01_Governance (Constitutions, Bylaws, Charters)",
        "02_Executive": "📋 02_Executive (Directives, Minutes, Decrees)",
        "03_Finance": "💰 03_Finance (Audits, Reconciliations, Budgets)",
        "04_Membership": "👥 04_Membership (Rosters, Attendance, Merit)",
        "05_Events": "🎉 05_Events (Symposiums, Workshops, Concept Notes)",
        "06_Research": "🔬 06_Research (Policy Papers, Whitepapers, Tech Reports)",
        "07_External": "🤝 07_External (MoUs, Partnerships, Ministerial Letters)"
    }
    
    for cat_code, cat_label in categories_map.items():
        cat_files = [f for f in all_files if f['doc_category'] == cat_code]
        with st.expander(f"{cat_label} ({len(cat_files)} files)", expanded=(len(cat_files) > 0 and search_query != "")):
            if not cat_files:
                st.caption("No registered documents in this folder.")
            else:
                for file_item in cat_files:
                    f_col1, f_col2 = st.columns([4, 1])
                    with f_col1:
                        st.markdown(f"**📄 {file_item['doc_title']}**")
                        st.caption(f"Registered on: {file_item['upload_date']} | Storage: Cloud Secured")
                    with f_col2:
                        st.link_button("🌐 Open Link", file_item['drive_url'])

# ---------------------------------------------------------
# PANEL D: ACADEMIC MERIT LEDGER
# ---------------------------------------------------------
elif panel_choice == "🎓 Academic Merit Ledger":
    st.markdown('<div class="section-title">Panel D: Academic Merit Ledger</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="cure-notice-box" style="border-left-color: #001F3F;">
        <b>MANDATORY EDMS CONSTITUTIONAL RULE:</b><br/>
        All Executive Officers and Subcommittee Members must maintain a minimum <b>60.0% academic average</b>.
        Members falling below 60.0% are automatically placed on Academic Probation and flagged for leadership review.
    </div>
    """, unsafe_allow_html=True)
    
    execs = fetch_all("SELECT * FROM executives")
    subs = fetch_all("SELECT * FROM subcommittees")
    
    all_members = [
        {"name": e['full_name'], "role": f"Executive ({e['portfolio']})", "avg": e['academic_avg_pct'], "type": "Executive"} 
        for e in execs
    ] + [
        {"name": s['full_name'], "role": f"Subcommittee Member #{s['portfolio_id']}", "avg": s['academic_avg_pct'], "type": "Subcommittee"} 
        for s in subs
    ]
    
    total_mem = len(all_members)
    compliant = sum(1 for m in all_members if m['avg'] >= 60.0)
    probation = total_mem - compliant
    
    mc1, mc2, mc3, mc4 = st.columns([1, 1, 1, 1])
    mc1.metric("Total Society Leadership", total_mem)
    mc2.metric("Compliant (>= 60.0%)", compliant)
    mc3.metric("Academic Probation (< 60.0%)", probation, delta_color="inverse")
    
    with mc4:
        df_merit_all = pd.DataFrame(all_members)
        if not df_merit_all.empty:
            csv_merit = df_merit_all.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Export Merit Ledger (CSV)",
                data=csv_merit,
                file_name=f"edms_merit_ledger_{date.today().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            
    # Visual Chart for Academic Average Distribution
    if all_members:
        with st.expander("📊 Academic Merit Grade Distribution", expanded=False):
            df_m = pd.DataFrame(all_members)
            st.bar_chart(df_m.set_index('name')['avg'])
    
    st.markdown("### 📜 Leadership Academic Performance Roster")
    
    tab_exec_ledger, tab_sub_ledger, tab_add_member = st.tabs(["🏛️ Executive Council Ledger", "👥 Subcommittee Roster", "➕ Register Member"])
    
    with tab_exec_ledger:
        if execs:
            df_exec = pd.DataFrame(execs)
            df_exec['Academic Status'] = df_exec['academic_avg_pct'].apply(
                lambda x: "🟢 COMPLIANT" if x >= 60.0 else "🔴 ACADEMIC PROBATION"
            )
            df_exec_show = df_exec[['id', 'full_name', 'portfolio', 'email', 'academic_avg_pct', 'Academic Status']]
            df_exec_show.columns = ['ID', 'Full Name', 'Portfolio', 'Email Address', 'Academic Avg (%)', 'Compliance Status']
            
            st.dataframe(
                df_exec_show.style.applymap(
                    lambda v: 'background-color: #FFCDD2; color: #B71C1C; font-weight: bold;' if 'PROBATION' in str(v) 
                    else ('background-color: #C8E6C9; color: #1B5E20; font-weight: bold;' if 'COMPLIANT' in str(v) else ''),
                    subset=['Compliance Status']
                ),
                use_container_width=True
            )
            
    with tab_sub_ledger:
        if subs:
            df_sub = pd.DataFrame(subs)
            df_sub['Academic Status'] = df_sub['academic_avg_pct'].apply(
                lambda x: "🟢 COMPLIANT" if x >= 60.0 else "🔴 ACADEMIC PROBATION"
            )
            df_sub_show = df_sub[['id', 'full_name', 'portfolio_id', 'academic_avg_pct', 'Academic Status']]
            df_sub_show.columns = ['ID', 'Full Name', 'Portfolio ID', 'Academic Avg (%)', 'Compliance Status']
            
            st.dataframe(
                df_sub_show.style.applymap(
                    lambda v: 'background-color: #FFCDD2; color: #B71C1C; font-weight: bold;' if 'PROBATION' in str(v) 
                    else ('background-color: #C8E6C9; color: #1B5E20; font-weight: bold;' if 'COMPLIANT' in str(v) else ''),
                    subset=['Compliance Status']
                ),
                use_container_width=True
            )
            
    with tab_add_member:
        st.markdown("#### Add New Executive or Subcommittee Member")
        with st.form("add_member_form", clear_on_submit=True):
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                mem_type = st.selectbox("Leadership Tier", ["Executive", "Subcommittee"])
                full_name = st.text_input("Full Name *")
                email = st.text_input("IUM Email Address")
            with col_m2:
                portfolio_title = st.text_input("Portfolio Title / ID *", placeholder="e.g. Lead: Strategic Partnerships")
                acad_avg = st.number_input("Academic Average (%) *", min_value=0.0, max_value=100.0, value=65.0, step=0.5)
                phone = st.text_input("Phone Number")
                
            submit_mem = st.form_submit_button("Register Leadership Member")
            if submit_mem:
                if not full_name.strip() or not portfolio_title.strip():
                    st.error("Name and Portfolio Title are required.")
                else:
                    if mem_type == "Executive":
                        success = execute_query("""
                            INSERT INTO executives (full_name, portfolio, email, phone, academic_avg_pct, status)
                            VALUES (?, ?, ?, ?, ?, 'Active')
                        """, (full_name, portfolio_title, email, phone, acad_avg))
                    else:
                        try:
                            port_id_int = int(''.join(filter(str.isdigit, portfolio_title))) if any(c.isdigit() for c in portfolio_title) else 1
                        except:
                            port_id_int = 1
                        success = execute_query("""
                            INSERT INTO subcommittees (full_name, portfolio_id, academic_avg_pct, status)
                            VALUES (?, ?, ?, 'Active')
                        """, (full_name, port_id_int, acad_avg))
                        
                    if success:
                        st.success(f"Member '{full_name}' successfully added to the Merit Ledger!")
                        st.rerun()

# ---------------------------------------------------------
# PANEL E: COUNCIL DIRECTORY & EMAIL ROSTER
# ---------------------------------------------------------
elif panel_choice == "📧 Council Directory & Roster":
    st.markdown('<div class="section-title">Panel E: Council Directory & Leadership Email Roster</div>', unsafe_allow_html=True)
    
    st.markdown("""
    Use this centralized directory to view, edit, and export official email addresses and contact information for EDMS Executive Council members and Subcommittee Leads.
    """)
    
    execs = fetch_all("SELECT * FROM executives")
    
    if execs:
        df_dir = pd.DataFrame(execs)
        
        # Email Quick Broadcast String
        email_list = [e['email'] for e in execs if e['email']]
        broadcast_str = "; ".join(email_list)
        
        st.markdown("### 📢 Council Broadcast Email String")
        st.text_area("Copy/Paste into Outlook/Gmail To/BCC field:", broadcast_str, height=70)
        
        st.markdown("### 📝 Executive Contact Directory (Editable)")
        
        for e in execs:
            with st.expander(f"👤 {e['portfolio']} - {e['full_name']}", expanded=False):
                with st.form(key=f"edit_exec_form_{e['id']}"):
                    ce1, ce2 = st.columns(2)
                    with ce1:
                        new_name = st.text_input("Full Name", value=e['full_name'])
                        new_email = st.text_input("IUM Email Address", value=e['email'] or "")
                    with ce2:
                        new_phone = st.text_input("Phone Number", value=e['phone'] or "")
                        new_avg = st.number_input("Academic Avg (%)", value=float(e['academic_avg_pct']), min_value=0.0, max_value=100.0, step=0.5)
                    
                    update_btn = st.form_submit_button("Save Updates")
                    if update_btn:
                        success = execute_query("""
                            UPDATE executives 
                            SET full_name = ?, email = ?, phone = ?, academic_avg_pct = ?
                            WHERE id = ?
                        """, (new_name, new_email, new_phone, new_avg, e['id']))
                        if success:
                            st.success(f"Updated contact details for {new_name}!")
                            st.rerun()

        # CSV Download Button for Roster
        csv_roster = df_dir.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Complete Leadership Roster (CSV)",
            data=csv_roster,
            file_name=f"edms_council_roster_{date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6C757D; font-size: 0.85rem; padding: 10px;">
    IUM Energy Development and Management Society (EDMS) &copy; 2026<br/>
    Official Operations Dashboard | Built with Streamlit & SQLite
</div>
""", unsafe_allow_html=True)
