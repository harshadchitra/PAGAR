import streamlit as st
import sqlite3
import datetime
import calendar
import io
import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ----------------- પેજ વિગતો અને થીમ સેટઅપ -----------------
st.set_page_config(
    page_title="Payroll & Master Expense Pro",
    page_icon="⚡",
    layout="wide"
)

# Uploads Folder Create
if not os.path.exists("uploaded_bills"):
    os.makedirs("uploaded_bills")

# Custom High-End Modern CSS Styling
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    .pro-header {
        background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(59, 130, 246, 0.3);
        margin-bottom: 25px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .pro-header h1 {
        margin: 0;
        font-size: 30px;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: 0.5px;
    }
    .pro-header p {
        margin: 8px 0 0 0;
        font-size: 14px;
        color: #e2e8f0;
    }
    .section-title {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-left: 4px solid #3b82f6;
        padding: 12px 18px;
        border-radius: 0 10px 10px 0;
        font-size: 18px;
        font-weight: 700;
        color: #38bdf8;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    [data-testid="stSidebar"] {
        background: #090d16;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    [data-testid="stSidebar"] * {
        color: #cbd5e1 !important;
    }
    textarea, input {
        color: #0f172a !important;
    }
    .stButton>button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border-radius: 10px;
        font-weight: 600;
        border: none;
        padding: 10px 20px;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(59, 130, 246, 0.6);
    }
</style>
""", unsafe_allow_html=True)

# ----------------- ડેટાબેઝ કનેક્શન (લોકલ SQLite - ૧૦૦% એરર ફ્રી) -----------------
def get_db_connection():
    conn = sqlite3.connect("payroll_mobile.db", check_same_thread=False)
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            designation TEXT,
            daily_rate REAL,
            mobile TEXT,
            address TEXT,
            work_type TEXT,
            shift_timing TEXT
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_name TEXT,
            date TEXT,
            status TEXT,
            overtime_amt REAL DEFAULT 0.0,
            UNIQUE(staff_name, date)
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS advance_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_name TEXT,
            date TEXT,
            amount REAL,
            note TEXT
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS salary_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_name TEXT,
            month_year TEXT,
            payable_days REAL,
            gross_salary REAL,
            advance_deduction REAL,
            net_salary REAL,
            paid_date TEXT,
            UNIQUE(staff_name, month_year)
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            category TEXT,
            amount REAL,
            details TEXT,
            bill_file TEXT
        );
    """)
    
    conn.commit()
    cursor.close()
    conn.close()

init_db()

# ----------------- DIGITAL SALARY SLIP PDF -----------------
def generate_single_salary_slip_story(story, staff_name, month_year, total_days, present_days, half_days, absent_days, daily_rate, gross_salary, advance_deduction, net_salary, total_overtime=0.0):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#0f172a'), alignment=1, spaceAfter=2)
    sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#475569'), alignment=1, spaceAfter=15)
    head_style = ParagraphStyle('HeadStyle', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#2563eb'), alignment=1, spaceAfter=15)
    normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontSize=10, leading=14)

    story.append(Paragraph("COURIER SOLUTION - PAYROLL PRO", title_style))
    story.append(Paragraph("Digital Verified Salary Slip Statement", sub_style))
    story.append(Paragraph(f"SALARY SLIP FOR {month_year.upper()}", head_style))

    data_info = [
        [Paragraph(f"<b>Staff Name:</b> {staff_name}", normal_style), Paragraph(f"<b>Date:</b> {datetime.date.today().strftime('%d/%m/%Y')}", normal_style)],
        [Paragraph(f"<b>Daily Rate:</b> RS {daily_rate:,.2f}", normal_style), Paragraph(f"<b>Working Period:</b> {month_year}", normal_style)]
    ]
    t_info = Table(data_info, colWidths=[250, 250])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#3b82f6')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 15))

    data_att = [
        [Paragraph("<b>Attendance Metrics</b>", normal_style), Paragraph("<b>Days / Amount</b>", normal_style)],
        [Paragraph("Total Days in Month", normal_style), Paragraph(str(total_days), normal_style)],
        [Paragraph("Full Present Days", normal_style), Paragraph(str(present_days), normal_style)],
        [Paragraph("Half Days", normal_style), Paragraph(str(half_days), normal_style)],
        [Paragraph("Absent Days", normal_style), Paragraph(str(absent_days), normal_style)],
        [Paragraph("Overtime Bonus / Extra", normal_style), Paragraph(f"RS {total_overtime:,.2f}", normal_style)],
    ]
    t_att = Table(data_att, colWidths=[330, 170])
    t_att.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e1b4b')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_att)
    story.append(Spacer(1, 15))

    data_sal = [
        [Paragraph("<b>Salary Breakdown</b>", normal_style), Paragraph("<b>Amount (RS)</b>", normal_style)],
        [Paragraph("Gross Earned Salary (incl. Overtime)", normal_style), Paragraph(f"RS {gross_salary:,.2f}", normal_style)],
        [Paragraph("Less: Advance Deduction", normal_style), Paragraph(f"- RS {advance_deduction:,.2f}", normal_style)],
        [Paragraph("<b>NET PAYABLE SALARY</b>", normal_style), Paragraph(f"<b>RS {net_salary:,.2f}</b>", normal_style)]
    ]
    t_sal = Table(data_sal, colWidths=[330, 170])
    t_sal.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#15803d')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#dcfce7')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_sal)
    story.append(Spacer(1, 30))

    data_sign = [
        [Paragraph("<b>Employee Signature</b>", normal_style), Paragraph("<b>Authorized Signatory</b>", ParagraphStyle('R', parent=normal_style, alignment=2))]
    ]
    t_sign = Table(data_sign, colWidths=[250, 250])
    story.append(t_sign)

def generate_salary_slip_pdf_bytes(staff_name, month_year, total_days, present_days, half_days, absent_days, daily_rate, gross_salary, advance_deduction, net_salary, total_overtime=0.0):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    generate_single_salary_slip_story(story, staff_name, month_year, total_days, present_days, half_days, absent_days, daily_rate, gross_salary, advance_deduction, net_salary, total_overtime)
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# ----------------- MASTER REPORT PDF GENERATOR -----------------
def generate_master_report_pdf_bytes(month_year_str, total_paid_salary, total_office_expenses, grand_total, exp_records, sal_records):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#0f172a'), alignment=1, spaceAfter=2)
    sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#475569'), alignment=1, spaceAfter=15)
    head_style = ParagraphStyle('HeadStyle', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#2563eb'), alignment=1, spaceAfter=10)
    normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontSize=9, leading=12)

    story.append(Paragraph("COURIER SOLUTION - MONTHLY MASTER REPORT", title_style))
    story.append(Paragraph(f"Summary Statement for Period: {month_year_str}", sub_style))

    data_summary = [
        [Paragraph("<b>Category Summary</b>", normal_style), Paragraph("<b>Amount (RS)</b>", normal_style)],
        [Paragraph("Total Paid Salary", normal_style), Paragraph(f"RS {total_paid_salary:,.2f}", normal_style)],
        [Paragraph("Total Office Expenses", normal_style), Paragraph(f"RS {total_office_expenses:,.2f}", normal_style)],
        [Paragraph("<b>GRAND TOTAL MONTHLY EXPENSE</b>", normal_style), Paragraph(f"<b>RS {grand_total:,.2f}</b>", normal_style)]
    ]
    t_sum = Table(data_summary, colWidths=[330, 170])
    t_sum.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e1b4b')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#e2e8f0')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_sum)
    story.append(Spacer(1, 15))

    story.append(Paragraph("Daily Expenses Breakup", head_style))
    exp_table_data = [[Paragraph("<b>Date</b>", normal_style), Paragraph("<b>Category</b>", normal_style), Paragraph("<b>Amount</b>", normal_style), Paragraph("<b>Details</b>", normal_style)]]
    for r in exp_records:
        exp_table_data.append([Paragraph(str(r[0]), normal_style), Paragraph(str(r[1]), normal_style), Paragraph(f"RS {r[2]:,.2f}", normal_style), Paragraph(str(r[3]), normal_style)])
    
    t_exp = Table(exp_table_data, colWidths=[80, 140, 100, 180])
    t_exp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_exp)
    story.append(Spacer(1, 15))

    story.append(Paragraph("Paid Salaries Statement", head_style))
    sal_table_data = [[Paragraph("<b>Staff Name</b>", normal_style), Paragraph("<b>Days</b>", normal_style), Paragraph("<b>Gross</b>", normal_style), Paragraph("<b>Advance</b>", normal_style), Paragraph("<b>Net Paid</b>", normal_style)]]
    for s in sal_records:
        sal_table_data.append([Paragraph(str(s[0]), normal_style), Paragraph(str(s[1]), normal_style), Paragraph(f"RS {s[2]:,.2f}", normal_style), Paragraph(f"RS {s[3]:,.2f}", normal_style), Paragraph(f"RS {s[4]:,.2f}", normal_style)])

    t_sal = Table(sal_table_data, colWidths=[140, 60, 100, 100, 100])
    t_sal.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#15803d')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_sal)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# ----------------- MAIN HEADER UI -----------------
st.markdown("""
<div class="pro-header">
    <h1>⚡ COURIER SOLUTION - PAYROLL & MASTER EXPENSE PRO</h1>
    <p>Staff Attendance, Shift, Overtime, Daily Expense & Monthly Master Analytics (Secure Local Mode)</p>
</div>
""", unsafe_allow_html=True)

menu = [
    "📅 Daily Attendance (હાજરી પૂરો)",
    "📊 Monthly Calendar View (કેલેન્ડર)",
    "💰 Salary & Digital Slip (પગાર & લિસ્ટ)",
    "💸 Advance Entry (ઉપાડ)",
    "📝 Daily Expenses (દૈનિક ખર્ચ / બિલ)",
    "📊 Master Report (માસિક માસ્ટર રિપોર્ટ)",
    "👤 Manage Staff (કર્મચારી)",
    "💾 Backup & Restore (બેકઅપ & રીસ્ટોર)"
]

st.sidebar.markdown("### 🚀 Navigation Menu")
choice = st.sidebar.radio("", menu)

# --- 1. DAILY ATTENDANCE ---
if choice == "📅 Daily Attendance (હાજરી પૂરો)":
    st.markdown('<div class="section-title">📅 રોજની હાજરી પૂરો & ઓવર ટાઈમ</div>', unsafe_allow_html=True)
    
    col_d1, col_d2 = st.columns([1, 2])
    with col_d1:
        att_date = st.date_input("તારીખ પસંદ કરો", datetime.date.today())

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, work_type, shift_timing FROM staff ORDER BY name ASC")
    staff_rows = cursor.fetchall()

    if not staff_rows:
        st.warning("⚠️ કોઈ કર્મચારી ઉમેરેલ નથી! પહેલા 'Manage Staff' માં જઈને ઉમેરો.")
    else:
        st.write("")
        att_data = {}
        for staff, w_type, shift in staff_rows:
            cursor.execute("SELECT status, overtime_amt FROM attendance WHERE staff_name=? AND date=?", (staff, str(att_date)))
            row = cursor.fetchone()
            default_idx = 0
            def_ot = 0.0
            if row:
                if row[0] == "Absent": default_idx = 1
                elif row[0] == "Half": default_idx = 2
                def_ot = row[1] if row[1] else 0.0

            col1, col2, col3 = st.columns([2, 1.5, 1.5])
            with col1:
                shift_info = f" ({w_type} | {shift})" if shift else ""
                st.markdown(f"👤 **{staff}** <small style='color:#94a3b8'>{shift_info}</small>", unsafe_allow_html=True)
            with col2:
                status = st.selectbox(f"Status for {staff}", ["Present", "Absent", "Half"], index=default_idx, key=f"att_{staff}", label_visibility="collapsed")
            with col3:
                ot_val = st.number_input(f"OT (RS) for {staff}", min_value=0.0, value=def_ot, step=50.0, key=f"ot_{staff}", label_visibility="collapsed")
                att_data[staff] = (status, ot_val)

        st.write("---")
        if st.button("💾 Save Attendance & Overtime", type="primary", use_container_width=True):
            for staff, (status, ot_amt) in att_data.items():
                cursor.execute("""
                    INSERT INTO attendance (staff_name, date, status, overtime_amt)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(staff_name, date) DO UPDATE SET status=excluded.status, overtime_amt=excluded.overtime_amt
                """, (staff, str(att_date), status, ot_amt))
            conn.commit()
            cursor.close()
            conn.close()
            st.success(f"✅ તારીખ {att_date} ની હાજરી અને ઓવર ટાઈમ સફળતાપૂર્વક સેવ થઈ ગયા!")
            st.rerun()
    cursor.close()
    conn.close()

# --- 2. MONTHLY CALENDAR VIEW ---
elif choice == "📊 Monthly Calendar View (કેલેન્ડર)":
    st.markdown('<div class="section-title">📊 આખા મહિનાનું હાજરી કેલેન્ડર</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        month = st.number_input("મહિનો (1-12)", min_value=1, max_value=12, value=datetime.date.today().month)
    with col2:
        year = st.number_input("વર્ષ (Year)", min_value=2020, max_value=2030, value=datetime.date.today().year)

    max_days = calendar.monthrange(int(year), int(month))[1]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM staff ORDER BY name ASC")
    staff_list = [r[0] for r in cursor.fetchall()]

    if staff_list:
        start_date = f"{year}-{int(month):02d}-01"
        end_date = f"{year}-{int(month):02d}-{max_days}"
        
        cursor.execute("SELECT staff_name, date, status FROM attendance WHERE date BETWEEN ? AND ?", (start_date, end_date))
        att_records = cursor.fetchall()

        att_dict = {}
        for staff, date_str, status in att_records:
            day_num = int(str(date_str).split("-")[2])
            if staff not in att_dict: att_dict[staff] = {}
            att_dict[staff][day_num] = status[0].upper()

        table_rows = []
        for staff in staff_list:
            row = {"Staff Name": staff}
            p, a, h = 0, 0, 0
            for d in range(1, max_days + 1):
                val = att_dict.get(staff, {}).get(d, "-")
                row[str(d)] = val
                if val == "P": p += 1
                elif val == "A": a += 1
                elif val == "H":
                    h += 1
                    p += 0.5
            row["Tot P"] = p
            row["Tot A"] = a
            row["Tot H"] = h
            table_rows.append(row)

        st.dataframe(table_rows, use_container_width=True)
        st.info("💡 **P** = Present (હાજર), **A** = Absent (ગેરહાજર), **H** = Half Day (અડધો દિવસ)")
    cursor.close()
    conn.close()

# --- 3. SALARY & PAID STATUS LIST ---
elif choice == "💰 Salary & Digital Slip (પગાર & લિસ્ટ)":
    st.markdown('<div class="section-title">💰 માસિક પગાર ગણતરી, સ્લિપ & પેઇડ/પેન્ડિંગ લિસ્ટ</div>', unsafe_allow_html=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM staff ORDER BY name ASC")
    staff_list = [r[0] for r in cursor.fetchall()]

    if not staff_list:
        st.warning("⚠️ કોઈ કર્મચારી ઉમેરેલ નથી!")
    else:
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            sel_month = st.number_input("મહિનો પસંદ કરો", min_value=1, max_value=12, value=datetime.date.today().month, key="s_m")
        with col_m2:
            sel_year = st.number_input("વર્ષ પસંદ કરો", min_value=2020, max_value=2030, value=datetime.date.today().year, key="s_y")

        month_year_str = f"{int(sel_month):02d}-{int(sel_year)}"

        st.write("---")
        st.markdown(f"### 📋 કર્મચારીઓનું માસિક લિસ્ટ ({month_year_str})")

        cursor.execute("SELECT staff_name, id, net_salary, payable_days, gross_salary, advance_deduction FROM salary_history WHERE month_year=?", (month_year_str,))
        paid_records = {row[0]: {"id": row[1], "net": row[2], "days": row[3], "gross": row[4], "adv": row[5]} for row in cursor.fetchall()}

        h_col1, h_col2, h_col3, h_col4, h_col5 = st.columns([2, 2.5, 1.5, 1, 1.5])
        with h_col1: st.markdown("**Staff Name**")
        with h_col2: st.markdown("**Status**")
        with h_col3: st.markdown("**Net Salary**")
        with h_col4: st.markdown("**Record ID**")
        with h_col5: st.markdown("**Print Slip**")
        st.write("---")

        for staff in staff_list:
            col1, col2, col3, col4, col5 = st.columns([2, 2.5, 1.5, 1, 1.5])
            with col1: st.write(f"👤 **{staff}**")
            with col2:
                if staff in paid_records:
                    st.markdown("🟢 **PAID (ચૂકવાઈ ગયો)**")
                else:
                    st.markdown("🟠 **PENDING (બાકી છે)**")
            with col3:
                if staff in paid_records:
                    st.write(f"RS {paid_records[staff]['net']:,.2f}")
                else:
                    st.write("---")
            with col4:
                if staff in paid_records:
                    st.write(f"#{paid_records[staff]['id']}")
                else:
                    st.write("---")
            with col5:
                if staff in paid_records:
                    cursor.execute("SELECT daily_rate FROM staff WHERE name=?", (staff,))
                    d_rate_res = cursor.fetchone()
                    daily_rate = d_rate_res[0] if d_rate_res else 0.0
                    
                    max_days = calendar.monthrange(int(sel_year), int(sel_month))[1]
                    start_date = f"{sel_year}-{int(sel_month):02d}-01"
                    end_date = f"{sel_year}-{int(sel_month):02d}-{max_days}"
                    
                    cursor.execute("SELECT status, overtime_amt FROM attendance WHERE staff_name=? AND date BETWEEN ? AND ?", (staff, start_date, end_date))
                    att_rows = cursor.fetchall()
                    present_count = sum(1 for r in att_rows if r[0] == "Present")
                    half_count = sum(1 for r in att_rows if r[0] == "Half")
                    absent_count = sum(1 for r in att_rows if r[0] == "Absent")
                    tot_ot = sum(r[1] for r in att_rows if r[1])

                    pdf_bytes = generate_salary_slip_pdf_bytes(
                        staff_name=staff,
                        month_year=month_year_str,
                        total_days=max_days,
                        present_days=present_count,
                        half_days=half_count,
                        absent_days=absent_count,
                        daily_rate=daily_rate,
                        gross_salary=paid_records[staff]['gross'],
                        advance_deduction=paid_records[staff]['adv'],
                        net_salary=paid_records[staff]['net'],
                        total_overtime=tot_ot
                    )
                    
                    st.download_button(
                        label="🖨️ Print Slip",
                        data=pdf_bytes,
                        file_name=f"Salary_Slip_{staff}_{month_year_str}.pdf",
                        mime="application/pdf",
                        key=f"print_slip_{staff}_{month_year_str}"
                    )
                else:
                    st.write("---")

        st.write("---")
        st.markdown('<div class="section-title">🧮 નવો પગાર ગણો અને સ્લિપ બનાવો</div>', unsafe_allow_html=True)
        
        select_options = ["🌐 All Staff (બધા કર્મચારીઓ એકસાથે)"] + staff_list
        sal_staff_choice = st.selectbox("જેનો પગાર બાકી છે તે કર્મચારી પસંદ કરો", select_options)

        if st.button("🧮 Calculate & Generate Salary Slip", type="primary", use_container_width=True):
            max_days = calendar.monthrange(int(sel_year), int(sel_month))[1]
            start_date = f"{sel_year}-{int(sel_month):02d}-01"
            end_date = f"{sel_year}-{int(sel_month):02d}-{max_days}"
            paid_date_str = datetime.date.today().strftime("%Y-%m-%d")

            if sal_staff_choice == "🌐 All Staff (બધા કર્મચારીઓ એકસાથે)":
                calculated_count = 0
                for s_item in staff_list:
                    if s_item not in paid_records:
                        cursor.execute("SELECT daily_rate FROM staff WHERE name=?", (s_item,))
                        daily_rate = cursor.fetchone()[0]

                        cursor.execute("SELECT status, overtime_amt FROM attendance WHERE staff_name=? AND date BETWEEN ? AND ?", (s_item, start_date, end_date))
                        att_rows = cursor.fetchall()
                        present_count = sum(1 for r in att_rows if r[0] == "Present")
                        half_count = sum(1 for r in att_rows if r[0] == "Half")
                        tot_ot = sum(r[1] for r in att_rows if r[1])

                        cursor.execute("SELECT SUM(amount) FROM advance_payments WHERE staff_name=? AND date BETWEEN ? AND ?", (s_item, start_date, end_date))
                        adv_row = cursor.fetchone()
                        adv_amt = adv_row[0] if adv_row[0] else 0.0

                        payable_days = present_count + (half_count * 0.5)
                        gross_salary = (payable_days * daily_rate) + tot_ot
                        net_salary = max(0.0, gross_salary - adv_amt)

                        cursor.execute("""
                            INSERT OR IGNORE INTO salary_history (staff_name, month_year, payable_days, gross_salary, advance_deduction, net_salary, paid_date)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (s_item, month_year_str, payable_days, gross_salary, adv_amt, net_salary, paid_date_str))
                        calculated_count += 1
                
                conn.commit()
                cursor.close()
                conn.close()
                if calculated_count > 0:
                    st.success(f"✅ કુલ {calculated_count} કર્મચારીઓનો પગાર એકસાથે સફળતાપૂર્વક કેલ્ક્યુલેટ થઈ ગયો!")
                    st.rerun()
                else:
                    st.info("બધા કર્મચારીઓનો પગાર પહેલેથી જ ચૂકવાઈ ગયેલ છે!")
            else:
                if sal_staff_choice in paid_records:
                    st.warning(f"⚠️ કર્મચારી '{sal_staff_choice}' નો પગાર આ મહિના માટે પહેલેથી ચૂકવાઈ ગયેલ છે!")
                else:
                    cursor.execute("SELECT daily_rate FROM staff WHERE name=?", (sal_staff_choice,))
                    daily_rate = cursor.fetchone()[0]

                    cursor.execute("SELECT status, overtime_amt FROM attendance WHERE staff_name=? AND date BETWEEN ? AND ?", (sal_staff_choice, start_date, end_date))
                    att_rows = cursor.fetchall()
                    present_count = sum(1 for r in att_rows if r[0] == "Present")
                    half_count = sum(1 for r in att_rows if r[0] == "Half")
                    tot_ot = sum(r[1] for r in att_rows if r[1])

                    cursor.execute("SELECT SUM(amount) FROM advance_payments WHERE staff_name=? AND date BETWEEN ? AND ?", (sal_staff_choice, start_date, end_date))
                    adv_row = cursor.fetchone()
                    adv_amt = adv_row[0] if adv_row[0] else 0.0

                    payable_days = present_count + (half_count * 0.5)
                    gross_salary = (payable_days * daily_rate) + tot_ot
                    net_salary = max(0.0, gross_salary - adv_amt)

                    cursor.execute("""
                        INSERT OR IGNORE INTO salary_history (staff_name, month_year, payable_days, gross_salary, advance_deduction, net_salary, paid_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (sal_staff_choice, month_year_str, payable_days, gross_salary, adv_amt, net_salary, paid_date_str))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success(f"✅ '{sal_staff_choice}' નો પગાર સફળતાપૂર્વક જમા થઈ ગયો!")
                    st.rerun()

        st.write("---")
        st.markdown('<div class="section-title">🗑️ પગાર રેકોર્ડ ડિલીટ કરો</div>', unsafe_allow_html=True)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, staff_name, month_year, net_salary, paid_date FROM salary_history ORDER BY id DESC")
        all_history = cursor.fetchall()

        if all_history:
            hist_options = {f"ID: #{r[0]} | Staff: {r[1]} | Month: {r[2]} | Net: RS {r[3]}": r[0] for r in all_history}
            selected_hist_label = st.selectbox("ડિલીટ કરવા માટે રેકોર્ડ પસંદ કરો", list(hist_options.keys()))
            
            if st.button("🗑️ Delete Selected Salary Record", type="secondary"):
                del_id = hist_options[selected_hist_label]
                cursor.execute("DELETE FROM salary_history WHERE id=?", (del_id,))
                conn.commit()
                cursor.close()
                conn.close()
                st.success("✅ પગાર રેકોર્ડ સફળતાપૂર્વક ડિલીટ થઈ ગયો છે!")
                st.rerun()
        else:
            st.info("કોઈ Paid રેકોર્ડ ઉપલબ્ધ નથી.")
        cursor.close()
        conn.close()

# --- 4. ADVANCE ENTRY ---
elif choice == "💸 Advance Entry (ઉપાડ)":
    st.markdown('<div class="section-title">💸 કર્મચારી ઉપાડ / એડવાન્સ એન્ટ્રી</div>', unsafe_allow_html=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM staff ORDER BY name ASC")
    staff_list = [r[0] for r in cursor.fetchall()]

    if not staff_list:
        st.warning("⚠️ કોઈ કર્મચારી ઉમેરેલ નથી!")
    else:
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            adv_staff = st.selectbox("કર્મચારી પસંદ કરો", staff_list)
            adv_amt = st.number_input("ઉપાડ રકમ (RS)", min_value=0.0, step=100.0)
        with col_a2:
            adv_date = st.date_input("તારીખ", datetime.date.today())
            adv_note = st.text_input("નોંધ (Note)")

        if st.button("💾 Save Advance Payment", type="primary", use_container_width=True):
            if adv_amt > 0:
                cursor.execute("INSERT INTO advance_payments (staff_name, date, amount, note) VALUES (?, ?, ?, ?)", (adv_staff, str(adv_date), adv_amt, adv_note))
                conn.commit()
                cursor.close()
                conn.close()
                st.success(f"✅ RS {adv_amt}/- નો ઉપાડ સફળતાપૂર્વક જમા થઈ ગયો!")
                st.rerun()
            else:
                st.error("⚠️ કૃપા કરીને સાચી રકમ નાખો!")

        st.write("---")
        st.markdown("### 📜 ઉપાડ રેકોર્ડ હિસ્ટ્રી")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, staff_name, date, amount, note FROM advance_payments ORDER BY id DESC")
        adv_rows = cursor.fetchall()
        if adv_rows:
            st.dataframe(adv_rows, use_container_width=True)
        cursor.close()
        conn.close()

# --- 5. DAILY EXPENSES ---
elif choice == "📝 Daily Expenses (દૈનિક ખર્ચ / બિલ)":
    st.markdown('<div class="section-title">📝 દૈનિક ખર્ચ એન્ટ્રી & બિલ અપલોડ</div>', unsafe_allow_html=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        exp_date = st.date_input("ખર્ચની તારીખ", datetime.date.today())
        exp_cat = st.selectbox("ખર્ચનો પ્રકાર (Category)", ["🏢 ઓફિસ ખર્ચ (Office)", "🚗 ગાડીનો ખર્ચ (Vehicle)", "📦 અધર ખર્ચ (Other)"])
        uploaded_file = st.file_uploader("📷 Upload Bill / Receipt Image (બિલ ફોટો)", type=["jpg", "jpeg", "png", "pdf"])
    with col_e2:
        exp_amt = st.number_input("ખર્ચ રકમ (RS)", min_value=0.0, step=50.0)
        exp_detail = st.text_input("ખર્ચની વિગત / નોંધ (Details)")

    if st.button("💾 Save Expense (ખર્ચ સેવ કરો)", type="primary", use_container_width=True):
        if exp_amt > 0:
            saved_filename = ""
            if uploaded_file is not None:
                file_ext = uploaded_file.name.split(".")[-1]
                saved_filename = f"bill_{int(datetime.datetime.now().timestamp())}.{file_ext}"
                file_path = os.path.join("uploaded_bills", saved_filename)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

            cursor.execute("INSERT INTO expenses (date, category, amount, details, bill_file) VALUES (?, ?, ?, ?, ?)", (str(exp_date), exp_cat, exp_amt, exp_detail, saved_filename))
            conn.commit()
            cursor.close()
            conn.close()
            st.success(f"✅ RS {exp_amt}/- નો '{exp_cat}' સફળતાપૂર્વક બિલ સાથે સેવ થઈ ગયો!")
            st.rerun()
        else:
            st.error("⚠️ કૃપા કરીને સાચી રકમ નાખો!")

    st.write("---")
    st.markdown("### 📊 ખર્ચ રિપોર્ટ & બિલ વ્યૂ")
    filter_date = st.date_input("જે તારીખનો હિસાબ જોવો હોય તે પસંદ કરો", datetime.date.today(), key="f_date")

    cursor.execute("SELECT id, category, amount, details, bill_file FROM expenses WHERE date=?", (str(filter_date),))
    e_rows = cursor.fetchall()

    if e_rows:
        tot_exp = sum(r[2] for r in e_rows)
        st.markdown(f"#### 💵 તારીખ {filter_date} નો કુલ ખર્ચ: **RS {tot_exp:,.2f}**")
        
        for r in e_rows:
            col_a, col_b, col_c, col_d = st.columns([2, 1.5, 3, 2])
            with col_a: st.write(f"📌 **{r[1]}**")
            with col_b: st.write(f"💰 **RS {r[2]:,.2f}**")
            with col_c: st.write(f"📝 {r[3]}")
            with col_d:
                if r[4]:
                    file_p = os.path.join("uploaded_bills", r[4])
                    if os.path.exists(file_p):
                        with open(file_p, "rb") as file_data:
                            st.download_button("📸 View/Download Bill", data=file_data, file_name=r[4], key=f"bill_{r[0]}")
                else:
                    st.write("No Bill")
    else:
        st.info(f"તારીખ {filter_date} માટે કોઈ ખર્ચ નોંધાયેલ નથી.")

    st.write("---")
    st.markdown("### 🗑️ ખોટી ખર્ચ એન્ટ્રી ડિલીટ કરો")
    cursor.execute("SELECT id, date, category, amount, details FROM expenses ORDER BY id DESC LIMIT 20")
    recent_exp = cursor.fetchall()

    if recent_exp:
        exp_dict = {f"ID: #{r[0]} | Date: {r[1]} | {r[2]} | RS {r[3]} ({r[4]})": r[0] for r in recent_exp}
        sel_del_exp = st.selectbox("ડિલીટ કરવા માટે એન્ટ્રી પસંદ કરો", list(exp_dict.keys()))
        if st.button("🗑️ Delete Selected Expense", type="secondary"):
            del_exp_id = exp_dict[sel_del_exp]
            cursor.execute("DELETE FROM expenses WHERE id=?", (del_exp_id,))
            conn.commit()
            cursor.close()
            conn.close()
            st.success("✅ ખર્ચ એન્ટ્રી ડિલીટ થઈ ગઈ!")
            st.rerun()
    cursor.close()
    conn.close()

# --- 6. MASTER REPORT ---
elif choice == "📊 Master Report (માસિક માસ્ટર રિપોર્ટ)":
    st.markdown('<div class="section-title">📊 આખા મહિનાનો માસ્ટર રિપોર્ટ (કુલ ખર્ચ + પગાર હિસાબ)</div>', unsafe_allow_html=True)
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        rep_month = st.number_input("મહિનો (1-12)", min_value=1, max_value=12, value=datetime.date.today().month, key="rm")
    with col_m2:
        rep_year = st.number_input("વર્ષ (Year)", min_value=2020, max_value=2030, value=datetime.date.today().year, key="ry")

    month_year_str = f"{int(rep_month):02d}-{int(rep_year)}"
    max_days = calendar.monthrange(int(rep_year), int(rep_month))[1]
    start_date = f"{rep_year}-{int(rep_month):02d}-01"
    end_date = f"{rep_year}-{int(rep_month):02d}-{max_days}"

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(net_salary) FROM salary_history WHERE month_year=?", (month_year_str,))
    tot_sal_row = cursor.fetchone()
    total_paid_salary = tot_sal_row[0] if tot_sal_row[0] else 0.0

    cursor.execute("SELECT SUM(amount) FROM expenses WHERE date BETWEEN ? AND ?", (start_date, end_date))
    tot_exp_row = cursor.fetchone()
    total_office_expenses = tot_exp_row[0] if tot_exp_row[0] else 0.0

    grand_total = total_paid_salary + total_office_expenses

    st.write("---")
    st.markdown("### 📈 માસિક કુલ ખર્ચ સમરી")
    
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.metric(label="👥 કુલ ચુકવેલ પગાર (Total Salary)", value=f"RS {total_paid_salary:,.2f}")
    with col_s2:
        st.metric(label="🏢 કુલ ઓફિસ ખર્ચ (Office Expenses)", value=f"RS {total_office_expenses:,.2f}")
    with col_s3:
        st.metric(label="💼 આખા મહિનાનો કુલ ખર્ચ (GRAND TOTAL)", value=f"RS {grand_total:,.2f}")

    cursor.execute("SELECT date, category, amount, details FROM expenses WHERE date BETWEEN ? AND ? ORDER BY date ASC", (start_date, end_date))
    exp_records = cursor.fetchall()

    cursor.execute("SELECT staff_name, payable_days, gross_salary, advance_deduction, net_salary, paid_date FROM salary_history WHERE month_year=?", (month_year_str,))
    sal_records = cursor.fetchall()
    cursor.close()
    conn.close()

    st.write("---")
    master_pdf_bytes = generate_master_report_pdf_bytes(month_year_str, total_paid_salary, total_office_expenses, grand_total, exp_records, sal_records)
    st.download_button(
        label="📥 Download Master Report PDF (પ્રિન્ટ / PDF)",
        data=master_pdf_bytes,
        file_name=f"Master_Report_{month_year_str}.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True
    )

    st.write("---")
    st.markdown("### 📅 તારીખ વાઈઝ દૈનિક ખર્ચ હિસાબ (Daily Expense Breakup)")
    if exp_records:
        st.dataframe(exp_records, use_container_width=True)
    else:
        st.info("આ મહિનામાં કોઈ દૈનિક ખર્ચ નોંધાયેલ નથી.")

    st.write("---")
    st.markdown("### 💰 ચૂકવાયેલા પગારનું માસિક સ્ટેટમેન્ટ (Paid Salary List)")
    if sal_records:
        st.dataframe(sal_records, use_container_width=True)
    else:
        st.info("આ મહિનામાં કોઈ પગાર ચૂકવાયેલ નથી.")

# --- 7. MANAGE STAFF ---
elif choice == "👤 Manage Staff (કર્મચારી)":
    st.markdown('<div class="section-title">👤 કર્મચારી મેનેજમેન્ટ (નવો ઉમેરો, એડિટ કરો અને લિસ્ટ)</div>', unsafe_allow_html=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()

    staff_tab1, staff_tab2 = st.tabs(["➕ નવો કર્મચારી ઉમેરો", "✏️ કર્મચારી વિગત એડિટ / સુધારો કરો"])

    with staff_tab1:
        col1, col2 = st.columns(2)
        with col1:
            s_name = st.text_input("કર્મચારીનું નામ", key="add_name")
            s_rate = st.number_input("રોજ / Daily Rate (RS)", min_value=0.0, step=50.0, key="add_rate")
            s_work_type = st.selectbox("કામનો પ્રકાર (Work Type)", ["Full Time", "Part Time"], key="add_wtype")
            s_address = st.text_area("સરનામું (Address)", height=80, key="add_addr")
        with col2:
            s_desig = st.text_input("હોદ્દો (Designation)", key="add_desig")
            s_mob = st.text_input("મોબાઈલ નંબર", key="add_mob")
            s_shift = st.text_input("Shift Timing (ઉદા. 09:00 AM to 06:00 PM)", key="add_shift")

        if st.button("💾 Save Staff", type="primary", use_container_width=True):
            if s_name and s_rate > 0:
                try:
                    cursor.execute("""
                        INSERT INTO staff (name, designation, daily_rate, mobile, address, work_type, shift_timing) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (s_name, s_desig, s_rate, s_mob, s_address, s_work_type, s_shift))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success(f"✅ કર્મચારી '{s_name}' સફળતાપૂર્વક સેવ થઈ ગયો!")
                    st.rerun()
                except Exception:
                    cursor.close()
                    conn.close()
                    st.error("⚠️ આ નામનો કર્મચારી પહેલેથી જ ડેટાબેઝમાં છે!")
            else:
                cursor.close()
                conn.close()
                st.error("⚠️ કૃપા કરીને નામ અને રોજ ભરો!")

    with staff_tab2:
        cursor.execute("SELECT id, name, designation, work_type, shift_timing, daily_rate, mobile, address FROM staff ORDER BY name ASC")
        staff_rows_all = cursor.fetchall()

        if staff_rows_all:
            staff_names_list = [r[1] for r in staff_rows_all]
            edit_staff_choice = st.selectbox("એડિટ કરવા માટે કર્મચારી પસંદ કરો", staff_names_list, key="edit_sel_staff")

            cursor.execute("SELECT id, name, designation, daily_rate, mobile, address, work_type, shift_timing FROM staff WHERE name=?", (edit_staff_choice,))
            curr_data = cursor.fetchone()

            if curr_data:
                s_id, c_name, c_desig, c_rate, c_mob, c_addr, c_wtype, c_shift = curr_data
                
                with st.form("edit_staff_form"):
                    st.markdown(f"**કર્મચારી ID: #{s_id}**")
                    e_name = st.text_input("કર્મચારીનું નામ", value=c_name)
                    e_rate = st.number_input("રોજ / Daily Rate (RS)", min_value=0.0, value=float(c_rate) if c_rate else 0.0, step=50.0)
                    e_wtype = st.selectbox("કામનો પ્રકાર (Work Type)", ["Full Time", "Part Time"], index=0 if c_wtype != "Part Time" else 1)
                    e_addr = st.text_area("સરનામું (Address)", value=c_addr if c_addr else "", height=80)
                    
                    e_desig = st.text_input("હોદ્દો (Designation)", value=c_desig if c_desig else "")
                    e_mob = st.text_input("મોબાઈલ નંબર", value=c_mob if c_mob else "")
                    e_shift = st.text_input("Shift Timing", value=c_shift if c_shift else "")

                    submit_update = st.form_submit_button("🔄 Update Staff Details (વિગત અપડેટ કરો)", type="primary")

                    if submit_update:
                        cursor.execute("""
                            UPDATE staff SET name=?, designation=?, daily_rate=?, mobile=?, address=?, work_type=?, shift_timing=? WHERE id=?
                        """, (e_name, e_desig, e_rate, e_mob, e_addr, e_wtype, e_shift, s_id))
                        conn.commit()
                        st.success(f"✅ કર્મચારી '{e_name}' ની વિગતો સફળતાપૂર્વક અપડેટ થઈ ગઈ!")
                        st.rerun()
        else:
            st.info("એડિટ કરવા માટે કોઈ કર્મચારી ઉપલબ્ધ નથી.")

    st.write("---")
    st.markdown('<div class="section-title">🗑️ કર્મચારીને લિસ્ટમાંથી દૂર / ડિલીટ કરો</div>', unsafe_allow_html=True)
    
    cursor.execute("SELECT name FROM staff ORDER BY name ASC")
    all_staff_to_del = [r[0] for r in cursor.fetchall()]

    if all_staff_to_del:
        del_staff_name = st.selectbox("છૂટા થયેલા / ડિલીટ કરવા માટે કર્મચારી પસંદ કરો", all_staff_to_del, key="del_sel_staff")
        if st.button("🗑️ Delete Staff (કર્મચારી કાઢી નાખો)", type="secondary"):
            cursor.execute("DELETE FROM staff WHERE name=?", (del_staff_name,))
            conn.commit()
            st.success(f"✅ કર્મચારી '{del_staff_name}' સફળતાપૂર્વક ડિલીટ થઈ ગયો છે!")
            st.rerun()
    else:
        st.info("ડિલીટ કરવા માટે કોઈ કર્મચારી ઉપલબ્ધ નથી.")

    st.write("---")
    st.markdown("### 📋 હાલના કર્મચારીઓનું લિસ્ટ (ક્રમ અને સંપૂર્ણ વિગત)")
    cursor.execute("SELECT id, name, designation, work_type, shift_timing, daily_rate, mobile, address FROM staff ORDER BY id ASC")
    staff_rows = cursor.fetchall()
    if staff_rows:
        st.dataframe(staff_rows, use_container_width=True)
    
    cursor.close()
    conn.close()

# --- 8. BACKUP & RESTORE ---
elif choice == "💾 Backup & Restore (બેકઅપ & રીસ્ટોર)":
    st.markdown('<div class="section-title">💾 ડેટાબેઝ સુરક્ષા & બેકઅપ સિસ્ટમ (Backup & Restore)</div>', unsafe_allow_html=True)
    
    b_tab1, b_tab2 = st.tabs(["📥 ડેટાબેઝ બેકઅપ ડાઉનલોડ કરો (Export)", "📤 જૂનું બેકઅપ સોફ્ટવેરમાં ચડાવો (Restore)"])
    
    conn = get_db_connection()
    cursor = conn.cursor()

    with b_tab1:
        st.write("💡 તમારા લેપટોપમાં સોફ્ટવેરનો આખો ડેટા સુરક્ષિત રાખવા માટે બેકઅપ ફાઈલ ડાઉનલોડ કરી લો.")
        
        if st.button("📦 આખા ડેટાનો બેકઅપ તૈયાર કરો", type="primary"):
            tables = ["staff", "attendance", "advance_payments", "salary_history", "expenses"]
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                for t in tables:
                    df = pd.read_sql_query(f"SELECT * FROM {t}", conn)
                    df.to_excel(writer, sheet_name=t, index=False)
            
            output.seek(0)
            
            st.download_button(
                label="⬇️ Excel Backup ફાઈલ ડાઉનલોડ કરો (.xlsx)",
                data=output.getvalue(),
                file_name=f"Payroll_Backup_{datetime.date.today().strftime('%Y_%m_%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.success("✅ તમારો બેકઅપ સફળતાપૂર્વક તૈયાર થઈ ગયો છે!")

    with b_tab2:
        st.write("⚠️ જો ક્યારેય ડેટાબેઝમાં કોઈ સમસ્યા થાય અથવા નવું સર્વર ચાલુ કરો, તો અહીંથી તમારો અગાઉ ડાઉનલોડ કરેલો Excel બેકઅપ અપલોડ કરી શકો છો.")
        
        uploaded_backup = st.file_uploader("📂 Choose Backup Excel File (.xlsx)", type=["xlsx"])
        
        if uploaded_backup is not None:
            if st.button("🚀 ડેટાબેઝમાં બેકઅપ રીસ્ટોર કરો", type="primary"):
                try:
                    excel_data = pd.ExcelFile(uploaded_backup)
                    
                    if "staff" in excel_data.sheet_names:
                        df_staff = pd.read_excel(excel_data, "staff")
                        for _, row in df_staff.iterrows():
                            cursor.execute("""
                                INSERT OR REPLACE INTO staff (name, designation, daily_rate, mobile, address, work_type, shift_timing)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (row['name'], row['designation'], row['daily_rate'], row['mobile'], row['address'], row['work_type'], row['shift_timing']))

                    if "attendance" in excel_data.sheet_names:
                        df_att = pd.read_excel(excel_data, "attendance")
                        for _, row in df_att.iterrows():
                            cursor.execute("""
                                INSERT OR REPLACE INTO attendance (staff_name, date, status, overtime_amt)
                                VALUES (?, ?, ?, ?)
                            """, (row['staff_name'], str(row['date']), row['status'], row['overtime_amt']))

                    if "advance_payments" in excel_data.sheet_names:
                        df_adv = pd.read_excel(excel_data, "advance_payments")
                        for _, row in df_adv.iterrows():
                            cursor.execute("""
                                INSERT INTO advance_payments (staff_name, date, amount, note)
                                VALUES (?, ?, ?, ?)
                            """, (row['staff_name'], str(row['date']), row['amount'], row['note']))

                    if "salary_history" in excel_data.sheet_names:
                        df_sal = pd.read_excel(excel_data, "salary_history")
                        for _, row in df_sal.iterrows():
                            cursor.execute("""
                                INSERT OR IGNORE INTO salary_history (staff_name, month_year, payable_days, gross_salary, advance_deduction, net_salary, paid_date)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (row['staff_name'], str(row['month_year']), row['payable_days'], row['gross_salary'], row['advance_deduction'], row['net_salary'], str(row['paid_date'])))

                    if "expenses" in excel_data.sheet_names:
                        df_exp = pd.read_excel(excel_data, "expenses")
                        for _, row in df_exp.iterrows():
                            cursor.execute("""
                                INSERT INTO expenses (date, category, amount, details, bill_file)
                                VALUES (?, ?, ?, ?, ?)
                            """, (str(row['date']), row['category'], row['amount'], row['details'], row['bill_file']))

                    conn.commit()
                    st.success("🎉 તમારો આખો બેકઅપ સફળતાપૂર્વક રીસ્ટોર (અપલોડ) થઈ ગયો છે!")
                    st.rerun()
                except Exception as e:
                    st.error(f"⚠️ બેકઅપ રીસ્ટોર કરવામાં ભૂલ થઈ: {e}")

    cursor.close()
    conn.close()

