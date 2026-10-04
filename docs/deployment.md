# Deployment

Local:

```bash
pip install -r requirements.txt
python scripts/generate_demo_data.py
python scripts/run_pipeline.py
python scripts/run_api.py        # :8000
python scripts/run_dashboard.py  # :8501
```

Production-style: run uvicorn with `--workers 2`, front the dashboard with a
reverse proxy, mount `data/` and `models/` as volumes, and schedule
`python scripts/run_pipeline.py` via cron. Not yet containerized.
