from app.ml.train_rf import train

def run_training():
    print("🧠 Training model...")
    train()
    print("✅ Model training complete")

if __name__ == "__main__":
    run_training()