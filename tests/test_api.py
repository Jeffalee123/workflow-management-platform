import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app import app

def run_tests():
    client = app.test_client()

    # 1. Test GET /api/workflows
    res = client.get("/api/workflows")
    assert res.status_code == 200
    print(f"[PASS] GET /api/workflows -> Returned {len(res.get_json())} workflow records")

    # 2. Test POST /api/workflows
    res = client.post("/api/workflows", json={
        "title": "Automated CI/CD Pipeline Verification",
        "assignee": "Jaffar Ali",
        "priority": "High",
        "department_id": 4
    })
    assert res.status_code == 201
    new_id = res.get_json()["id"]
    print(f"[PASS] POST /api/workflows -> Created workflow #{new_id}")

    # 3. Test PATCH /api/workflows/<id>/status
    res = client.patch(f"/api/workflows/{new_id}/status", json={"status": "Completed"})
    assert res.status_code == 200
    print(f"[PASS] PATCH /api/workflows/{new_id}/status -> Updated status to Completed")

    # 4. Test GET /api/stats
    res = client.get("/api/stats")
    assert res.status_code == 200
    print(f"[PASS] GET /api/stats -> {res.get_json()}")

    # 5. Clean up test entry
    res = client.delete(f"/api/workflows/{new_id}")
    assert res.status_code == 200
    print(f"[PASS] DELETE /api/workflows/{new_id} -> Cleaned up test record")

if __name__ == "__main__":
    run_tests()
