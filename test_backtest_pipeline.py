import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_full_pipeline():
    print("=== Testing Backtest Pipeline ===")
    
    # 1. Trigger backtest
    res = client.get("/run-backtest?symbol=AAPL")
    print(f"Trigger backtest status: {res.status_code}")
    data = res.json()
    print("Response:", data)
    assert res.status_code == 200
    assert data.get("status") == "started"
    run_id = data.get("run_id")
    assert run_id is not None
    print(f"Started Run ID: {run_id}")

    # 2. Poll run-status
    max_wait = 45 # seconds
    start = time.time()
    final_status = None
    while time.time() - start < max_wait:
        time.sleep(2)
        s_res = client.get(f"/run-status/{run_id}")
        assert s_res.status_code == 200
        status_info = s_res.json()
        status = status_info.get("status")
        print(f"Elapsed {int(time.time() - start)}s -> Status: {status}")
        if status in ("completed", "failed"):
            final_status = status_info
            break

    assert final_status is not None, "Timed out waiting for backtest run to finish"
    print("\nFinal run status payload:")
    print(final_status)
    assert final_status["status"] == "completed", f"Backtest failed: {final_status}"
    assert final_status["metrics"] is not None
    print(f"ML Score: {final_status['metrics'].get('ml_score')}")
    print(f"Sharpe: {final_status['metrics'].get('sharpe')}")
    print(f"Return: {final_status['metrics'].get('return_pct')}%")

    # 3. Test Equity Points
    eq_res = client.get(f"/equity/{run_id}")
    assert eq_res.status_code == 200
    points = eq_res.json()
    print(f"\nEquity curve points retrieved: {len(points)}")
    assert len(points) > 0, "No equity points recorded!"
    print(f"First equity point: {points[0]}")
    print(f"Last equity point: {points[-1]}")
    assert "timestamp" in points[0]
    assert "equity" in points[0]
    assert isinstance(points[0]["equity"], (int, float))

    print("\n[SUCCESS] ALL BACKTEST AND EQUITY PIPELINE TESTS PASSED!")

if __name__ == "__main__":
    test_full_pipeline()
