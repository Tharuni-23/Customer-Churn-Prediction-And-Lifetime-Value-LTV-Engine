import time
import traceback
from datetime import datetime

from main import run_pipeline


INTERVAL_SECONDS = 5 * 60


def start_scheduler():

    print("=" * 70)
    print("CHURN + LTV SCHEDULER STARTED")
    print("=" * 70)

    while True:

        run_started = datetime.now()

        print("\n")
        print("=" * 70)
        print("SCHEDULED RUN")
        print("=" * 70)
        print("Started:", run_started)

        try:
            run_pipeline()

            print("\nPipeline run finished successfully.")

        except Exception as e:

            print("\nPIPELINE FAILED")
            print("Error:", e)

            traceback.print_exc()

        print("\nNext run will start in 5 minutes.")

        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    start_scheduler()