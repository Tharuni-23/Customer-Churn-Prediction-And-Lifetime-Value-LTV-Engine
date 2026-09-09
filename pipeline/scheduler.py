# ============================================================
# pipeline/scheduler.py
#
# Runs the Churn + LTV pipeline every 5 minutes
# ============================================================

import time
import traceback
from datetime import datetime

from pipeline.main import run_pipeline


# ============================================================
# CONFIGURATION
# ============================================================

INTERVAL_SECONDS = 5 * 60


# ============================================================
# RUN ONE PIPELINE
# ============================================================

def run_scheduled_pipeline():

    start_time = datetime.now()

    print()
    print("=" * 70)
    print("SCHEDULED RUN")
    print("=" * 70)
    print("Started:", start_time)

    try:
        run_pipeline()

        print()
        print("Pipeline run finished successfully.")

    except Exception as error:

        print()
        print("PIPELINE FAILED")
        print("Error:", error)
        traceback.print_exc()


# ============================================================
# START SCHEDULER
# ============================================================

def start_scheduler():

    print()
    print("=" * 70)
    print("CHURN + LTV SCHEDULER STARTED")
    print("=" * 70)
    print("Interval : 5 minutes")
    print("First run starts after 5 minutes.")
    print("Press CTRL+C to stop.\n")

    try:

        while True:

            print("-" * 70)
            print("Waiting for next scheduled run...")
            print("Current time:", datetime.now())
            print("-" * 70)

            time.sleep(INTERVAL_SECONDS)

            run_scheduled_pipeline()

    except KeyboardInterrupt:
        print("\nScheduler stopped.")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    start_scheduler()