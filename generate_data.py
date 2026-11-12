"""Generate 500 synthetic citizen grievance records for project demonstration."""
from pathlib import Path
import random
from datetime import datetime, timedelta
import pandas as pd

# The committed sample CSV is already available in data/citizen_grievances.csv.
# Run this file to regenerate it with fresh synthetic records.
random.seed()
categories = {
    "Roads & Infrastructure": ("Public Works Department", [
        "Pothole on main road", "Damaged road surface", "Broken footpath"]),
    "Water Supply": ("Water Supply Department", [
        "No water supply since yesterday", "Leaking water pipeline", "Dirty water from tap"]),
    "Electricity": ("Electricity Department", [
        "Frequent power cuts", "Damaged electric wire", "Voltage fluctuation"]),
    "Sanitation": ("Municipal Corporation", [
        "Garbage not collected", "Overflowing public dustbin", "Blocked public drain"]),
    "Public Safety": ("Public Safety Department", [
        "Unsafe open manhole", "Broken traffic signal", "Street safety concern"]),
    "Healthcare": ("Health Department", [
        "Shortage of medicines", "Clinic sanitation issue", "Long waiting time"]),
    "Public Transport": ("Transport Department", [
        "Irregular bus service", "Damaged bus stop shelter", "Bus not stopping"]),
    "Street Lighting": ("Municipal Corporation", [
        "Street lights not working", "Damaged street lamp", "Dark public road"]),
}
statuses = ["Pending", "In Progress", "Resolved", "Rejected"]
areas = [f"Ward {i:02d}" for i in range(1, 9)]
names = ["Aarav Sharma", "Aanya Verma", "Rohan Gupta", "Priya Singh", "Kabir Mehta"]
rows = []
today = datetime.now()
for i in range(1, 501):
    category = random.choice(list(categories))
    department, descriptions = categories[category]
    submitted = today - timedelta(days=random.randint(0, 365))
    status = random.choices(statuses, weights=[28, 24, 42, 6])[0]
    days = random.randint(1, 18) if status == "Resolved" else ""
    rows.append({
        "complaint_id": f"GRV-{submitted.year}-{i:04d}",
        "citizen_name": random.choice(names),
        "category": category,
        "department": department,
        "description": random.choice(descriptions),
        "area": random.choice(areas),
        "priority": random.choice(["Low", "Medium", "High", "Critical"]),
        "status": status,
        "submitted_date": submitted.strftime("%Y-%m-%d"),
        "resolved_date": (submitted + timedelta(days=days)).strftime("%Y-%m-%d") if days else "",
        "resolution_days": days,
    })
output = Path(__file__).parent / "data" / "citizen_grievances.csv"
pd.DataFrame(rows).to_csv(output, index=False)
print(f"Generated {len(rows)} synthetic records at {output}")
