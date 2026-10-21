import sqlite3
import pandas as pd
import datetime
import streamlit as st

# Streamlit Page Setup
st.set_page_config(
    page_title="EDMS Team Portal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_NAME = "edms_clean.db"

# Custom CSS - Minimal, Modern, Professional & Total Lockscreen Styling
st.markdown("""
    <style>
    .stApp {
        background-color: #FAFAFA;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .main-header {
        background: linear-gradient(135deg, #001F3F 0%, #1A365D 100%);
        color: white;
        padding: 20px 24px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .main-header h1 {
        color: #FFFFFF !important;
        margin: 0;
        font-size: 26px;
        font-weight: 700;
    }
    .main-header p {
        color: #E2E8F0;
        margin: 4px 0 0 0;
        font-size: 14px;
    }
    .lockscreen-container {
        background-color: #FFFFFF;
        padding: 35px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-top: 6px solid #001F3F;
        text-align: center;
        margin-top: 30px;
    }
    .admin-badge {
        background-color: #2E7D32;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #001F3F;
        color: white;
        border-radius: 6px;
        font-weight: 600;
        border: none;
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
    
    # 100% BLANK TABLES - NO PRE-FILLED DATA
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT,
        portfolio_role TEXT NOT NULL,
        member_type TEXT DEFAULT 'Subcommittee'
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        assignee_name TEXT NOT NULL,
        assignee_email TEXT NOT NULL,
        due_date TEXT NOT NULL,
        priority TEXT DEFAULT 'Medium',
        status TEXT DEFAULT 'To Do',
        created_at TEXT NOT NULL
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        posted_by TEXT NOT NULL,
        posted_date TEXT NOT NULL
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS meeting_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        meeting_date TEXT NOT NULL,
        attendees TEXT,
        summary_decisions TEXT,
        document_url TEXT,
        logged_by TEXT NOT NULL
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_name TEXT NOT NULL,
        event_date TEXT NOT NULL,
        venue TEXT,
        description TEXT
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS suggestions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        submitted_by TEXT DEFAULT 'Anonymous',
        message TEXT NOT NULL,
        submitted_date TEXT NOT NULL
    )''')

    conn.commit()
    conn.close()

init_db()

# ---------------------------------------------------------
# TOTAL LOCKSCREEN AUTHENTICATION
# ---------------------------------------------------------
if 'portal_unlocked' not in st.session_state:
    st.session_state['portal_unlocked'] = False

if not st.session_state['portal_unlocked']:
    st.markdown("<br>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown("""
            <div class="lockscreen-container">
                <h2 style="color: #001F3F; margin-bottom: 5px;">⚡ EDMS Operations Portal</h2>
                <p style="color: #64748B; font-size: 15px;">Energy Development & Management Society<br>International University of Management</p>
                <hr style="margin: 20px 0; border: none; border-top: 1px solid #E2E8F0;">
                <p style="font-weight: 600; color: #1E293B; font-size: 16px;">🔒 Restricted Access Lockscreen</p>
                <p style="color: #64748B; font-size: 13px;">Please enter the leadership passcode to open the system.</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("total_lockscreen_form"):
            passcode_input = st.text_input("Portal Access Passcode", type="password", help="Default Passcode: 1234")
            submit_passcode = st.form_submit_button("🔓 Unlock Portal", use_container_width=True)
            
            if submit_passcode:
                if passcode_input == "1234":
                    st.session_state['portal_unlocked'] = True
                    st.session_state['is_executive'] = True
                    st.success("Access Granted! Unlocking Portal...")
                    st.rerun()
                else:
                    st.error("❌ Incorrect Passcode. Access Denied.")
    st.stop() # Stops execution so nothing else renders when locked

# ---------------------------------------------------------
# UNLOCKED PORTAL INTERFACE
# ---------------------------------------------------------

# Sidebar Controls
st.sidebar.title("⚡ EDMS Navigation")
st.sidebar.markdown("<span class='admin-badge'>🔓 Portal Unlocked (Full Access)</span>", unsafe_allow_html=True)

if st.sidebar.button("🔒 Lock Portal / Log Out", use_container_width=True):
    st.session_state['portal_unlocked'] = False
    st.session_state['is_executive'] = False
    st.rerun()

st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Go to Section:",
    [
        "📢 Notice Board",
        "📋 Task Board & Email Logger",
        "👥 Team Roster",
        "📝 Meeting Notes & Documents",
        "📅 Event Calendar",
        "💡 Member Suggestion Box"
    ]
)

conn = get_connection()

# Header Banner
st.markdown("""
    <div class="main-header">
        <h1>⚡ Energy Development & Management Society Portal</h1>
        <p>International University of Management — Central Operations System</p>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SECTION 1: NOTICE BOARD
# ---------------------------------------------------------
if menu == "📢 Notice Board":
    st.title("📢 Notice Board & Announcements")
    st.write("Official announcements, updates, and notices from executive leadership.")
    
    with st.expander("➕ Post New Announcement", expanded=False):
        with st.form("add_notice_form"):
            n_title = st.text_input("Announcement Title")
            n_by = st.text_input("Posted By (Your Name & Title)")
            n_content = st.text_area("Announcement Message / Details")
            
            submit_notice = st.form_submit_button("📢 Publish Announcement")
            if submit_notice and n_title and n_content:
                cursor = conn.cursor()
                today_str = datetime.date.today().strftime("%Y-%m-%d")
                cursor.execute(
                    "INSERT INTO announcements (title, content, posted_by, posted_date) VALUES (?, ?, ?, ?)",
                    (n_title, n_content, n_by or "Executive Directorate", today_str)
                )
                conn.commit()
                st.success("Announcement published successfully!")
                st.rerun()

    df_notices = pd.read_sql_query("SELECT title AS 'Title', content AS 'Message', posted_by AS 'Posted By', posted_date AS 'Date' FROM announcements ORDER BY id DESC", conn)
    
    if not df_notices.empty:
        for _, row in df_notices.iterrows():
            st.info(f"### 📌 {row['Title']}\n**Posted by:** {row['Posted By']} | **Date:** {row['Date']}\n\n{row['Message']}")
            st.markdown("---")
    else:
        st.info("ℹ️ No announcements posted yet. Starting 100% blank!")

# ---------------------------------------------------------
# SECTION 2: TASK BOARD & EMAIL LOGGER
# ---------------------------------------------------------
elif menu == "📋 Task Board & Email Logger":
    st.title("📋 Task Board & Email Logger")
    st.write("Assign tasks directly to team members with their contact email logged.")
    
    tab_view, tab_add, tab_status = st.tabs(["🔍 View Tasks", "➕ Assign New Task", "✏️ Update Task Status"])
    
    with tab_add:
        st.subheader("Assign a Task & Log Contact Email")
        with st.form("add_task_form"):
            t_title = st.text_input("Task Description / What needs to be done?")
            
            members_df = pd.read_sql_query("SELECT full_name, email FROM members", conn)
            
            col_name, col_email = st.columns(2)
            with col_name:
                if not members_df.empty:
                    t_assignee = st.selectbox("Assign To (From Roster)", members_df['full_name'].tolist())
                    selected_email = members_df[members_df['full_name'] == t_assignee]['email'].values[0]
                else:
                    t_assignee = st.text_input("Assign To (Full Name)")
                    selected_email = ""
            
            with col_email:
                t_email = st.text_input("Assignee Email Address", value=selected_email)
            
            col_p, col_d = st.columns(2)
            with col_p:
                t_priority = st.selectbox("Priority Level", ["Medium", "High", "Low"])
            with col_d:
                t_due = st.date_input("Due Date", datetime.date.today() + datetime.timedelta(days=7))
            
            submit_task = st.form_submit_button("➕ Log Task & Assign Email")
            if submit_task and t_title and t_assignee:
                cursor = conn.cursor()
                today_str = datetime.date.today().strftime("%Y-%m-%d")
                cursor.execute(
                    "INSERT INTO tasks (title, assignee_name, assignee_email, due_date, priority, status, created_at) VALUES (?, ?, ?, ?, ?, 'To Do', ?)",
                    (t_title, t_assignee, t_email, t_due.strftime("%Y-%m-%d"), t_priority, today_str)
                )
                conn.commit()
                st.success(f"✅ Task logged for {t_assignee} ({t_email})!")
                st.rerun()

    with tab_status:
        st.subheader("Update Task Status")
        tasks_df = pd.read_sql_query("SELECT id, title, assignee_name, status FROM tasks ORDER BY id DESC", conn)
        if not tasks_df.empty:
            task_dict = {f"#{r['id']} - {r['title']} ({r['assignee_name']}) [{r['status']}]": r['id'] for _, r in tasks_df.iterrows()}
            selected_label = st.selectbox("Select Task to Update", list(task_dict.keys()))
            task_id = task_dict[selected_label]
            
            new_status = st.selectbox("New Status", ["To Do", "In Progress", "Completed"])
            if st.button("💾 Save Status Update"):
                cursor = conn.cursor()
                cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
                conn.commit()
                st.success(f"Task status updated to '{new_status}'!")
                st.rerun()
        else:
            st.info("No tasks logged yet.")

    with tab_view:
        df_all_tasks = pd.read_sql_query(
            "SELECT id AS 'Task ID', title AS 'Task Description', assignee_name AS 'Assigned To', assignee_email AS 'Contact Email', due_date AS 'Due Date', priority AS 'Priority', status AS 'Status' FROM tasks ORDER BY id DESC",
            conn
        )
        if not df_all_tasks.empty:
            st.subheader("📋 Current Task Board")
            st.dataframe(df_all_tasks, use_container_width=True, hide_index=True)
        else:
            st.info("ℹ️ Task board is currently empty. Starting 100% blank!")

# ---------------------------------------------------------
# SECTION 3: TEAM ROSTER
# ---------------------------------------------------------
elif menu == "👥 Team Roster":
    st.title("👥 Team Roster & Contact Directory")
    st.write("Browse team members and access their contact emails.")
    
    with st.expander("➕ Add / Edit Team Members", expanded=False):
        tab_add_m, tab_edit_m = st.tabs(["➕ Add New Member", "✏️ Edit Member Profile"])
        
        with tab_add_m:
            with st.form("add_member_form"):
                m_name = st.text_input("Full Name")
                m_email = st.text_input("Email Address")
                m_phone = st.text_input("Phone Number")
                m_role = st.text_input("Portfolio / Role Title (e.g. Secretary General, Research Lead, Events Member)")
                m_type = st.selectbox("Member Category", ["Executive Board", "Subcommittee Member", "General Member"])
                
                submit_member = st.form_submit_button("➕ Save Team Member")
                if submit_member and m_name and m_email:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO members (full_name, email, phone, portfolio_role, member_type) VALUES (?, ?, ?, ?, ?)",
                        (m_name, m_email, m_phone, m_role, m_type)
                    )
                    conn.commit()
                    st.success(f"Added {m_name} to the team roster!")
                    st.rerun()

        with tab_edit_m:
            m_list = pd.read_sql_query("SELECT id, full_name, email, portfolio_role FROM members", conn)
            if not m_list.empty:
                m_dict = {f"{r['full_name']} ({r['portfolio_role']})": r['id'] for _, r in m_list.iterrows()}
                selected_m = st.selectbox("Select Member to Manage", list(m_dict.keys()))
                m_id = m_dict[selected_m]
                
                m_data = m_list[m_list['id'] == m_id].iloc[0]
                
                with st.form("edit_m_form"):
                    e_name = st.text_input("Full Name", value=m_data['full_name'])
                    e_email = st.text_input("Email", value=m_data['email'])
                    e_role = st.text_input("Role Title", value=m_data['portfolio_role'])
                    
                    save_m = st.form_submit_button("💾 Update Member Profile")
                    if save_m:
                        cursor = conn.cursor()
                        cursor.execute("UPDATE members SET full_name=?, email=?, portfolio_role=? WHERE id=?", (e_name, e_email, e_role, m_id))
                        conn.commit()
                        st.success("Member updated!")
                        st.rerun()
            else:
                st.info("No members in directory yet.")

    df_members = pd.read_sql_query(
        "SELECT full_name AS 'Full Name', portfolio_role AS 'Role / Title', email AS 'Contact Email', phone AS 'Phone', member_type AS 'Category' FROM members ORDER BY member_type, full_name",
        conn
    )
    if not df_members.empty:
        st.dataframe(df_members, use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ Team roster is currently empty. Add members above!")

# ---------------------------------------------------------
# SECTION 4: MEETING NOTES & DOCUMENTS
# ---------------------------------------------------------
elif menu == "📝 Meeting Notes & Documents":
    st.title("📝 Meeting Notes & Document Repository")
    st.write("Log agendas, meeting summaries, and document links.")
    
    with st.expander("➕ Log New Meeting Notes or Document", expanded=False):
        with st.form("add_meeting_form"):
            m_title = st.text_input("Meeting / Document Title (e.g. End of Year Joint Meeting Agenda)")
            m_date = st.date_input("Meeting Date", datetime.date.today())
            m_attendees = st.text_input("Attendees Present")
            m_summary = st.text_area("Key Decisions / Minutes Summary")
            m_url = st.text_input("Google Drive / Document Link (Optional)")
            m_logged_by = st.text_input("Logged By (Your Name)")
            
            submit_m = st.form_submit_button("📝 Save Meeting Record")
            if submit_m and m_title:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO meeting_notes (title, meeting_date, attendees, summary_decisions, document_url, logged_by) VALUES (?, ?, ?, ?, ?, ?)",
                    (m_title, m_date.strftime("%Y-%m-%d"), m_attendees, m_summary, m_url, m_logged_by)
                )
                conn.commit()
                st.success("Meeting record saved successfully!")
                st.rerun()

    df_meetings = pd.read_sql_query(
        "SELECT meeting_date AS 'Date', title AS 'Title / Document', attendees AS 'Attendees', summary_decisions AS 'Key Decisions', document_url AS 'Link', logged_by AS 'Logged By' FROM meeting_notes ORDER BY id DESC",
        conn
    )
    if not df_meetings.empty:
        st.dataframe(df_meetings, use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ No meeting records logged yet. Starting 100% blank!")

# ---------------------------------------------------------
# SECTION 5: EVENT CALENDAR
# ---------------------------------------------------------
elif menu == "📅 Event Calendar":
    st.title("📅 Upcoming Society Events & Calendar")
    st.write("Keep track of upcoming meetings, site visits, workshops, and deadlines.")
    
    with st.expander("➕ Schedule New Event", expanded=False):
        with st.form("add_event_form"):
            e_title = st.text_input("Event Name")
            e_date = st.date_input("Event Date")
            e_venue = st.text_input("Venue / Room")
            e_desc = st.text_area("Event Description / Agenda")
            
            submit_e = st.form_submit_button("📅 Add Event")
            if submit_e and e_title:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO events (event_name, event_date, venue, description) VALUES (?, ?, ?, ?)",
                    (e_title, e_date.strftime("%Y-%m-%d"), e_venue, e_desc)
                )
                conn.commit()
                st.success("Event scheduled!")
                st.rerun()

    df_events = pd.read_sql_query("SELECT event_date AS 'Date', event_name AS 'Event', venue AS 'Venue', description AS 'Details' FROM events ORDER BY event_date ASC", conn)
    if not df_events.empty:
        st.dataframe(df_events, use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ Event calendar is empty.")

# ---------------------------------------------------------
# SECTION 6: MEMBER SUGGESTION BOX
# ---------------------------------------------------------
elif menu == "💡 Member Suggestion Box":
    st.title("💡 Member Suggestion Box")
    st.write("Submit ideas, feedback, or suggestions for the leadership team to discuss in meetings.")
    
    with st.form("suggestion_form"):
        s_by = st.text_input("Your Name (Leave blank for Anonymous)", value="")
        s_msg = st.text_area("Your Suggestion / Idea for EDMS")
        
        submit_s = st.form_submit_button("💡 Send Suggestion")
        if submit_s and s_msg:
            cursor = conn.cursor()
            today_str = datetime.date.today().strftime("%Y-%m-%d")
            cursor.execute(
                "INSERT INTO suggestions (submitted_by, message, submitted_date) VALUES (?, ?, ?)",
                (s_by or "Anonymous", s_msg, today_str)
            )
            conn.commit()
            st.success("Thank you! Your suggestion has been logged.")
            st.rerun()

    st.subheader("💡 Logged Suggestions")
    df_sug = pd.read_sql_query("SELECT submitted_date AS 'Date', submitted_by AS 'From', message AS 'Suggestion' FROM suggestions ORDER BY id DESC", conn)
    if not df_sug.empty:
        st.dataframe(df_sug, use_container_width=True, hide_index=True)
    else:
        st.info("No suggestions received yet.")

conn.close()
