import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "workflow.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Create relational tables: departments & tasks
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workflows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            assignee TEXT NOT NULL,
            priority TEXT CHECK(priority IN ('Low', 'Medium', 'High', 'Critical')) NOT NULL,
            status TEXT CHECK(status IN ('Pending', 'In Progress', 'Completed')) NOT NULL DEFAULT 'Pending',
            department_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (department_id) REFERENCES departments(id)
        )
    """)

    # Seed default departments if empty
    cursor.execute("SELECT COUNT(*) FROM departments")
    if cursor.fetchone()[0] == 0:
        depts = [("IT Operations",), ("Cybersecurity & SOC",), ("Network Engineering",), ("Software Dev",)]
        cursor.executemany("INSERT INTO departments (name) VALUES (?)", depts)

    # Seed sample business workflows if empty
    cursor.execute("SELECT COUNT(*) FROM workflows")
    if cursor.fetchone()[0] == 0:
        sample_tasks = [
            ("Provision Active Directory Accounts for Q4 Hires", "Jaffar Ali", "High", "Completed", 1),
            ("Deploy CIS-Hardened Docker Containers to Staging", "Jaffar Ali", "Critical", "In Progress", 2),
            ("Configure Site-to-Site IPsec VPN Failover Tunnel", "Marco Rossi", "High", "Pending", 3),
            ("Audit REST API Rate Limiting & JWT Authentication", "Elena Bianchi", "Medium", "In Progress", 4),
        ]
        cursor.executemany(
            "INSERT INTO workflows (title, assignee, priority, status, department_id) VALUES (?, ?, ?, ?, ?)",
            sample_tasks
        )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print(f"[+] Relational database initialized at {DB_PATH}")
