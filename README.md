# SIH 2026 — DVR/NVR Forensic Analysis Tool

> A unified, vendor-agnostic forensic platform for DVR/NVR surveillance evidence acquisition, recovery, analysis, and reporting.

---

## 👥 Team Members & Assignments

| Member | GitHub Username | Assigned Page | Task |
|--------|----------------|---------------|------|
| Member 1 | @member1 | `app.py` + `pages/1_🔍_Device_Detection.py` | Home page + Brand detection |
| Member 2 | @member2 | `pages/2_🔒_Acquisition.py` + `utils/hasher.py` | Forensic imaging + MD5/SHA-256 |
| Member 3 | @member3 | `pages/3_📋_Metadata_Parser.py` + `utils/metadata.py` | Video metadata + Timeline |
| Member 4 | @member4 | `pages/4_🗂️_Recovery_Simulator.py` | Deleted footage recovery simulator |
| Member 5 | @member5 | `pages/5_🤖_AI_Analytics.py` + `utils/detector.py` | AI face & object detection |
| Member 6 | @member6 | `pages/6_📄_Report_Generator.py` + `utils/pdf_report.py` | PDF report + Integration lead |

---

## 🚀 How to Run

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/SIH2026-DVR-Forensic.git
cd SIH2026-DVR-Forensic
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📁 Project Structure

```
SIH2026-DVR-Forensic/
├── app.py                          ← Home page (Member 1)
├── pages/
│   ├── 1_🔍_Device_Detection.py   ← Member 1
│   ├── 2_🔒_Acquisition.py        ← Member 2
│   ← 3_📋_Metadata_Parser.py      ← Member 3
│   ├── 4_🗂️_Recovery_Simulator.py ← Member 4
│   ├── 5_🤖_AI_Analytics.py       ← Member 5
│   └── 6_📄_Report_Generator.py   ← Member 6
├── utils/
│   ├── hasher.py                   ← Member 2
│   ├── metadata.py                 ← Member 3
│   ├── detector.py                 ← Member 5
│   └── pdf_report.py               ← Member 6
├── sample_videos/                  ← Add test videos here
├── outputs/                        ← Generated reports saved here
├── requirements.txt
└── README.md
```

---

## 🛠️ Tech Stack

- **Python 3.11** — Main language
- **Streamlit** — Web app framework (no HTML/CSS needed!)
- **OpenCV + YOLOv8** — AI video analytics
- **moviepy** — Video metadata extraction
- **fpdf2** — PDF report generation
- **Plotly** — Interactive charts and timeline
- **Pandas** — Data tables

---

## 🌿 Git Workflow (For All Members)

### First time setup:
```bash
git clone https://github.com/YOUR_USERNAME/SIH2026-DVR-Forensic.git
cd SIH2026-DVR-Forensic
git checkout -b your-name/feature-name
```

### Daily workflow:
```bash
# Pull latest changes from main
git pull origin main

# Work on your files...

# Save your work
git add .
git commit -m "Add: describe what you did"
git push origin your-name/feature-name
```

### When done with a feature:
- Go to GitHub → Create a Pull Request → Ask Member 6 to review & merge

---

## 📋 GitHub Issues

Each member has a GitHub Issue assigned to them. Check the **Issues** tab to see your tasks.

---

## 📌 Important Rules

1. **Never push directly to `main`** — always use your own branch
2. **Only edit your assigned files** — don't touch others' pages
3. **Commit at least once a day** — even if it's just a small change
4. **Use `sample_videos/`** for test videos — don't commit large video files (use `.gitignore`)
5. **Ask Member 6** if you're stuck on integration

---

## 🎯 Demo Flow

1. Open app → Home page
2. Upload video → Device Detection (Brand identified)
3. Acquisition → MD5/SHA-256 hash generated
4. Metadata Parser → Video properties + Timeline
5. Recovery Simulator → Deleted files "recovered"
6. AI Analytics → Face + object detection live
7. Report Generator → Download forensic PDF
