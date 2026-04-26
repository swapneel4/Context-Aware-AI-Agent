from datetime import datetime, timedelta

# -----------------------------
# 🧠 Helper: format rows
# -----------------------------
def _format_tasks(rows):
    return [
        {
            "id": row[0],
            "task": row[1],
            "deadline": row[2],
            "created_at": row[3]
        }
        for row in rows
    ]


# -----------------------------
# ➕ CREATE TASK
# -----------------------------
def create_task(conn, task: str, deadline: str | None):
    if not task:
        return {"status": "error", "message": "Task cannot be empty"}

    cursor = conn.cursor()

    now = datetime.utcnow()
    delete_after = now + timedelta(days=7)

    cursor.execute(
    """
    INSERT INTO tasks (task, deadline, created_at, delete_after)
    VALUES (?, ?, ?, ?)
    """,
    (
        task,
        deadline,
        now.strftime("%Y-%m-%d %H:%M:%S"),
        delete_after.strftime("%Y-%m-%d %H:%M:%S")
    )
)

    conn.commit()

    return {
        "status": "success",
        "message": "Task created",
        "task": task,
        "deadline": deadline
    }


# -----------------------------
# 📖 GET TASKS
# -----------------------------
def get_tasks(conn):
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, task, deadline, created_at
        FROM tasks
        ORDER BY 
            CASE 
                WHEN deadline IS NULL THEN 1 
                ELSE 0 
            END,
            deadline ASC
        """
    )

    rows = cursor.fetchall()

    tasks = _format_tasks(rows)

    if not tasks:
        return {
            "status": "success",
            "tasks": [],
            "message": "No tasks found"
        }

    return {
        "status": "success",
        "tasks": tasks
    }


# -----------------------------
# ✏️ UPDATE TASK
# -----------------------------
def update_task(conn, task_id: int | None, task: str | None = None, deadline: str | None = None):
    if not task_id:
        return {"status": "error", "message": "Task ID required"}

    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, deadline FROM tasks WHERE id = ?",
        (task_id,)
    )
    row = cursor.fetchone()

    if not row:
        return {"status": "error", "message": "Task not found"}

    old_deadline = row[1]

    # update logic
    if task and deadline:
        cursor.execute(
            "UPDATE tasks SET task = ?, deadline = ? WHERE id = ?",
            (task, deadline, task_id)
        )
    elif task:
        cursor.execute(
            "UPDATE tasks SET task = ? WHERE id = ?",
            (task, task_id)
        )
    elif deadline:
        cursor.execute(
            "UPDATE tasks SET deadline = ? WHERE id = ?",
            (deadline, task_id)
        )
    else:
        return {"status": "error", "message": "Nothing to update"}

    conn.commit()

    return {
        "status": "success",
        "task_id": task_id,
        "old_deadline": old_deadline,
        "new_deadline": deadline
    }


# -----------------------------
# ❌ DELETE TASK
# -----------------------------
def delete_task(conn, task_id: int | None):
    if not task_id:
        return {"status": "error", "message": "Task ID required"}

    cursor = conn.cursor()

    # check if exists
    cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
    if not cursor.fetchone():
        return {"status": "error", "message": "Task not found"}

    cursor.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    conn.commit()

    return {
        "status": "success",
        "message": "Task deleted",
        "task_id": task_id
    }