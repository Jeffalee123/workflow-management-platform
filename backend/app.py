import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from database import get_connection, init_db

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app = Flask(__name__, static_folder=FRONTEND_DIR)
CORS(app)

init_db()

@app.route("/")
def serve_dashboard():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/api/workflows", methods=["GET"])
def get_workflows():
    conn = get_connection()
    rows = conn.execute("""
        SELECT w.id, w.title, w.assignee, w.priority, w.status, w.created_at, d.name AS department
        FROM workflows w
        LEFT JOIN departments d ON w.department_id = d.id
        ORDER BY w.id DESC
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/workflows", methods=["POST"])
def create_workflow():
    data = request.get_json()
    if not data or not data.get("title") or not data.get("assignee"):
        return jsonify({"error": "Title and assignee are required"}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO workflows (title, assignee, priority, status, department_id) VALUES (?, ?, ?, ?, ?)",
        (
            data["title"],
            data["assignee"],
            data.get("priority", "Medium"),
            data.get("status", "Pending"),
            data.get("department_id", 1),
        )
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": new_id, "message": "Workflow task created"}), 201

@app.route("/api/workflows/<int:workflow_id>/status", methods=["PATCH"])
def update_status(workflow_id):
    data = request.get_json()
    new_status = data.get("status")
    if new_status not in ("Pending", "In Progress", "Completed"):
        return jsonify({"error": "Invalid status"}), 400

    conn = get_connection()
    conn.execute("UPDATE workflows SET status = ? WHERE id = ?", (new_status, workflow_id))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Workflow #{workflow_id} updated to {new_status}"})

@app.route("/api/workflows/<int:workflow_id>", methods=["DELETE"])
def delete_workflow(workflow_id):
    conn = get_connection()
    conn.execute("DELETE FROM workflows WHERE id = ?", (workflow_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Workflow #{workflow_id} deleted"})

@app.route("/api/stats", methods=["GET"])
def get_stats():
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM workflows").fetchone()[0]
    completed = conn.execute("SELECT COUNT(*) FROM workflows WHERE status = 'Completed'").fetchone()[0]
    in_progress = conn.execute("SELECT COUNT(*) FROM workflows WHERE status = 'In Progress'").fetchone()[0]
    pending = conn.execute("SELECT COUNT(*) FROM workflows WHERE status = 'Pending'").fetchone()[0]
    conn.close()
    return jsonify({
        "total": total,
        "completed": completed,
        "in_progress": in_progress,
        "pending": pending
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
