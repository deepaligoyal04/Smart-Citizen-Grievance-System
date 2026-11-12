# Smart Citizen Grievance & Public Service Management System

A Python + Streamlit + SQLite academic demonstration project for registering, tracking,
prioritising and analysing citizen grievances.

## Features
- Citizen complaint registration with unique complaint IDs
- Automatic department assignment based on complaint category
- Rule-based priority classification (Low, Medium, High, Critical)
- SQLite database for persistent complaint storage
- Search, filtering and status updates
- Dashboard KPIs, monthly trends, department-wise charts and priority analysis
- Excel and PDF report downloads

## Dataset
`data/citizen_grievances.csv` contains 500 **synthetically generated demonstration records**.
It is not official CPGRAMS or government data. New complaints submitted in the app are
stored in `grievance.db`.

## Run on Windows
1. Install Python 3.10 or newer.
2. Open a terminal in this project folder.
3. Create and activate a virtual environment (optional but recommended):
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```
4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
5. Start the app:
   ```powershell
   streamlit run app.py
   ```
6. Open the local URL shown in the terminal (usually http://localhost:8501).

The SQLite database is created automatically on first launch and seeded from the CSV
when it is empty.

## Important project notes
- Priority assignment currently uses transparent keyword-based rules, not a trained ML model.
- Department mapping is a configurable demonstration mapping.
- The initial sample dataset is synthetic. Do not describe it as real citizen data.
- Change and test the rules, fields and UI before presenting this as your own project.
