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

# Helper functions to load/save JSON tables locally/cloud sync
def load_table(table_name, default_value):
    file_path = os.path.join(DATA_DIR, f"{table_name}.json")
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default_value
    return default_value

def save_table(table_name, data):
    file_path = os.path.join(DATA_DIR, f"{table_name}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Initialize JSON Datasets
if not os.path.exists(os.path.join(DATA_DIR, "staff.json")):
    save_table("staff", [])
if not os.path.exists(os.path.join(DATA_DIR, "attendance.json")):
    save_table("attendance", {})
if not os.path.exists(os.path.join(DATA_DIR, "advance_payments.json")):
    save_table("advance_payments", [])
if not os.path.exists(os.path.join(DATA_DIR, "salary_history.json")):
    save_table("salary_history", [])
if not os.path.exists(os.path.join(DATA_DIR, "expenses.json")):
    save_table("expenses", [])

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
    st.markdown('<div class="section-title">📅 રોજની હાજરી પૂરો & ઓવર ટાઈમ</div>', unsafe_allow_html=True)
    
    col_d1, col_d2 = st.columns([1, 2])
    with col_d1:
        att_date = st.date_input("તારીખ પસંદ કરો", datetime.date.today())

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

        h_col1, h_col2, h_col3, h_col4, h_col5 = st.columns([2, 2.5, 1.5, 1, 1.5])
        with h_col1: st.markdown("**Staff Name**")
        with h_col2: st.markdown("**Status**")
        with h_col3: st.markdown("**Net Salary**")
        with h_col4: st.markdown("**Record ID**")
        with h_col5: st.markdown("**Print Slip**")
        st.write("---")

        for staff in staff_names:
            col1, col2, col3, col4, col5 = st.columns([2, 2.5, 1.5, 1, 1.5])
            with col1: st.write(f"👤 **{staff}**")
            with col2:
                if staff in paid_records:
                    st.markdown("🟢 **PAID (ચૂકવાઈ ગયો)**")
                else:
                    st.markdown("🟠 **PENDING (બાકી છે)**")
            with col3:
                if staff in paid_records:
                    st.write(f"RS {paid_records[staff]['net_salary']:,.2f}")
                else:
                    st.write("---")
            with col4:
                if staff in paid_records:
                    st.write(f"#{paid_records[staff].get('id', 1)}")
                else:
                    st.write("---")
            with col5:
                if staff in paid_records:
                    d_rate = next((s['daily_rate'] for s in staff_list if s['name'] == staff), 0.0)
                    max_days = calendar.monthrange(int(sel_year), int(sel_month))[1]
                    
                    att_data = load_table("attendance", {})
                    present_count, half_count, absent_count, tot_ot = 0, 0, 0, 0.0
                    for d in range(1, max_days + 1):
                        date_str = f"{int(sel_year)}-{int(sel_month):02d}-{d:02d}"
                        rec = att_data.get(f"{staff}_{date_str}")
                        if rec:
                            if rec["status"] == "Present": present_count += 1
                            elif rec["status"] == "Half": half_count += 1
                            elif rec["status"] == "Absent": absent_count += 1
                            tot_ot += rec.get("overtime_amt", 0.0)

                    pdf_bytes = generate_salary_slip_pdf_bytes(
                        staff_name=staff,
                        month_year=month_year_str,
                        total_days=max_days,
                        present_days=present_count,
                        half_days=half_count,
                        absent_days=absent_count,
                        daily_rate=d_rate,
                        gross_salary=paid_records[staff]['gross_salary'],
                        advance_deduction=paid_records[staff]['advance_deduction'],
                        net_salary=paid_records[staff]['net_salary'],
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
        
        select_options = ["🌐 All Staff (બધા કર્મચારીઓ એકસાથે)"] + staff_names
        sal_staff_choice = st.selectbox("જેનો પગાર બાકી છે તે કર્મચારી પસંદ કરો", select_options)

        if st.button("🧮 Calculate & Generate Salary Slip", type="primary", use_container_width=True):
            max_days = calendar.monthrange(int(sel_year), int(sel_month))[1]
            paid_date_str = datetime.date.today().strftime("%Y-%m-%d")
            att_data = load_table("attendance", {})
            adv_data = load_table("advance_payments", [])

            def process_staff_salary(s_item):
                d_rate = next((s['daily_rate'] for s in staff_list if s['name'] == s_item), 0.0)
                present_count, half_count, tot_ot = 0, 0, 0.0
                for d in range(1, max_days + 1):
                    date_str = f"{int(sel_year)}-{int(sel_month):02d}-{d:02d}"
                    rec = att_data.get(f"{s_item}_{date_str}")
                    if rec:
                        if rec["status"] == "Present": present_count += 1
                        elif rec["status"] == "Half": half_count += 1
                        tot_ot += rec.get("overtime_amt", 0.0)

                # Calculate advances in this month
                adv_amt = 0.0
                for adv in adv_data:
                    if adv['staff_name'] == s_item:
                        a_date = adv['date']
                        if a_date.startswith(f"{int(sel_year)}-{int(sel_month):02d}"):
                            adv_amt += adv['amount']

                payable_days = present_count + (half_count * 0.5)
                gross_salary = (payable_days * d_rate) + tot_ot
                net_salary = max(0.0, gross_salary - adv_amt)

                # Check if already exists
                exists = False
                for item in salary_history:
                    if item['staff_name'] == s_item and item['month_year'] == month_year_str:
                        exists = True
                        break
                
                if not exists:
                    new_id = len(salary_history) + 1
                    salary_history.append({
                        "id": new_id,
                        "staff_name": s_item,
                        "month_year": month_year_str,
                        "payable_days": payable_days,
                        "gross_salary": gross_salary,
                        "advance_deduction": adv_amt,
                        "net_salary": net_salary,
                        "paid_date": paid_date_str
                    })
                    return True
                return False

            if sal_staff_choice == "🌐 All Staff (બધા કર્મચારીઓ એકસાથે)":
                calc_count = 0
                for s_item in staff_names:
                    if s_item not in paid_records:
                        if process_staff_salary(s_item):
                            calc_count += 1
                save_table("salary_history", salary_history)
                if calc_count > 0:
                    st.success(f"✅ કુલ {calc_count} કર્મચારીઓનો પગાર સફળતાપૂર્વક કેલ્ક્યુલેટ થઈ ગયો!")
                    st.rerun()
                else:
                    st.info("બધા કર્મચારીઓનો પગાર પહેલેથી જ ચૂકવાઈ ગયેલ છે!")
            else:
                if sal_staff_choice in paid_records:
                    st.warning(f"⚠️ કર્મચારી '{sal_staff_choice}' નો પગાર પહેલેથી ચૂકવાઈ ગયેલ છે!")
                else:
                    process_staff_salary(sal_staff_choice)
                    save_table("salary_history", salary_history)
                    st.success(f"✅ '{sal_staff_choice}' નો પગાર જમા થઈ ગયો!")
                    st.rerun()

        st.write("---")
        st.markdown('<div class="section-title">🗑️ પગાર રેકોર્ડ ડિલીટ કરો</div>', unsafe_allow_html=True)
        if salary_history:
            hist_options = {f"ID: #{r.get('id', 1)} | Staff: {r['staff_name']} | Month: {r['month_year']} | Net: RS {r['net_salary']}": r for r in salary_history}
            selected_hist_label = st.selectbox("ડિલીટ કરવા માટે રેકોર્ડ પસંદ કરો", list(hist_options.keys()))
            
            if st.button("🗑️ Delete Selected Salary Record", type="secondary"):
                target = hist_options[selected_hist_label]
                salary_history = [item for item in salary_history if not (item['staff_name'] == target['staff_name'] and item['month_year'] == target['month_year'])]
                save_table("salary_history", salary_history)
                st.success("✅ પગાર રેકોર્ડ સફળતાપૂર્વક ડિલીટ થઈ ગયો!")
                st.rerun()
        else:
            st.info("કોઈ Paid રેકોર્ડ ઉપલબ્ધ નથી.")

# --- 4. ADVANCE ENTRY ---
elif choice == "💸 Advance Entry (ઉપાડ)":
    st.markdown('<div class="section-title">💸 કર્મચારી ઉપાડ / એડવાન્સ એન્ટ્રી</div>', unsafe_allow_html=True)
    
    staff_list = load_table("staff", [])
    staff_names = [s['name'] for s in staff_list]

    if not staff_names:
        st.warning("⚠️ કોઈ કર્મચારી ઉમેરેલ નથી!")
    else:
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            adv_staff = st.selectbox("કર્મચારી પસંદ કરો", staff_names)
            adv_amt = st.number_input("ઉપાડ રકમ (RS)", min_value=0.0, step=100.0)
        with col_a2:
            adv_date = st.date_input("તારીખ", datetime.date.today())
            adv_note = st.text_input("નોંધ (Note)")

        if st.button("💾 Save Advance Payment", type="primary", use_container_width=True):
            if adv_amt > 0:
                adv_data = load_table("advance_payments", [])
                new_id = len(adv_data) + 1
                adv_data.append({
                    "id": new_id,
                    "staff_name": adv_staff,
                    "date": str(adv_date),
                    "amount": adv_amt,
                    "note": adv_note
                })
                save_table("advance_payments", adv_data)
                st.success(f"✅ RS {adv_amt}/- નો ઉપાડ સફળતાપૂર્વક જમા થઈ ગયો!")
                st.rerun()
            else:
                st.error("⚠️ સાચી રકમ નાખો!")

        st.write("---")
        st.markdown("### 📜 ઉપાડ રેકોર્ડ હિસ્ટ્રી")
        adv_data = load_table("advance_payments", [])
        if adv_data:
            st.dataframe(adv_data, use_container_width=True)
        else:
            st.info("કોઈ ઉપાડ રેકોર્ડ નથી.")

# --- 5. DAILY EXPENSES ---
elif choice == "📝 Daily Expenses (દૈનિક ખર્ચ / બિલ)":
    st.markdown('<div class="section-title">📝 દૈનિક ખર્ચ એન્ટ્રી & બિલ અપલોડ</div>', unsafe_allow_html=True)
    
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

            expenses_data = load_table("expenses", [])
            new_id = len(expenses_data) + 1
            expenses_data.append({
                "id": new_id,
                "date": str(exp_date),
                "category": exp_cat,
                "amount": exp_amt,
                "details": exp_detail,
                "bill_file": saved_filename
            })
            save_table("expenses", expenses_data)
            st.success(f"✅ RS {exp_amt}/- નો ખર્ચ સેવ થઈ ગયો!")
            st.rerun()
        else:
            st.error("⚠️ સાચી રકમ નાખો!")

    st.write("---")
    st.markdown("### 📊 ખર્ચ રિપોર્ટ & બિલ વ્યૂ")
    filter_date = st.date_input("જે તારીખનો હિસાબ જોવો હોય તે પસંદ કરો", datetime.date.today(), key="f_date")
    expenses_data = load_table("expenses", [])
    e_rows = [e for e in expenses_data if e['date'] == str(filter_date)]

    if e_rows:
        tot_exp = sum(r['amount'] for r in e_rows)
        st.markdown(f"#### 💵 તારીખ {filter_date} નો કુલ ખર્ચ: **RS {tot_exp:,.2f}**")
        
        for r in e_rows:
            col_a, col_b, col_c, col_d = st.columns([2, 1.5, 3, 2])
            with col_a: st.write(f"📌 **{r['category']}**")
            with col_b: st.write(f"💰 **RS {r['amount']:,.2f}**")
            with col_c: st.write(f"📝 {r['details']}")
            with col_d:
                if r['bill_file']:
                    file_p = os.path.join("uploaded_bills", r['bill_file'])
                    if os.path.exists(file_p):
                        with open(file_p, "rb") as file_data:
                            st.download_button("📸 View/Download Bill", data=file_data, file_name=r['bill_file'], key=f"bill_{r['id']}")
                else:
                    st.write("No Bill")
    else:
        st.info(f"તારીખ {filter_date} માટે કોઈ ખર્ચ નોંધાયેલ નથી.")

# --- 6. MASTER REPORT ---
elif choice == "📊 Master Report (માસિક માસ્ટર રિપોર્ટ)":
    st.markdown('<div class="section-title">📊 આખા મહિનાનો માસ્ટર રિપોર્ટ (કુલ ખર્ચ + પગાર હિસાબ)</div>', unsafe_allow_html=True)
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        rep_month = st.number_input("મહિનો (1-12)", min_value=1, max_value=12, value=datetime.date.today().month, key="rm")
    with col_m2:
        rep_year = st.number_input("વર્ષ (Year)", min_value=2020, max_value=2030, value=datetime.date.today().year, key="ry")

    month_year_str = f"{int(rep_month):02d}-{int(rep_year)}"
    start_date = f"{int(rep_year)}-{int(rep_month):02d}-01"
    max_days = calendar.monthrange(int(rep_year), int(rep_month))[1]
    end_date = f"{int(rep_year)}-{int(rep_month):02d}-{max_days}"

    salary_history = load_table("salary_history", [])
    expenses_data = load_table("expenses", [])

    sal_records = [s for s in salary_history if s['month_year'] == month_year_str]
    total_paid_salary = sum(s['net_salary'] for s in sal_records)

    exp_records = [e for e in expenses_data if start_date <= e['date'] <= end_date]
    total_office_expenses = sum(e['amount'] for e in exp_records)

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
    
    staff_list = load_table("staff", [])
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
                exists = any(s['name'] == s_name for s in staff_list)
                if exists:
                    st.error("⚠️ આ નામનો કર્મચારી પહેલેથી જ છે!")
                else:
                    new_id = len(staff_list) + 1
                    staff_list.append({
                        "id": new_id,
                        "name": s_name,
                        "designation": s_desig,
                        "daily_rate": s_rate,
                        "mobile": s_mob,
                        "address": s_address,
                        "work_type": s_work_type,
                        "shift_timing": s_shift
                    })
                    save_table("staff", staff_list)
                    st.success(f"✅ કર્મચારી '{s_name}' સફળતાપૂર્વક સેવ થઈ ગયો!")
                    st.rerun()
            else:
                st.error("⚠️ કૃપા કરીને નામ અને રોજ ભરો!")

    with staff_tab2:
        if staff_list:
            staff_names_list = [s['name'] for s in staff_list]
            edit_staff_choice = st.selectbox("એડિટ કરવા માટે કર્મચારી પસંદ કરો", staff_names_list, key="edit_sel_staff")
            curr_data = next((s for s in staff_list if s['name'] == edit_staff_choice), None)

            if curr_data:
                with st.form("edit_staff_form"):
                    st.markdown(f"**કર્મચારી ID: #{curr_data.get('id', 1)}**")
                    e_name = st.text_input("કર્મચારીનું નામ", value=curr_data['name'])
                    e_rate = st.number_input("રોજ / Daily Rate (RS)", min_value=0.0, value=float(curr_data['daily_rate']), step=50.0)
                    e_wtype = st.selectbox("કામનો પ્રકાર (Work Type)", ["Full Time", "Part Time"], index=0 if curr_data.get('work_type') != "Part Time" else 1)
                    e_addr = st.text_area("સરનામું (Address)", value=curr_data.get('address', ''), height=80)
                    e_desig = st.text_input("હોદ્દો (Designation)", value=curr_data.get('designation', ''))
                    e_mob = st.text_input("મોબાઈલ નંબર", value=curr_data.get('mobile', ''))
                    e_shift = st.text_input("Shift Timing", value=curr_data.get('shift_timing', ''))

                    submit_update = st.form_submit_button("🔄 Update Staff Details", type="primary")

                    if submit_update:
                        for s in staff_list:
                            if s['name'] == edit_staff_choice:
                                s['name'] = e_name
                                s['daily_rate'] = e_rate
                                s['work_type'] = e_wtype
                                s['address'] = e_addr
                                s['designation'] = e_desig
                                s['mobile'] = e_mob
                                s['shift_timing'] = e_shift
                        save_table("staff", staff_list)
                        st.success("✅ વિગતો અપડેટ થઈ ગઈ!")
                        st.rerun()
        else:
            st.info("કોઈ કર્મચારી ઉપલબ્ધ નથી.")

    st.write("---")
    st.markdown('<div class="section-title">🗑️ કર્મચારીને લિસ્ટમાંથી ડિલીટ કરો</div>', unsafe_allow_html=True)
    if staff_list:
        staff_names_list = [s['name'] for s in staff_list]
        del_staff_name = st.selectbox("ડિલીટ કરવા માટે કર્મચારી પસંદ કરો", staff_names_list, key="del_sel_staff")
        if st.button("🗑️ Delete Staff", type="secondary"):
            staff_list = [s for s in staff_list if s['name'] != del_staff_name]
            save_table("staff", staff_list)
            st.success(f"✅ કર્મચારી '{del_staff_name}' ડિલીટ થઈ ગયો!")
            st.rerun()

    st.write("---")
    st.markdown("### 📋 હાલના કર્મચારીઓનું લિસ્ટ")
    if staff_list:
        st.dataframe(staff_list, use_container_width=True)

# --- 8. BACKUP & RESTORE ---
elif choice == "💾 Backup & Restore (બેકઅપ & રીસ્ટોર)":
    st.markdown('<div class="section-title">💾 ડેટાબેઝ સુરક્ષા & બેકઅપ સિસ્ટમ (Backup & Restore)</div>', unsafe_allow_html=True)
    
    b_tab1, b_tab2 = st.tabs(["📥 બેકઅપ ડાઉનલોડ કરો (Export)", "📤 બેકઅપ સોફ્ટવેરમાં ચડાવો (Restore)"])
    
    with b_tab1:
        st.write("💡 આખો ડેટા એક્સેલ ફાઈલ તરીકે ડાઉનલોડ કરી લો.")
        if st.button("📦 આખા ડેટાનો બેકઅપ તૈયાર કરો", type="primary"):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                for t in ["staff", "advance_payments", "salary_history", "expenses"]:
                    df = pd.DataFrame(load_table(t, []))
                    df.to_excel(writer, sheet_name=t, index=False)
            output.seek(0)
            st.download_button(
                label="⬇️ Excel Backup ફાઈલ ડાઉનલોડ કરો (.xlsx)",
                data=output.getvalue(),
                file_name=f"Payroll_CloudJSON_Backup_{datetime.date.today().strftime('%Y_%m_%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.success("✅ બેકઅપ તૈયાર છે!")

    with b_tab2:
        uploaded_backup = st.file_uploader("📂 Choose Backup Excel File (.xlsx)", type=["xlsx"])
        if uploaded_backup is not None:
            if st.button("🚀 ડેટાબેઝમાં બેકઅપ રીસ્ટોર કરો", type="primary"):
                try:
                    excel_data = pd.ExcelFile(uploaded_backup)
                    for t in ["staff", "advance_payments", "salary_history", "expenses"]:
                        if t in excel_data.sheet_names:
                            df = pd.read_excel(excel_data, t)
                            save_table(t, df.to_dict(orient="records"))
                    st.success("🎉 બેકઅપ સફળતાપૂર્વક રીસ્ટોર થઈ ગયો!")
                    st.rerun()
                except Exception as e:
                    st.error(f"⚠️ ભૂલ થઈ: {e}")

