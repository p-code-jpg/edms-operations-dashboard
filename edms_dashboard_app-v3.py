import sqlite3
import pandas as pd
import datetime
import streamlit as st

# Streamlit Page Setup
st.set_page_config(
    page_title="IUM EDMS Team Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_NAME = "edms_operations.db"

# Custom Styling - Clean & Modern IUM Theme
st.markdown("""
    <style>
    /* Main Background & Clean Typography */
    .stApp {
        background-color: #FAFAFA;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Header Styling */
    .main-header {
        background: linear-gradient(135deg, #001F3F 0%, #1A365D 100%);
        color: white;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .main-header h1 {
        color: #FFFFFF !important;
        margin: 0;
        font-size: 28px;
        font-weight: 700;
    }
    .main-header p {
        color: #E2E8F0;
        margin: 6px 0 0 0;
        font-size: 15px;
    }

    /* Metric Card Styling */
    .metric-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 18px;
        border-top: 4px solid #800020;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        text-align: center;
    }
    .metric-value {
        font-size: 32px;
        font-weight: 800;
        color: #001F3F;
    }
    .metric-label {
        font-size: 13px;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 4px;
    }

    /* Directive Card Styling */
    .directive-card {
        background-color: #FFFFFF;
        border-left: 5px solid #001F3F;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    .directive-title {
        color: #800020;
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .directive-meta {
        font-size: 12px;
        color: #64748B;
        margin-bottom: 8px;
    }

    /* Button Customization */
    .stButton>button {
        background-color: #001F3F;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        padding: 8px 16px;
    }
    .stButton>button:hover {
        background-color: #800020;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS executives (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        portfolio TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        academic_avg_pct REAL DEFAULT 65.0,
        status TEXT DEFAULT 'Active'
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subcommittees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        portfolio TEXT NOT NULL,
        specific_role TEXT NOT NULL,
        email TEXT,
        academic_avg_pct REAL DEFAULT 65.0,
        status TEXT DEFAULT 'Active'
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        portfolio TEXT NOT NULL,
        assignee_name TEXT NOT NULL,
        priority TEXT DEFAULT 'Medium',
        due_date TEXT NOT NULL,
        status TEXT DEFAULT 'Pending',
        cure_notice_sent INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS biweekly_pulses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        portfolio TEXT NOT NULL,
        submitter_name TEXT NOT NULL,
        submission_date TEXT NOT NULL,
        kpis_met TEXT,
        roadblocks TEXT,
        financial_inflow REAL DEFAULT 0.0,
        financial_outflow REAL DEFAULT 0.0,
        status TEXT DEFAULT 'Submitted'
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS central_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doc_category TEXT NOT NULL,
        doc_title TEXT NOT NULL,
        drive_url TEXT NOT NULL,
        uploaded_by TEXT NOT NULL,
        upload_date TEXT NOT NULL
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS executive_directives (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        directive_no TEXT NOT NULL,
        title TEXT NOT NULL,
        issuer TEXT NOT NULL,
        effective_date TEXT NOT NULL,
        mandate_text TEXT NOT NULL,
        status TEXT DEFAULT 'Active'
    )''')
    
    # Seed Executives
    cursor.execute("SELECT COUNT(*) FROM executives")
    if cursor.fetchone()[0] == 0:
        execs = [
            ("Patience Jodt", "Chairperson & Executive Directorate", "chairperson@ium.edu.na", "+264 81 000 0001", 72.0, "Active"),
            ("Egon Nauta", "Research, Innovation & Academics", "research@ium.edu.na", "+264 81 000 0002", 78.5, "Active"),
            ("Shafondjodi Ankome", "External Affairs, Partnerships & Liaison", "external@ium.edu.na", "+264 81 000 0003", 70.0, "Active"),
            ("Daniella Casmillo", "Treasurer & Finance", "treasurer@ium.edu.na", "+264 81 000 0004", 75.0, "Active"),
            ("Rosalia Gabriel", "Programs & Events Secretary", "events@ium.edu.na", "+264 81 000 0005", 68.0, "Active"),
            ("Ina Uugwanga", "Spokesperson & PR Secretary", "pr@ium.edu.na", "+264 81 000 0006", 71.0, "Active"),
        ]
        cursor.executemany("INSERT INTO executives (full_name, portfolio, email, phone, academic_avg_pct, status) VALUES (?, ?, ?, ?, ?, ?)", execs)
        
    # Seed Subcommittees
    cursor.execute("SELECT COUNT(*) FROM subcommittees")
    if cursor.fetchone()[0] == 0:
        subs = [
            ("Chanray Kisting", "Research, Innovation & Academics", "Research Subcommittee Officer", "chanray@ium.edu.na", 68.5, "Active"),
            ("Joseph Sasamba", "Research, Innovation & Academics", "Research Subcommittee Officer", "joseph@ium.edu.na", 71.0, "Active"),
            ("Stephanus", "Research, Innovation & Academics", "Research Subcommittee Officer", "stephanus@ium.edu.na", 66.0, "Active"),
            ("Wilhelmina Abraham", "External Affairs & Partnerships", "External Affairs Secretary", "wilhelmina@ium.edu.na", 74.0, "Active"),
            ("Wissle Maliti", "External Affairs & Partnerships", "Outreach & Mobilization Head", "wissle@ium.edu.na", 72.5, "Active"),
            ("Setson Martin", "External Affairs & Partnerships", "External Liaison Officer", "setson@ium.edu.na", 67.0, "Active"),
            ("Wilhelmina Abraham", "Secretariat & Editorial Directorate", "Head Editorial Writer", "editorial@ium.edu.na", 74.0, "Active"),
        ]
        cursor.executemany("INSERT INTO subcommittees (full_name, portfolio, specific_role, email, academic_avg_pct, status) VALUES (?, ?, ?, ?, ?, ?)", subs)
        
    # Seed Initial Files
    cursor.execute("SELECT COUNT(*) FROM central_files")
    if cursor.fetchone()[0] == 0:
        files = [
            ("Governance & Legal", "EDMS Constitution Amended 2026", "https://drive.google.com/file/d/edms_constitution", "Maria Iipinge", "2026-04-15"),
            ("Governance & Legal", "Executive Directive No. 02 of 2026", "https://drive.google.com/file/d/edms_directive2", "Patience Jodt", "2026-05-10"),
            ("Membership Roster", "Master Subcommittee & Compliance Roster", "https://drive.google.com/file/d/membership_roster", "Chairperson Office", "2026-10-17"),
            ("External Affairs", "2027 Corporate Partnership Prospectus", "https://drive.google.com/file/d/prospectus_draft", "Shafondjodi Ankome", "2026-10-17"),
            ("Brand & Media", "EDMS Official Branch Logo (Option 2 Canva PNG)", "https://drive.google.com/file/d/edms_logo_png", "Rosalia Gabriel", "2026-10-20")
        ]
        cursor.executemany("INSERT INTO central_files (doc_category, doc_title, drive_url, uploaded_by, upload_date) VALUES (?, ?, ?, ?, ?)", files)

    # Seed Directives
    cursor.execute("SELECT COUNT(*) FROM executive_directives")
    if cursor.fetchone()[0] == 0:
        directives = [
            ("Directive No. 01 of 2026", "Establishment of Executive Portfolios & Academic Merit Gate", "Patience Jodt (Chairperson)", "2026-02-10", "Enforces the mandatory 60% academic average requirement for all office bearers across all directorates.", "Active"),
            ("Directive No. 02 of 2026", "Bi-Weekly Executive Pulse Check (BEPC) System", "Patience Jodt (Chairperson)", "2026-05-10", "Mandates fortnightly operational pulse reporting and automatic 48-Hour Cure Notices for unexcused missed deadlines.", "Active"),
            ("Directive No. 03 of 2026", "Standardization of Official EDMS Branch Logo", "Executive Directorate", "2026-10-20", "Requires all official documents, event flyers, and correspondence to use the approved EDMS Bulb + IUM Globe Canva Option 2 lockup.", "Active")
        ]
        cursor.executemany("INSERT INTO executive_directives (directive_no, title, issuer, effective_date, mandate_text, status) VALUES (?, ?, ?, ?, ?, ?)", directives)

    conn.commit()
    conn.close()

# Initialize DB
init_db()

# Top Navigation Bar / Banner
st.markdown("""
    <div class="main-header">
        <h1>⚡ IUM EDMS Team Operations Portal</h1>
        <p>Energy Development & Management Society — International University of Management</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("Navigation")
menu = st.sidebar.radio(
    "Choose a section:",
    [
        "🏠 Overview Dashboard",
        "📋 Task Manager",
        "👥 Team Roster & Profile Manager",
        "📜 Executive Directives & Policies",
        "📝 Submit Fortnightly Report",
        "📁 Document Vault"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Need help?** You can update emails, change member names/titles, or issue new directives at any time using the respective tabs.")

conn = get_connection()

# ---------------------------------------------------------
# TAB 1: OVERVIEW DASHBOARD
# ---------------------------------------------------------
if menu == "🏠 Overview Dashboard":
    st.title("🏠 Operational Summary")
    st.write("Welcome to the EDMS Operations Portal! Here is a quick snapshot of our active tasks, team members, and policy directives.")
    
    # Fetch key metrics
    total_execs = pd.read_sql_query("SELECT COUNT(*) AS c FROM executives", conn)['c'][0]
    total_subs = pd.read_sql_query("SELECT COUNT(*) AS c FROM subcommittees", conn)['c'][0]
    total_members = total_execs + total_subs
    
    pending_tasks = pd.read_sql_query("SELECT COUNT(*) AS c FROM tasks WHERE status != 'Completed'", conn)['c'][0]
    completed_tasks = pd.read_sql_query("SELECT COUNT(*) AS c FROM tasks WHERE status = 'Completed'", conn)['c'][0]
    total_directives = pd.read_sql_query("SELECT COUNT(*) AS c FROM executive_directives WHERE status='Active'", conn)['c'][0]
    
    # 4 Metric Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_members}</div>
                <div class="metric-label">Active Team Members</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-card" style="border-top-color: #001F3F;">
                <div class="metric-value">{pending_tasks}</div>
                <div class="metric-label">Open / In-Progress Tasks</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="metric-card" style="border-top-color: #2E7D32;">
                <div class="metric-value">{completed_tasks}</div>
                <div class="metric-label">Completed Tasks</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
            <div class="metric-card" style="border-top-color: #D84315;">
                <div class="metric-value">{total_directives}</div>
                <div class="metric-label">Active Directives</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # High Priority & Recent Tasks Preview
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        st.subheader("📌 Urgent & Recent Action Items")
        df_recent = pd.read_sql_query(
            "SELECT title AS 'Task', assignee_name AS 'Assigned To', due_date AS 'Due Date', priority AS 'Priority', status AS 'Status' FROM tasks ORDER BY id DESC LIMIT 5",
            conn
        )
        if not df_recent.empty:
            st.dataframe(df_recent, use_container_width=True, hide_index=True)
        else:
            st.success("🎉 All caught up! No active pending tasks right now.")
            
    with col_right:
        st.subheader("⚡ Quick Announcements & Policies")
        st.success("✅ **Logo Complete**: Official Branch Logo (Option 2) exported and ready for Marketing submission.")
        st.info("📅 **Upcoming**: Pre-year-end Corporate Sponsorship Prospectus outreach to energy partners.")
        st.warning("📜 **Active Policy**: Executive Directive No. 02 requires fortnightly BEPC reports due every alternate Friday by 17:00.")

# ---------------------------------------------------------
# TAB 2: TASK MANAGER
# ---------------------------------------------------------
elif menu == "📋 Task Manager":
    st.title("📋 Society Task Manager")
    st.write("Assign tasks, track progress, and update status easily.")
    
    tab_view, tab_add, tab_update = st.tabs(["🔍 View All Tasks", "➕ Assign New Task", "✏️ Update Task Status"])
    
    with tab_view:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filter_status = st.selectbox("Filter by Status", ["All", "Pending", "In Progress", "Completed"])
        with col_f2:
            all_names = ["All"] + pd.read_sql_query("SELECT full_name FROM executives UNION SELECT full_name FROM subcommittees", conn)['full_name'].tolist()
            filter_assignee = st.selectbox("Filter by Assigned Member", all_names)
            
        query = "SELECT id AS 'Task ID', title AS 'Task Title', portfolio AS 'Portfolio', assignee_name AS 'Assigned To', priority AS 'Priority', due_date AS 'Due Date', status AS 'Status' FROM tasks WHERE 1=1"
        params = []
        if filter_status != "All":
            query += " AND status = ?"
            params.append(filter_status)
        if filter_assignee != "All":
            query += " AND assignee_name = ?"
            params.append(filter_assignee)
            
        query += " ORDER BY id DESC"
        df_tasks = pd.read_sql_query(query, conn, params=params)
        st.dataframe(df_tasks, use_container_width=True, hide_index=True)
        
    with tab_add:
        st.subheader("Assign a New Task")
        with st.form("add_task_form"):
            task_title = st.text_input("Task Title / What needs to be done?")
            portfolio = st.selectbox("Portfolio / Department", [
                "Research, Innovation & Academics",
                "External Affairs & Partnerships",
                "Programs & Events",
                "Spokesperson & Public Relations",
                "Treasurer & Finance",
                "Secretariat & Editorial Directorate"
            ])
            assignees = pd.read_sql_query("SELECT full_name FROM executives UNION SELECT full_name FROM subcommittees", conn)['full_name'].tolist()
            assignee = st.selectbox("Assign To", assignees)
            priority = st.selectbox("Priority Level", ["Medium", "High", "Low"])
            due_date = st.date_input("Deadline", datetime.date.today() + datetime.timedelta(days=7))
            
            submit_task = st.form_submit_button("➕ Save & Assign Task")
            if submit_task and task_title:
                cursor = conn.cursor()
                today_str = datetime.date.today().strftime("%Y-%m-%d")
                cursor.execute(
                    "INSERT INTO tasks (title, portfolio, assignee_name, priority, due_date, status, cure_notice_sent, created_at) VALUES (?, ?, ?, ?, ?, 'Pending', 0, ?)",
                    (task_title, portfolio, assignee, priority, due_date.strftime("%Y-%m-%d"), today_str)
                )
                conn.commit()
                st.success(f"✅ Task assigned to {assignee} successfully!")
                st.rerun()

    with tab_update:
        st.subheader("Update Existing Task Status")
        tasks_df = pd.read_sql_query("SELECT id, title, assignee_name, status FROM tasks ORDER BY id DESC", conn)
        if not tasks_df.empty:
            task_dict = {f"#{row['id']} - {row['title']} ({row['assignee_name']}) [{row['status']}]": row['id'] for _, row in tasks_df.iterrows()}
            selected_task_label = st.selectbox("Select Task to Update", list(task_dict.keys()))
            selected_task_id = task_dict[selected_task_label]
            
            new_status = st.selectbox("New Status", ["Pending", "In Progress", "Completed"])
            if st.button("💾 Update Status"):
                cursor = conn.cursor()
                cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, selected_task_id))
                conn.commit()
                st.success(f"Task status updated to '{new_status}'!")
                st.rerun()
        else:
            st.info("No tasks available to update.")

# ---------------------------------------------------------
# TAB 3: TEAM ROSTER & PROFILE MANAGER
# ---------------------------------------------------------
elif menu == "👥 Team Roster & Profile Manager":
    st.title("👥 Team Roster & Member Profile Management")
    st.info("💡 **Admin Notice**: You can add emails, change member names, edit portfolio titles, update roles, or adjust academic averages at any time using the forms below.")

    tab_directory, tab_edit, tab_add_member = st.tabs(["📖 View Directory", "✏️ Edit Member / Email / Title", "➕ Add New Member"])

    with tab_directory:
        col_exec, col_sub = st.columns(2)
        with col_exec:
            st.subheader("🏛️ Executive Board Leads")
            df_execs = pd.read_sql_query("SELECT id AS 'ID', full_name AS 'Name', portfolio AS 'Portfolio Title', email AS 'Email', phone AS 'Phone', academic_avg_pct AS 'Academic Avg %' FROM executives", conn)
            st.dataframe(df_execs, use_container_width=True, hide_index=True)
            
        with col_sub:
            st.subheader("👥 Subcommittee Members")
            df_subs = pd.read_sql_query("SELECT id AS 'ID', full_name AS 'Name', portfolio AS 'Directorate', specific_role AS 'Role Title', email AS 'Email', academic_avg_pct AS 'Academic Avg %' FROM subcommittees", conn)
            st.dataframe(df_subs, use_container_width=True, hide_index=True)

    with tab_edit:
        st.subheader("✏️ Edit Existing Team Member Details")
        st.write("Select a member to modify their name, email address, portfolio title, or role.")

        member_type = st.radio("Select Member Group", ["Executive Officer", "Subcommittee Member"])
        
        if member_type == "Executive Officer":
            df_m = pd.read_sql_query("SELECT id, full_name, portfolio, email, phone, academic_avg_pct FROM executives", conn)
            if not df_m.empty:
                exec_opts = {f"{r['full_name']} — {r['portfolio']}": r['id'] for _, r in df_m.iterrows()}
                selected_label = st.selectbox("Select Executive to Edit", list(exec_opts.keys()))
                m_id = exec_opts[selected_label]
                m_data = df_m[df_m['id'] == m_id].iloc[0]

                with st.form("edit_exec_form"):
                    e_name = st.text_input("Full Name", value=m_data['full_name'])
                    e_port = st.text_input("Portfolio / Title", value=m_data['portfolio'])
                    e_email = st.text_input("Email Address", value=m_data['email'] or "")
                    e_phone = st.text_input("Phone Number", value=m_data['phone'] or "")
                    e_avg = st.number_input("Academic Average (%)", min_value=0.0, max_value=100.0, value=float(m_data['academic_avg_pct']))

                    update_exec = st.form_submit_button("💾 Save Changes to Executive Profile")
                    if update_exec:
                        cursor = conn.cursor()
                        cursor.execute(
                            "UPDATE executives SET full_name=?, portfolio=?, email=?, phone=?, academic_avg_pct=? WHERE id=?",
                            (e_name, e_port, e_email, e_phone, e_avg, m_id)
                        )
                        conn.commit()
                        st.success(f"✅ Executive profile for '{e_name}' updated successfully!")
                        st.rerun()

        else:
            df_m = pd.read_sql_query("SELECT id, full_name, portfolio, specific_role, email, academic_avg_pct FROM subcommittees", conn)
            if not df_m.empty:
                sub_opts = {f"{r['full_name']} — {r['specific_role']} ({r['portfolio']})": r['id'] for _, r in df_m.iterrows()}
                selected_label = st.selectbox("Select Subcommittee Member to Edit", list(sub_opts.keys()))
                m_id = sub_opts[selected_label]
                m_data = df_m[df_m['id'] == m_id].iloc[0]

                with st.form("edit_sub_form"):
                    s_name = st.text_input("Full Name", value=m_data['full_name'])
                    s_dept = st.text_input("Directorate / Department", value=m_data['portfolio'])
                    s_role = st.text_input("Specific Role Title", value=m_data['specific_role'])
                    s_email = st.text_input("Email Address", value=m_data['email'] or "")
                    s_avg = st.number_input("Academic Average (%)", min_value=0.0, max_value=100.0, value=float(m_data['academic_avg_pct']))

                    update_sub = st.form_submit_button("💾 Save Changes to Subcommittee Profile")
                    if update_sub:
                        cursor = conn.cursor()
                        cursor.execute(
                            "UPDATE subcommittees SET full_name=?, portfolio=?, specific_role=?, email=?, academic_avg_pct=? WHERE id=?",
                            (s_name, s_dept, s_role, s_email, s_avg, m_id)
                        )
                        conn.commit()
                        st.success(f"✅ Profile for '{s_name}' updated successfully!")
                        st.rerun()

    with tab_add_member:
        st.subheader("➕ Add New Member")
        add_type = st.radio("Add To", ["Subcommittee Member", "Executive Officer"])

        if add_type == "Subcommittee Member":
            with st.form("add_new_sub_form"):
                n_name = st.text_input("Full Name")
                n_dept = st.selectbox("Directorate", [
                    "Research, Innovation & Academics",
                    "External Affairs & Partnerships",
                    "Programs & Events",
                    "PR & Brand Management",
                    "Finance & Auditing",
                    "Secretariat & Editorial Directorate"
                ])
                n_role = st.text_input("Role Title", value="Subcommittee Officer")
                n_email = st.text_input("Email Address")
                n_avg = st.number_input("Academic Average (%)", min_value=0.0, max_value=100.0, value=65.0)

                add_btn = st.form_submit_button("➕ Save Subcommittee Member")
                if add_btn and n_name:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO subcommittees (full_name, portfolio, specific_role, email, academic_avg_pct, status) VALUES (?, ?, ?, ?, ?, 'Active')",
                        (n_name, n_dept, n_role, n_email, n_avg)
                    )
                    conn.commit()
                    st.success(f"Member '{n_name}' added successfully!")
                    st.rerun()
        else:
            with st.form("add_new_exec_form"):
                n_name = st.text_input("Full Name")
                n_port = st.text_input("Portfolio Title (e.g. Vice-Chairperson / Liaison Lead)")
                n_email = st.text_input("Email Address")
                n_phone = st.text_input("Phone Number")
                n_avg = st.number_input("Academic Average (%)", min_value=0.0, max_value=100.0, value=70.0)

                add_exec_btn = st.form_submit_button("➕ Save Executive Officer")
                if add_exec_btn and n_name:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO executives (full_name, portfolio, email, phone, academic_avg_pct, status) VALUES (?, ?, ?, ?, ?, 'Active')",
                        (n_name, n_port, n_email, n_phone, n_avg)
                    )
                    conn.commit()
                    st.success(f"Executive '{n_name}' added successfully!")
                    st.rerun()

# ---------------------------------------------------------
# TAB 4: EXECUTIVE DIRECTIVES & POLICIES
# ---------------------------------------------------------
elif menu == "📜 Executive Directives & Policies":
    st.title("📜 Executive Directives & Operational Policies")
    st.info("📜 **Governance Notice**: You can issue new Executive Directives, update policy titles, edit policy text, or publish new organizational mandates directly here.")

    tab_view_dir, tab_add_dir, tab_edit_dir = st.tabs(["📖 View Active Directives", "➕ Issue New Directive", "✏️ Edit / Update Directives"])

    with tab_view_dir:
        df_dirs = pd.read_sql_query("SELECT directive_no AS 'Directive No.', title AS 'Title', issuer AS 'Issued By', effective_date AS 'Effective Date', mandate_text AS 'Mandate / Policy Text', status AS 'Status' FROM executive_directives ORDER BY id DESC", conn)
        if not df_dirs.empty:
            for _, r in df_dirs.iterrows():
                st.markdown(f"""
                    <div class="directive-card">
                        <div class="directive-title">{r['Directive No.']}: {r['Title']}</div>
                        <div class="directive-meta">Issued by: <b>{r['Issued By']}</b> | Effective Date: <b>{r['Effective Date']}</b> | Status: <b>{r['Status']}</b></div>
                        <div>{r['Mandate / Policy Text']}</div>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown("---")
            st.dataframe(df_dirs, use_container_width=True, hide_index=True)
        else:
            st.info("No active directives logged yet.")

    with tab_add_dir:
        st.subheader("Issue a New Official Executive Directive")
        with st.form("add_directive_form"):
            d_no = st.text_input("Directive Number", value=f"Directive No. 0{pd.read_sql_query('SELECT COUNT(*) AS c FROM executive_directives', conn)['c'][0] + 1} of 2026")
            d_title = st.text_input("Directive Title / Subject")
            d_issuer = st.text_input("Issuing Authority", value="Office of the Chairperson / Executive Board")
            d_date = st.date_input("Effective Date", datetime.date.today())
            d_text = st.text_area("Directive Mandate & Policy Content (Full Text)")

            submit_d = st.form_submit_button("📜 Publish Directive")
            if submit_d and d_title and d_text:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO executive_directives (directive_no, title, issuer, effective_date, mandate_text, status) VALUES (?, ?, ?, ?, ?, 'Active')",
                    (d_no, d_title, d_issuer, d_date.strftime("%Y-%m-%d"), d_text)
                )
                conn.commit()
                st.success(f"✅ Directive '{d_no}: {d_title}' published successfully!")
                st.rerun()

    with tab_edit_dir:
        st.subheader("Edit or Update an Existing Directive")
        df_d = pd.read_sql_query("SELECT id, directive_no, title, issuer, mandate_text, status FROM executive_directives ORDER BY id DESC", conn)
        if not df_d.empty:
            d_opts = {f"{r['directive_no']} - {r['title']} [{r['status']}]": r['id'] for _, r in df_d.iterrows()}
            selected_d_label = st.selectbox("Select Directive to Edit", list(d_opts.keys()))
            selected_d_id = d_opts[selected_d_label]
            d_row = df_d[df_d['id'] == selected_d_id].iloc[0]

            with st.form("edit_directive_form"):
                ed_no = st.text_input("Directive Number", value=d_row['directive_no'])
                ed_title = st.text_input("Title", value=d_row['title'])
                ed_issuer = st.text_input("Issuing Authority", value=d_row['issuer'])
                ed_text = st.text_area("Policy Text / Mandate Content", value=d_row['mandate_text'])
                ed_status = st.selectbox("Status", ["Active", "Archived", "Under Review"])

                update_d_btn = st.form_submit_button("💾 Save Directive Updates")
                if update_d_btn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE executive_directives SET directive_no=?, title=?, issuer=?, mandate_text=?, status=? WHERE id=?",
                        (ed_no, ed_title, ed_issuer, ed_text, ed_status, selected_d_id)
                    )
                    conn.commit()
                    st.success("✅ Directive updated successfully!")
                    st.rerun()

# ---------------------------------------------------------
# TAB 5: SUBMIT FORTNIGHTLY REPORT
# ---------------------------------------------------------
elif menu == "📝 Submit Fortnightly Report":
    st.title("📝 Submit Fortnightly Progress Report")
    st.write("A simple, quick form for team leads and officers to log bi-weekly progress.")
    
    with st.form("simple_bepc_form"):
        portfolio = st.selectbox("Your Department / Directorate", [
            "Research, Innovation & Academics",
            "External Affairs & Partnerships",
            "Programs & Events",
            "Public Relations & Brand Management",
            "Finance & Treasurer",
            "Secretariat & Office of SG"
        ])
        submitter = st.text_input("Your Name")
        kpis = st.text_area("What key tasks were completed in the last 2 weeks?")
        roadblocks = st.text_area("Any challenges or assistance needed from leadership?")
        
        submit_bepc = st.form_submit_button("🚀 Submit Progress Report")
        if submit_bepc and submitter:
            cursor = conn.cursor()
            today_str = datetime.date.today().strftime("%Y-%m-%d")
            cursor.execute(
                "INSERT INTO biweekly_pulses (portfolio, submitter_name, submission_date, kpis_met, roadblocks, financial_inflow, financial_outflow, status) VALUES (?, ?, ?, ?, ?, 0.0, 0.0, 'Submitted')",
                (portfolio, submitter, today_str, kpis, roadblocks)
            )
            conn.commit()
            st.success("✅ Your report has been submitted! Thank you.")
            st.rerun()

    st.subheader("📋 Recent Submissions Log")
    df_reports = pd.read_sql_query(
        "SELECT submission_date AS 'Date', portfolio AS 'Department', submitter_name AS 'Submitted By', kpis_met AS 'Completed Tasks', roadblocks AS 'Challenges' FROM biweekly_pulses ORDER BY id DESC",
        conn
    )
    if not df_reports.empty:
        st.dataframe(df_reports, use_container_width=True, hide_index=True)
    else:
        st.info("No report submissions logged yet.")

# ---------------------------------------------------------
# TAB 6: DOCUMENT VAULT
# ---------------------------------------------------------
elif menu == "📁 Document Vault":
    st.title("📁 EDMS Key Document Vault")
    st.write("Access official society files, constitutions, rosters, and guidelines.")
    
    df_files = pd.read_sql_query("SELECT doc_category AS 'Category', doc_title AS 'Document Title', drive_url AS 'Drive Link', uploaded_by AS 'Uploaded By', upload_date AS 'Date' FROM central_files ORDER BY doc_category", conn)
    st.dataframe(df_files, use_container_width=True, hide_index=True)
    
    with st.expander("➕ Link a New Document"):
        with st.form("add_file_form"):
            cat = st.selectbox("Category", ["Governance & Legal", "Membership Roster", "External Affairs", "Brand & Media", "Finance & Reports"])
            title = st.text_input("Document Name")
            url = st.text_input("Google Drive / Link URL")
            uploader = st.text_input("Your Name")
            
            add_file = st.form_submit_button("➕ Add Link to Vault")
            if add_file and title and url:
                cursor = conn.cursor()
                today_str = datetime.date.today().strftime("%Y-%m-%d")
                cursor.execute(
                    "INSERT INTO central_files (doc_category, doc_title, drive_url, uploaded_by, upload_date) VALUES (?, ?, ?, ?, ?)",
                    (cat, title, url, uploader, today_str)
                )
                conn.commit()
                st.success(f"Document '{title}' linked successfully!")
                st.rerun()

conn.close()
