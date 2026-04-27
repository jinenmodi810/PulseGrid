.PHONY: demo demo-backend demo-jobs demo-metrics

demo:
	@bash -lc "source venv/bin/activate && PYTHONPATH=backend python3 backend/scripts/demo_orchestrator.py"

demo-backend:
	@bash -lc "source venv/bin/activate && cd backend && PYTHONPATH=. uvicorn app.main:app --reload --host 127.0.0.1 --port 8002"

demo-jobs:
	@bash -lc "source venv/bin/activate && cd backend && PYTHONPATH=. python3 -m app.jobs.outbox_publisher"

demo-metrics:
	@curl -s http://127.0.0.1:8002/metrics | rg "pulsegrid_api_requests_total|pulsegrid_outbox_pending_events|pulsegrid_silver_runtime_processed|pulsegrid_gold_runtime_processed"
