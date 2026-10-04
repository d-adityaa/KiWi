# API reference

Base: `http://127.0.0.1:8000`

GET  /health            /models            /regions
GET  /skill             /weights           /weights/summary
GET  /forecast          /confidence        /uncertainty   (coverage)
GET  /extremes          /risk              /data-health
GET  /runs              /registry          /explain /evaluate
POST /run               /fallback          /forecast/query /export

All responses are demo/synthetic. See `api/routes/api.py`.
