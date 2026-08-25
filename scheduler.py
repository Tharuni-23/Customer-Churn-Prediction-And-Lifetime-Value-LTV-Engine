# ============================================================
# scheduler.py
#
# Runs the prediction pipeline every five minutes.
# ============================================================

import time
import traceback

from datetime import datetime

from main import run_pipeline


# ============================================================
# CONFIGURATION
# ============================================================

INTERVAL_SECONDS = (
    5 * 60
)


# ============================================================
# RUN ONE PIPELINE
# ============================================================

def run_scheduled_pipeline():

    start_time = datetime.now()


    print()
    print("=" * 70)
    print("SCHEDULED RUN")
    print("=" * 70)

    print(
        "Started:",
        start_time
    )


    try:

        run_pipeline()

        print()
        print(
            "Pipeline run finished successfully."
        )


    except Exception as error:

        print()
        print(
            "PIPELINE FAILED"
        )

        print(
            "Error:",
            error
        )

        traceback.print_exc()


# ============================================================
# START SCHEDULER
# ============================================================

def start_scheduler():

    print()
    print("=" * 70)
    print("CHURN + LTV SCHEDULER STARTED")
    print("=" * 70)

    print(
        "Interval: 5 minutes"
    )

    print(
        "Press CTRL+C to stop the scheduler."
    )


    while True:

        run_scheduled_pipeline()


        print()
        print("-" * 70)

        print(
            "Pipeline run completed."
        )

        print(
            "Next run in 5 minutes."
        )

        print(
            "Waiting..."
        )

        print("-" * 70)


        try:

            time.sleep(
                INTERVAL_SECONDS
            )

        except KeyboardInterrupt:

            print()
            print(
                "Scheduler stopped by user."
            )

            break


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:

        start_scheduler()

    except KeyboardInterrupt:

        print(
            "Scheduler stopped."
        )

    except Exception:

        print(
            "SCHEDULER FAILED TO START"
        )

        traceback.print_exc()