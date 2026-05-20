import time
from app.jobs.generate_data import run_batch
from app.jobs.train_model import run_training

def run_pipeline():
    while True:
        print("\n🔥 STARTING PIPELINE")

        # 1. Generate data
        run_batch(n=20)

        # 2. Train model
        run_training()

        print("😴 Sleeping for 1 hour...\n")
        time.sleep(3600)  # 1 hour

if __name__ == "__main__":
    run_pipeline()