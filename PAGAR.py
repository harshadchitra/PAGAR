import streamlit as st
import sqlite3
import datetime
import calendar
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


# ----------------- પેજ વિગતો અને થીમ સેટઅપ -----------------
st.set_page_config(
    page_title="Courier Solution - Payroll Pro",
    page_icon="💼",
    layout="wide"
)

# Custom CSS for Modern UI/UX
st.markdown("""
<style>
    /* Main Background & Font Styling */
    .stApp {
        background-color: #f4f6f9;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Header Title Design */
    .main-title {
        background: linear-gradient(135deg, #0e2a47 0%, #1a5276 100%);
        color: #ffffff;
        padding: 20px 25px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        text-align: center;
    }
    .main-title h1 {
        margin: 0;
        font-size: 28px;
        font-weight: 700;
        letter-spacing: 1px;
    }
    .main-title p {
        margin: 5px 0 0 0;
        font-size: 14px;
        opacity: 0.85;
    }

    /* Card Box Design */
    .metric-card {
        background: #ffffff;
        padding: 18px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-left: 5px solid #1a5276;
        margin-bottom: 15px;
    }
    
    /* Sidebar Customization */
    [data-testid="stSidebar"] {
        background-color: #0e2a47;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* Custom Buttons Styling */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    /* Section Subheaders */
    .sub-header {
        color: #0e2a47;
        font-size: 20px;
        font-weight: 600;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 8px;
        margin-top: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)


# ----------------- ડેટાબેઝ સેટઅપ -----------------
def init_db():
    conn = sqlite3.connect("payroll_mobile.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            designation TEXT,
            daily_rate REAL,
            mobile TEXT,
            address TEXT
        )
    """)
    
    try:
        cursor.execute("ALTER TABLE staff ADD COLUMN address TEXT")
    except sqlite3.OperationalError:
        pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_name TEXT,
            date TEXT,
            status TEXT,
            UNIQUE(staff_name, date)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS advance_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_name TEXT,
            date TEXT,
            amount REAL,
            note TEXT
        )
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
        )
    """)
    conn.commit()
    conn.close()


init_db()


# ----------------- DIGITAL SALARY SLIP PDF -----------------
def generate_salary_slip_pdf_bytes(staff_name, month_year, total_days, present_days, half_days, absent_days, daily_rate, gross_salary, advance_deduction, net_salary):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#002147'), alignment=1, spaceAfter=2)
    sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#555555'), alignment=1, spaceAfter=15)
    head_style = ParagraphStyle('HeadStyle', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#d9534f'), alignment=1, spaceAfter=15)
    normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontSize=10, leading=14)

    story.append(Paragraph("COURIER SOLUTION - PAYROLL", title_style))
    story.append(Paragraph("Monthly Salary Slip / Digital Statement", sub_style))
    story.append(Paragraph(f"SALARY SLIP FOR {month_year.upper()}", head_style))

    data_info = [
        [Paragraph(f"<b>Staff Name:</b> {staff_name}", normal_style), Paragraph(f"<b>Date:</b> {datetime.date.today().strftime('%d/%m/%Y')}", normal_style)],
        [Paragraph(f"<b>Daily Rate:</b> RS {daily_rate:,.2f}", normal_style), Paragraph(f"<b>Working Period:</b> {month_year}", normal_style)]
    ]
    t_info = Table(data_info, colWidths=[250, 250])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8f9fa')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#002147')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 15))

    data_att = [
        [Paragraph("<b>Attendance Metrics</b>", normal_style), Paragraph("<b>Days</b>", normal_style)],
        [Paragraph("Total Days in Month", normal_style), Paragraph(str(total_days), normal_style)],
        [Paragraph("Full Present Days", normal_style), Paragraph(str(present_days), normal_style)],
        [Paragraph("Half Days", normal_style), Paragraph(str(half_days), normal_style)],
        [Paragraph("Absent Days", normal_style), Paragraph(str(absent_days), normal_style)],
    ]
    t_att = Table(data_att, colWidths=[330, 170])
    t_att.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#002147')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_att)
    story.append(Spacer(1, 15))

    data_sal = [
        [Paragraph("<b>Salary Breakdown</b>", normal_style), Paragraph("<b>Amount (RS)</b>", normal_style)],
        [Paragraph("Gross Earned Salary", normal_style), Paragraph(f"RS {gross_salary:,.2f}", normal_style)],
        [Paragraph("Less: Advance Deduction", normal_style), Paragraph(f"- RS {advance_deduction:,.2f}", normal_style)],
        [Paragraph("<b>NET PAYABLE SALARY</b>", normal_style), Paragraph(f"<b>RS {net_salary:,.2f}</b>", normal_style)]
    ]
    t_sal = Table(data_sal, colWidths=[330, 170])
    t_sal.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#008000')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#e8f5e9')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_sal)
    story.append(Spacer(1, 40))

    data_sign = [
        [Paragraph("<b>Employee Signature</b>", normal_style), Paragraph("<b>Authorized Signatory</b>", ParagraphStyle('R', parent=normal_style, alignment=2))]
    ]
    t_sign = Table(data_sign, colWidths=[250, 250])
    story.append(t_sign)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# ----------------- MAIN HEADER UI -----------------
st.markdown("""
<div class="main-title">
    <h1>💼 COURIER SOLUTION - PAYROLL PRO</h1>
    <p>Staff Attendance, Advance & Digital Salary Management System</p>
</div>
""", unsafe_allow_html=True)


menu = [
    "📅 Daily Attendance (હાજરી પૂરો)",
    "📊 Monthly Calendar View (કેલેન્ડર)",
    "💰 Salary & Digital Slip (પગાર & લિસ્ટ)",
    "💸 Advance Entry (ઉપાડ)",
    "👤 Manage Staff (કર્મચારી)"
]

st.sidebar.markdown("### 📌 Navigation Menu")
choice = st.sidebar.radio("", menu)


# --- 1. DAILY ATTENDANCE ---
if choice == "📅 Daily Attendance (હાજરી પૂરો)":
    st.markdown('<div class="sub-header">📅 રોજની હાજરી પૂરો</div>', unsafe_allow_html=True)
    
    col_d1, col_d2 = st.columns([1, 2])
    with col_d1:
        att_date = st.date_input("તારીખ પસંદ કરો", datetime.date.today())

    conn = sqlite3.connect("payroll_mobile.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM staff ORDER BY name ASC")
    staff_list = [r[0] for r in cursor.fetchall()]

    if not staff_list:
        st.warning("⚠️ કોઈ કર્મચારી ઉમેરેલ નથી! પહેલા 'Manage Staff' માં જઈને ઉમેરો.")
    else:
        st.write("")
        att_data = {}
        for staff in staff_list:
            cursor.execute("SELECT status FROM attendance WHERE staff_name=? AND date=?", (staff, str(att_date)))
            row = cursor.fetchone()
            default_idx = 0
            if row:
                if row[0] == "Absent": default_idx = 1
                elif row[0] == "Half": default_idx = 2

            col1, col2 = st.columns([2, 2])
            with col1:
                st.markdown(f"👤 **{staff}**")
            with col2:
                status = st.selectbox(f"Status for {staff}", ["Present", "Absent", "Half"], index=default_idx, key=f"att_{staff}", label_visibility="collapsed")
                att_data[staff] = status

        st.write("---")
        if st.button("💾 Save Attendance (હાજરી સેવ કરો)", type="primary", use_container_width=True):
            for staff, status in att_data.items():
                cursor.execute("""
                    INSERT INTO attendance (staff_name, date, status)
                    VALUES (?, ?, ?)
                    ON CONFLICT(staff_name, date) DO UPDATE SET status=excluded.status
                """, (staff, str(att_date), status))
            conn.commit()
            st.success(f"✅ તારીખ {att_date} ની હાજરી સફળતાપૂર્વક સેવ થઈ ગઈ!")
    conn.close()


# --- 2. MONTHLY CALENDAR VIEW ---
elif choice == "📊 Monthly Calendar View (કેલેન્ડર)":
    st.markdown('<div class="sub-header">📊 આખા મહિનાનું હાજરી કેલેન્ડર</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        month = st.number_input("મહિનો (1-12)", min_value=1, max_value=12, value=datetime.date.today().month)
    with col2:
        year = st.number_input("વર્ષ (Year)", min_value=2020, max_value=2030, value=datetime.date.today().year)

    max_days = calendar.monthrange(int(year), int(month))[1]

    conn = sqlite3.connect("payroll_mobile.db")
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
            day_num = int(date_str.split("-")[2])
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
    conn.close()


# --- 3. SALARY & PAID STATUS LIST ---
elif choice == "💰 Salary & Digital Slip (પગાર & લિસ્ટ)":
    st.markdown('<div class="sub-header">💰 માસિક પગાર ગણતરી, સ્લિપ & પેઇડ/પેન્ડિંગ લિસ્ટ</div>', unsafe_allow_html=True)
    
    conn = sqlite3.connect("payroll_mobile.db")
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
            
            with col1:
                st.write(f"👤 **{staff}**")
            
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
                    
                    cursor.execute("SELECT status FROM attendance WHERE staff_name=? AND date BETWEEN ? AND ?", (staff, start_date, end_date))
                    att_rows = cursor.fetchall()
                    present_count = sum(1 for r in att_rows if r[0] == "Present")
                    half_count = sum(1 for r in att_rows if r[0] == "Half")
                    absent_count = sum(1 for r in att_rows if r[0] == "Absent")

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
                        net_salary=paid_records[staff]['net']
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

        st.markdown('<div class="sub-header">🧮 નવો પગાર ગણો અને સ્લિપ બનાવો</div>', unsafe_allow_html=True)
        sal_staff = st.selectbox("જેનો પગાર બાકી છે તે કર્મચારી પસંદ કરો", staff_list)

        if st.button("🧮 Calculate & Generate Salary Slip", type="primary", use_container_width=True):
            if sal_staff in paid_records:
                st.warning(f"⚠️ કર્મચારી '{sal_staff}' નો પગાર આ મહિના માટે પહેલેથી ચૂકવાઈ ગયેલ છે!")
            else:
                cursor.execute("SELECT daily_rate FROM staff WHERE name=?", (sal_staff,))
                daily_rate = cursor.fetchone()[0]

                max_days = calendar.monthrange(int(sel_year), int(sel_month))[1]
                start_date = f"{sel_year}-{int(sel_month):02d}-01"
                end_date = f"{sel_year}-{int(sel_month):02d}-{max_days}"

                cursor.execute("SELECT status FROM attendance WHERE staff_name=? AND date BETWEEN ? AND ?", (sal_staff, start_date, end_date))
                att_rows = cursor.fetchall()
                present_count = sum(1 for r in att_rows if r[0] == "Present")
                half_count = sum(1 for r in att_rows if r[0] == "Half")
                absent_count = sum(1 for r in att_rows if r[0] == "Absent")

                cursor.execute("SELECT SUM(amount) FROM advance_payments WHERE staff_name=? AND date BETWEEN ? AND ?", (sal_staff, start_date, end_date))
                adv_row = cursor.fetchone()
                adv_amt = adv_row[0] if adv_row[0] else 0.0

                payable_days = present_count + (half_count * 0.5)
                gross_salary = payable_days * daily_rate
                net_salary = max(0.0, gross_salary - adv_amt)

                paid_date_str = datetime.date.today().strftime("%Y-%m-%d")
                cursor.execute("""
                    INSERT INTO salary_history (staff_name, month_year, payable_days, gross_salary, advance_deduction, net_salary, paid_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (sal_staff, month_year_str, payable_days, gross_salary, adv_amt, net_salary, paid_date_str))
                conn.commit()
                st.success(f"✅ '{sal_staff}' નો પગાર સફળતાપૂર્વક જમા થઈ ગયો છે!")
                st.rerun()

        st.write("---")
        st.markdown('<div class="sub-header">🗑️ પગાર રેકોર્ડ ડિલીટ કરો</div>', unsafe_allow_html=True)
        cursor.execute("SELECT id, staff_name, month_year, net_salary, paid_date FROM salary_history ORDER BY id DESC")
        all_history = cursor.fetchall()

        if all_history:
            hist_options = {f"ID: #{r[0]} | Staff: {r[1]} | Month: {r[2]} | Net: RS {r[3]}": r[0] for r in all_history}
            selected_hist_label = st.selectbox("ડિલીટ કરવા માટે રેકોર્ડ પસંદ કરો", list(hist_options.keys()))
            
            if st.button("🗑️ Delete Selected Salary Record", type="secondary"):
                del_id = hist_options[selected_hist_label]
                cursor.execute("DELETE FROM salary_history WHERE id=?", (del_id,))
                conn.commit()
                st.success("✅ પગાર રેકોર્ડ સફળતાપૂર્વક ડિલીટ થઈ ગયો છે!")
                st.rerun()
        else:
            st.info("કોઈ Paid રેકોર્ડ ઉપલબ્ધ નથી.")

    conn.close()


# --- 4. ADVANCE ENTRY ---
elif choice == "💸 Advance Entry (ઉપાડ)":
    st.markdown('<div class="sub-header">💸 કર્મચારી ઉપાડ / એડવાન્સ એન્ટ્રી</div>', unsafe_allow_html=True)
    
    conn = sqlite3.connect("payroll_mobile.db")
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
                st.success(f"✅ RS {adv_amt}/- નો ઉપાડ સફળતાપૂર્વક જમા થઈ ગયો!")
            else:
                st.error("⚠️ કૃપા કરીને સાચી રકમ નાખો!")

        st.write("---")
        st.markdown("### 📜 ઉપાડ રેકોર્ડ હિસ્ટ્રી")
        cursor.execute("SELECT id, staff_name, date, amount, note FROM advance_payments ORDER BY id DESC")
        adv_rows = cursor.fetchall()
        if adv_rows:
            st.dataframe(adv_rows, use_container_width=True)
    conn.close()


# --- 5. MANAGE STAFF ---
elif choice == "👤 Manage Staff (કર્મચારી)":
    st.markdown('<div class="sub-header">👤 નવો કર્મચારી ઉમેરો</div>', unsafe_allow_html=True)
    
    conn = sqlite3.connect("payroll_mobile.db")
    cursor = conn.cursor()

    col1, col2 = st.columns(2)
    with col1:
        s_name = st.text_input("કર્મચારીનું નામ")
        s_rate = st.number_input("રોજ / Daily Rate (RS)", min_value=0.0, step=50.0)
        s_address = st.text_area("સરનામું (Address)", height=80)
    with col2:
        s_desig = st.text_input("હોદ્દો (Designation)")
        s_mob = st.text_input("મોબાઈલ નંબર")

    if st.button("💾 Save Staff", type="primary", use_container_width=True):
        if s_name and s_rate > 0:
            try:
                cursor.execute("INSERT INTO staff (name, designation, daily_rate, mobile, address) VALUES (?, ?, ?, ?, ?)", (s_name, s_desig, s_rate, s_mob, s_address))
                conn.commit()
                st.success(f"✅ કર્મચારી '{s_name}' સફળતાપૂર્વક સેવ થઈ ગયો!")
                st.rerun()
            except sqlite3.IntegrityError:
                st.error("⚠️ આ નામનો કર્મચારી પહેલેથી જ ડેટાબેઝમાં છે!")
        else:
            st.error("⚠️ કૃપા કરીને નામ અને રોજ ભરો!")

    st.write("---")
    st.markdown('<div class="sub-header">🗑️ કર્મચારીને લિસ્ટમાંથી દૂર / ડિલીટ કરો</div>', unsafe_allow_html=True)
    
    cursor.execute("SELECT name FROM staff ORDER BY name ASC")
    all_staff_to_del = [r[0] for r in cursor.fetchall()]

    if all_staff_to_del:
        del_staff_name = st.selectbox("છૂટા થયેલા / ડિલીટ કરવા માટે કર્મચારી પસંદ કરો", all_staff_to_del)
        if st.button("🗑️ Delete Staff (કર્મચારી કાઢી નાખો)", type="secondary"):
            cursor.execute("DELETE FROM staff WHERE name=?", (del_staff_name,))
            conn.commit()
            st.success(f"✅ કર્મચારી '{del_staff_name}' સફળતાપૂર્વક ડિલીટ થઈ ગયો છે!")
            st.rerun()
    else:
        st.info("ડિલીટ કરવા માટે કોઈ કર્મચારી ઉપલબ્ધ નથી.")

    st.write("---")
    st.markdown("### 📋 હાલના કર્મચારીઓનું લિસ્ટ (સંપૂર્ણ વિગત)")
    cursor.execute("SELECT id, name, designation, daily_rate, mobile, address FROM staff ORDER BY name ASC")
    staff_rows = cursor.fetchall()
    if staff_rows:
        st.dataframe(staff_rows, use_container_width=True)
    conn.close()

