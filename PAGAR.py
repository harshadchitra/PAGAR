import streamlit as st
import datetime
import calendar
import io
import os
import json
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

# Local Storage Folder for JSON Data Files
DATA_DIR = "cloud_data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

if not os.path.exists("uploaded_bills"):
    os.makedirs("uploaded_bills")

# Helper functions to load/save JSON tables locally with Exception Safety
def load_table(table_name, default_value):
    file_path = os.path.join(DATA_DIR, f"{table_name}.json")
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                if not content.strip():
                    return default_value
                return json.loads(content)
        except Exception:
            return default_value
    return default_value

def save_table(table_name, data):
    file_path = os.path.join(DATA_DIR, f"{table_name}.json")
    try:
        temp_path = f"{file_path}.tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        if os.path.exists(file_path):
            os.remove(file_path)
        os.rename(temp_path, file_path)
    except Exception as e:
        st.error(f"Error saving data for {table_name}: {e}")

# Initialize JSON Datasets Safely
def initialize_datasets():
    defaults = {
        "staff": [],
        "attendance": {},
        "advance_payments": [],
        "salary_history": [],
        "expenses": []
    }
    for tbl, def_val in defaults.items():
        file_path = os.path.join(DATA_DIR, f"{tbl}.json")
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            save_table(tbl, def_val)

initialize_datasets()

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
        exp_table_data.append([Paragraph(str(r['date']), normal_style), Paragraph(str(r['category']), normal_style), Paragraph(f"RS {r['amount']:,.2f}", normal_style), Paragraph(str(r['details']), normal_style)])
    
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
        sal_table_data.append([Paragraph(str(s['staff_name']), normal_style), Paragraph(str(s['payable_days']), normal_style), Paragraph(f"RS {s['gross_salary']:,.2f}", normal_style), Paragraph(f"RS {s['advance_deduction']:,.2f}", normal_style), Paragraph(f"RS {s['net_salary']:,.2f}", normal_style)])

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
    <p>Staff Attendance, Shift, Overtime, Daily Expense & Monthly Master Analytics (Cloud File Mode)</p>
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
    st.markdown('<div class="section-title">📅 રોજની હાજરી પૂરો & ઓવર ટાઈમ (તારીખ ફિલ્ટર સાથે)</div>', unsafe_allow_html=True)
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        att_date = st.date_input("તારીખ પસંદ કરો (Running Date)", datetime.date.today())

    staff_list = load_table("staff", [])
    attendance_data = load_table("attendance", {})

    if not staff_list:
        st.warning("⚠️ કોઈ કર્મચારી ઉમેરેલ નથી! પહેલા 'Manage Staff' માં જઈને ઉમેરો.")
    else:
        st.write("")
        att_input = {}
        date_str = str(att_date)
        for s in staff_list:
            staff_name = s['name']
            w_type = s.get('work_type', 'Full Time')
            shift = s.get('shift_timing', '')

            key_str = f"{staff_name}_{date_str}"
            current_att = attendance_data.get(key_str, {"status": "Present", "overtime_amt": 0.0})
            
            default_idx = 0
            if current_att["status"] == "Absent": default_idx = 1
            elif current_att["status"] == "Half": default_idx = 2
            def_ot = current_att.get("overtime_amt", 0.0)

            col1, col2, col3 = st.columns([2, 1.5, 1.5])
            with col1:
                shift_info = f" ({w_type} | {shift})" if shift else ""
                st.markdown(f"👤 **{staff_name}** <small style='color:#94a3b8'>{shift_info}</small>", unsafe_allow_html=True)
            with col2:
                status = st.selectbox(f"Status for {staff_name}", ["Present", "Absent", "Half"], index=default_idx, key=f"att_{staff_name}", label_visibility="collapsed")
            with col3:
                ot_val = st.number_input(f"OT (RS) for {staff_name}", min_value=0.0, value=float(def_ot), step=50.0, key=f"ot_{staff_name}", label_visibility="collapsed")
                att_input[staff_name] = {"status": status, "overtime_amt": ot_val}

        st.write("---")
        if st.button("💾 Save Attendance & Overtime", type="primary", use_container_width=True):
            for staff_name, vals in att_input.items():
                key_str = f"{staff_name}_{date_str}"
                attendance_data[key_str] = vals
            save_table("attendance", attendance_data)
            st.success(f"✅ તારીખ {att_date} ની હાજરી અને ઓવર ટાઈમ સફળતાપૂર્વક સેવ થઈ ગયા!")
            st.rerun()

# --- 2. MONTHLY CALENDAR VIEW ---
elif choice == "📊 Monthly Calendar View (કેલેન્ડર)":
    st.markdown('<div class="section-title">📊 આખા મહિનાનું હાજરી કેલેન્ડર</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        month = st.number_input("મહિનો (1-12)", min_value=1, max_value=12, value=datetime.date.today().month)
    with col2:
        year = st.number_input("વર્ષ (Year)", min_value=2020, max_value=2030, value=datetime.date.today().year)

    max_days = calendar.monthrange(int(year), int(month))[1]
    staff_list = load_table("staff", [])
    attendance_data = load_table("attendance", {})
    staff_names = [s['name'] for s in staff_list]

    if staff_names:
        table_rows = []
        for staff in staff_names:
            row = {"Staff Name": staff}
            p, a, h = 0, 0, 0
            for d in range(1, max_days + 1):
                date_str = f"{int(year)}-{int(month):02d}-{d:02d}"
                key_str = f"{staff}_{date_str}"
                rec = attendance_data.get(key_str)
                val = "-"
                if rec:
                    val = rec["status"][0].upper()
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
    else:
        st.warning("⚠️ કોઈ કર્મચારી ઉપલબ્ધ નથી.")

# --- 3. SALARY & PAID STATUS LIST ---
elif choice == "💰 Salary & Digital Slip (પગાર & લિસ્ટ)":
    st.markdown('<div class="section-title">💰 માસિક પગાર ગણતરી, સ્લિપ & પેઇડ/પેન્ડિંગ લિસ્ટ</div>', unsafe_allow_html=True)
    
    staff_list = load_table("staff", [])
    staff_names = [s['name'] for s in staff_list]

    if not staff_names:
        st.warning("⚠️ કોઈ કર્મચારી ઉમેરેલ નથી!")
    else:
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            sel_month = st.number_input("મહિનો પસંદ કરો", min_value=1, max_value=12, value=datetime.date.today().month, key="s_m")
        with col_m2:
            sel_year = st.number_input("વર્ષ પસંદ કરો", min_value=2020, max_value=2030, value=datetime.date.today().year, key="s_y")

        month_year_str = f"{int(sel_month):02d}-{int(sel_year)}"
        salary_history = load_table("salary_history", [])
        paid_records = {item['staff_name']: item for item in salary_history if item['month_year'] == month_year_str}

        st.write("---")
        st.markdown(f"### 📋 કર્મચારીઓનું માસિક લિસ્ટ ({month_year_str})")

        for staff in staff_names:
            st.write(f"👤 **{staff}** - {'🟢 PAID' if staff in paid_records else '🟠 PENDING'}")

# --- 4. ADVANCE ENTRY ---
elif choice == "💸 Advance Entry (ઉપાડ)":
    st.markdown('<div class="section-title">💸 કર્મચારી ઉપાડ (Advance) એન્ટ્રી</div>', unsafe_allow_html=True)
    staff_list = load_table("staff", [])
    staff_names = [s['name'] for s in staff_list]
    if not staff_names:
        st.warning("⚠️ પહેલા કર્મચારી ઉમેરો.")
    else:
        with st.form("adv_form"):
            staff_sel = st.selectbox("કર્મચારી પસંદ કરો", staff_names)
            adv_date = st.date_input("તારીખ", datetime.date.today())
            adv_amt = st.number_input("ઉપાડ રકમ (RS)", min_value=0.0, step=100.0)
            adv_notes = st.text_input("નોંધ (Remarks)")
            submitted = st.form_submit_button("Save Advance Entry")
            if submitted:
                adv_records = load_table("advance_payments", [])
                adv_records.append({"staff_name": staff_sel, "date": str(adv_date), "amount": adv_amt, "notes": adv_notes})
                save_table("advance_payments", adv_records)
                st.success("✅ ઉપાડની એન્ટ્રી સેવ થઈ ગઈ!")
                st.rerun()

# --- 5. DAILY EXPENSES ---
elif choice == "📝 Daily Expenses (દૈનિક ખર્ચ / બિલ)":
    st.markdown('<div class="section-title">📝 દૈનિક ખર્ચ અને બિલ અપલોડ</div>', unsafe_allow_html=True)
    with st.form("exp_form"):
        e_date = st.date_input("ખર્ચની તારીખ", datetime.date.today())
        e_cat = st.selectbox("કેટેગરી", ["Office Supplies", "Fuel", "Maintenance", "Tea/Refreshment", "Other"])
        e_amt = st.number_input("રકમ (RS)", min_value=0.0, step=50.0)
        e_det = st.text_input("વિગત (Details)")
        submitted = st.form_submit_button("Save Expense")
        if submitted:
            expenses = load_table("expenses", [])
            expenses.append({"date": str(e_date), "category": e_cat, "amount": e_amt, "details": e_det})
            save_table("expenses", expenses)
            st.success("✅ ખર્ચ સફળતાપૂર્વક સેવ થઈ ગયો!")
            st.rerun()

# --- 6. MASTER REPORT ---
elif choice == "📊 Master Report (માસિક માસ્ટર રિપોર્ટ)":
    st.markdown('<div class="section-title">📊 માસિક માસ્ટર રિપોર્ટ & એનાલિટિક્સ</div>', unsafe_allow_html=True)
    st.info("સંપૂર્ણ માસિક અહેવાલ અહીંથી જોઈ અને પીડીએફ ડાઉનલોડ કરી શકો છો.")

# --- 7. MANAGE STAFF ---
elif choice == "👤 Manage Staff (કર્મચારી)":
    st.markdown('<div class="section-title">👤 કર્મચારીઓનું સંચાલન (Manage Staff)</div>', unsafe_allow_html=True)
    
    with st.form("staff_form"):
        s_name = st.text_input("કર્મચારીનું નામ (Staff Name)")
        s_rate = st.number_input("દૈનિક પગાર (Daily Rate RS)", min_value=0.0, step=50.0)
        s_type = st.selectbox("નોકરીનો પ્રકાર", ["Full Time", "Part Time"])
        s_shift = st.text_input("શિફ્ટ ટાઈમિંગ (દા.ત. 9 AM - 6 PM)")
        submitted = st.form_submit_button("Add Staff")
        
        if submitted and s_name:
            staff_list = load_table("staff", [])
            staff_list.append({"name": s_name, "daily_rate": s_rate, "work_type": s_type, "shift_timing": s_shift})
            save_table("staff", data=staff_list)
            st.success(f"✅ કર્મચારી '{s_name}' સફળતાપૂર્વક ઉમેરાઈ ગયા!")
            st.rerun()

    st.write("---")
    st.subheader("મૌજૂદ કર્મચારીઓની યાદી:")
    staff_list = load_table("staff", [])
    if staff_list:
        df_staff = pd.DataFrame(staff_list)
        st.dataframe(df_staff, use_container_width=True)
    else:
        st.info("કોઈ કર્મચારી ઉપલબ્ધ નથી.")

# --- 8. BACKUP & RESTORE ---
elif choice == "💾 Backup & Restore (બેકઅપ & રીસ્ટોર)":
    st.markdown('<div class="section-title">💾 બેકઅપ અને ડેટા સુરક્ષા (Backup & Restore)</div>', unsafe_allow_html=True)
    
    st.write("### 📥 1. ડેટા બેકઅપ ડાઉનલોડ કરો")
    all_data = {
        "staff": load_table("staff", []),
        "attendance": load_table("attendance", {}),
        "advance_payments": load_table("advance_payments", []),
        "salary_history": load_table("salary_history", []),
        "expenses": load_table("expenses", [])
    }
    json_str = json.dumps(all_data, ensure_ascii=False, indent=4)
    st.download_button(
        label="📥 Download Complete Backup (JSON)",
        data=json_str,
        file_name=f"payroll_backup_{datetime.date.today()}.json",
        mime="application/json",
        type="primary"
    )
    
    st.markdown("---")
    st.write("### 📤 2. જૂનો બેકઅપ ડેટા રીસ્ટોર (Restore) કરો")
    uploaded_backup = st.file_uploader("તમારી બેકઅપ JSON ફાઇલ અહીં અપલોડ કરો:", type=["json"], key="restore_file")
    
    if uploaded_backup is not None:
        if st.button("🔄 Restore Data Now", type="primary"):
            try:
                backup_content = json.load(uploaded_backup)
                for tbl in ["staff", "attendance", "advance_payments", "salary_history", "expenses"]:
                    if tbl in backup_content:
                        save_table(tbl, backup_content[tbl])
                st.success("✅ બેકઅપ સફળતાપૂર્વક રીસ્ટોર થઈ ગયો છે! (Data Restored Successfully)")
                st.rerun()
            except Exception as e:
                st.error(f"❌ બેકઅપ ફાઇલ વાંચવામાં ભૂલ છે: {e}")

