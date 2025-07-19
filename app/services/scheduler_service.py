from apscheduler.schedulers.background import BackgroundScheduler
import subprocess
import time

def run_nightly_refresh():
    print("🌙 Running nightly_refresh...")
    subprocess.call(["python", "scripts/nightly_refresh.py"])

def run_nightly_evaluation():
    print("📊 Running nightly evaluation...")
    subprocess.call(["python", "evaluate.py"])

def start_scheduler():
    scheduler = BackgroundScheduler(timezone="UTC")

    scheduler.add_job(run_nightly_refresh, trigger="cron", hour=2, minute=0)
    scheduler.add_job(run_nightly_evaluation, trigger="cron", hour=3, minute=0)
    scheduler.add_job(run_nightly_refresh, 'interval', minutes=1)
    scheduler.start()
    print("✅ Scheduler started.")
