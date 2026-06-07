# Integrated Hiring Pipeline Architecture

This project is a standalone implementation of the architecture below:

+------------------------+
| Job Generator          |
| JD Generation          |
+-----------+------------+
			|
			v
+------------------------+
| Candidate Database     |
| Resume Search          |
+-----------+------------+
			|
			v
+------------------------+
| AI Matching Engine     |
| Similarity Search      |
+-----------+------------+
			|
			v
+------------------------+
| Email Service          |
| SMTP / SendGrid        |
+-----------+------------+
			|
			v
+------------------------+
| Recruiter Dashboard    |
+------------------------+

No external project paths are required at runtime.

## Core files in this new project

- run_integrated_pipeline.py: stage-based orchestrator for all five architecture blocks.
- src/ingest/naukri_scraper.py: built-in Naukri scraper for job link collection.
- src/job_generator/jd_service.py: built-in JD generation from job links.
- src/candidate_db/repository.py: local candidate workbook loader.
- src/matching/engine.py: resume-to-JD matching engine and scoring.
- src/email/service.py: email service stage with SMTP/SendGrid provider support.
- src/dashboard/app.py: recruiter dashboard (shortlist table, score analytics, metrics).
- Run_Integrated_Pipeline.bat: launcher for pipeline execution.
- Run_Dashboard.bat: launcher for recruiter dashboard.

## Run the architecture pipeline

```powershell
python .\run_integrated_pipeline.py --keyword "Oracle Fusion Application" --pages 2 --rows 10
```

Use the candidate workbook:

```powershell
python .\run_integrated_pipeline.py --candidate-profiles-file .\output\candidate_profiles.xlsx
```

Optional manual login flow for Naukri:

```powershell
python .\run_integrated_pipeline.py --login --keyword "Oracle Fusion Application" --pages 2 --rows 10
```

Tune matching strictness:

```powershell
python .\run_integrated_pipeline.py --top-k 5 --min-score 0.15 --rows 20
```

Enable real email sends via SMTP:

```powershell
python .\run_integrated_pipeline.py --send-emails --email-provider smtp --notification-email recruiter@example.com
```

Enable real email sends via SendGrid:

```powershell
python .\run_integrated_pipeline.py --send-emails --email-provider sendgrid --notification-email recruiter@example.com
```

## Launch recruiter dashboard

```powershell
streamlit run src\dashboard\app.py
```

## Outputs generated

- output/job_links.xlsx
- output/jd_catalog.csv
- output/candidate_profiles.xlsx
- output/shortlisted_profiles.csv
- output/email_dispatch.csv
- output/pipeline_summary.json

## Data inputs

- Candidate profiles default location: output/candidate_profiles.xlsx
- Browser profile default location: output/naukri_browser_profile
