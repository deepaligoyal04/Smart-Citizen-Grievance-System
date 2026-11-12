import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from database import initialize_database, fetch_grievances, insert_grievance, update_status

st.set_page_config(page_title="Smart Citizen Grievance System", page_icon="🏛️", layout="wide")
initialize_database()

DEPARTMENT_MAP = {
    "Roads & Infrastructure": "Public Works Department",
    "Water Supply": "Water Supply Department",
    "Electricity": "Electricity Department",
    "Sanitation": "Municipal Corporation",
    "Public Safety": "Public Safety Department",
    "Healthcare": "Health Department",
    "Public Transport": "Transport Department",
    "Street Lighting": "Municipal Corporation",
}
CATEGORIES = list(DEPARTMENT_MAP.keys())

def assign_priority(description, category):
    text = description.lower()
    critical_words = ["fire", "accident", "electrocution", "emergency", "life-threatening", "injury"]
    high_words = ["dangerous", "overflow", "burst", "sparks", "unsafe", "no water", "power failure"]
    if any(word in text for word in critical_words):
        return "Critical"
    if any(word in text for word in high_words) or category == "Public Safety":
        return "High"
    if len(text.split()) > 12:
        return "Medium"
    return "Low"

def make_excel(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        data.to_excel(writer, index=False, sheet_name="Grievances")
    return output.getvalue()

def make_pdf(data):
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=landscape(A4))
    styles = getSampleStyleSheet()
    elements = [Paragraph("Smart Citizen Grievance Report", styles["Title"]), Spacer(1, 12)]
    columns = ["Complaint ID", "Category", "Department", "Priority", "Status", "Submitted"]
    view = data[columns].fillna("").astype(str)
    table_data = [columns] + view.head(35).values.tolist()
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#23395d")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.4, colors.grey),
        ("FONTSIZE", (0,0), (-1,-1), 7),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#eef2f7")]),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(f"Records shown: {min(len(data),35)} of {len(data)} filtered records.", styles["Normal"]))
    doc.build(elements)
    return output.getvalue()

st.title("🏛️ Smart Citizen Grievance & Public Service Management")
st.caption("A demonstration system for registering, tracking and analysing public-service complaints.")
st.info("Demo dataset: the initial 500 records are synthetically generated for academic demonstration, not official government records.")

page = st.sidebar.radio("Navigation", ["Dashboard", "Register Complaint", "Manage Complaints", "Reports"])
df = fetch_grievances()
if not df.empty:
    df["submitted_date"] = pd.to_datetime(df["submitted_date"], errors="coerce")
    df["resolved_date"] = pd.to_datetime(df["resolved_date"], errors="coerce")

if page == "Dashboard":
    st.subheader("Grievance Overview")
    f1, f2, f3 = st.columns(3)
    with f1: status_filter = st.multiselect("Filter by status", sorted(df["status"].dropna().unique()))
    with f2: dept_filter = st.multiselect("Filter by department", sorted(df["department"].dropna().unique()))
    with f3: priority_filter = st.multiselect("Filter by priority", ["Low","Medium","High","Critical"])
    filtered = df.copy()
    if status_filter: filtered = filtered[filtered.status.isin(status_filter)]
    if dept_filter: filtered = filtered[filtered.department.isin(dept_filter)]
    if priority_filter: filtered = filtered[filtered.priority.isin(priority_filter)]
    total = len(filtered)
    resolved = int((filtered.status == "Resolved").sum())
    pending = int(filtered.status.isin(["Pending", "In Progress"]).sum())
    resolution_rate = (resolved / total * 100) if total else 0
    a,b,c,d = st.columns(4)
    a.metric("Total Complaints", f"{total:,}")
    b.metric("Resolved", f"{resolved:,}")
    c.metric("Pending / In Progress", f"{pending:,}")
    d.metric("Resolution Rate", f"{resolution_rate:.1f}%")
    st.divider()
    left, right = st.columns(2)
    with left:
        status_counts = filtered["status"].value_counts().rename_axis("Status").reset_index(name="Count")
        st.plotly_chart(px.pie(status_counts, names="Status", values="Count", hole=.45, title="Complaint Status Distribution"), use_container_width=True)
    with right:
        dept_counts = filtered["department"].value_counts().rename_axis("Department").reset_index(name="Complaints")
        st.plotly_chart(px.bar(dept_counts, x="Department", y="Complaints", title="Department-wise Complaints", color="Department"), use_container_width=True)
    left, right = st.columns(2)
    with left:
        trend = filtered.dropna(subset=["submitted_date"]).copy()
        if not trend.empty:
            trend["Month"] = trend["submitted_date"].dt.to_period("M").astype(str)
            monthly = trend.groupby("Month").size().reset_index(name="Complaints")
            st.plotly_chart(px.line(monthly, x="Month", y="Complaints", markers=True, title="Monthly Complaint Trend"), use_container_width=True)
    with right:
        p = filtered["priority"].value_counts().reindex(["Low","Medium","High","Critical"], fill_value=0).rename_axis("Priority").reset_index(name="Count")
        st.plotly_chart(px.bar(p, x="Priority", y="Count", title="Priority Breakdown", color="Priority"), use_container_width=True)
    st.subheader("Recent Complaints")
    st.dataframe(filtered.sort_values("submitted_date", ascending=False).head(15), use_container_width=True, hide_index=True)

elif page == "Register Complaint":
    st.subheader("Register a New Citizen Complaint")
    with st.form("complaint_form", clear_on_submit=True):
        name = st.text_input("Citizen name")
        category = st.selectbox("Complaint category", CATEGORIES)
        area = st.selectbox("Area / Ward", [f"Ward {i:02d} - {n}" for i,n in enumerate(
            ["Central","North","South","East","West","Market","Industrial","Residential"], 1)])
        description = st.text_area("Describe the complaint", placeholder="Explain the issue and its location...")
        submitted = st.form_submit_button("Submit Complaint", type="primary")
    if submitted:
        if not name.strip() or not description.strip():
            st.error("Please enter both citizen name and complaint description.")
        else:
            existing = fetch_grievances()
            next_id = len(existing) + 1
            complaint_id = f"GRV-{date.today().year}-{next_id:04d}"
            department = DEPARTMENT_MAP[category]
            priority = assign_priority(description, category)
            insert_grievance((complaint_id, name.strip(), category, department, description.strip(),
                              area, priority, "Pending", date.today().isoformat(), None, None))
            st.success(f"Complaint registered successfully. Your complaint ID is {complaint_id}")
            st.write(f"Assigned department: **{department}** | Priority: **{priority}**")

elif page == "Manage Complaints":
    st.subheader("Search and Update Complaints")
    search = st.text_input("Search by complaint ID, citizen, category or area")
    view = df.copy()
    if search:
        mask = view.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
        view = view[mask]
    st.dataframe(view, use_container_width=True, hide_index=True)
    if not view.empty:
        selected = st.selectbox("Select complaint ID", view["complaint_id"].tolist())
        current = view.loc[view.complaint_id == selected, "status"].iloc[0]
        new_status = st.selectbox("Update status", ["Pending","In Progress","Resolved","Rejected"],
                                  index=["Pending","In Progress","Resolved","Rejected"].index(current))
        if st.button("Save Status Update", type="primary"):
            update_status(selected, new_status)
            st.success(f"{selected} updated to {new_status}.")
            st.rerun()

elif page == "Reports":
    st.subheader("Download Administrative Reports")
    st.write("Export the grievance records currently stored in the SQLite database.")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("Download Excel Report", make_excel(df), "grievance_report.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.download_button("Download PDF Report", make_pdf(df), "grievance_report.pdf", "application/pdf")

st.sidebar.divider()
st.sidebar.caption("Academic project demo • Python + SQLite + Streamlit + Pandas + Plotly")
