from flask import Flask, render_template, request, redirect, url_for, jsonify
import db
import logging
from datetime import datetime
import pytz
from flask import request

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

db.init_db()

def get_user_ip():
    return request.headers.get("X-Forwarded-For", request.remote_addr)


def get_current_ist_time():
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")


@app.route("/")
def home():
    return redirect(url_for("tasks"))

@app.route("/tasks")
def tasks():

    user_ip = get_user_ip()
    current_time = get_current_ist_time()
    print("-----------------------------------------------------------------------------------------")
    logging.info("Tasks page accessed | User IP: %s | Time (IST): %s", user_ip, current_time)
    print("-----------------------------------------------------------------------------------------")
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    conn.close()

    return render_template("tasks/list.html", tasks=tasks)


@app.route("/tasks/add")
def add_task():
    return render_template("tasks/add.html")

@app.route("/tasks/create", methods=["POST"])
def create_task():
    try:
        title = request.form["title"]
        description = request.form.get("description")

        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, description) VALUES (?, ?)",
            (title, description)
        )
        conn.commit()
        conn.close()

        user_ip = get_user_ip()
        current_time = get_current_ist_time()
        print("------------------------------------------------------------------------------------------------------------------------------")
        logging.info(
            "Task created from UI | Title: '%s' | Description: '%s' | Time (IST): %s | User IP: %s",
            title,
            description,
            current_time,
            user_ip
        )
        print("------------------------------------------------------------------------------------------------------------------------------")
        return redirect(url_for("tasks"))

    except Exception as e:
        logging.error(str(e))
        return "Error creating task", 500




@app.route("/tasks/delete/<int:task_id>")
def delete_task_ui(task_id):
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()

        logging.info("Task deleted from UI: %s", task_id)
        return redirect(url_for("tasks"))

    except Exception as e:
        logging.error(str(e))
        return "Error deleting task", 500



@app.route("/tasks/edit/<int:task_id>")
def edit_task(task_id):
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    conn.close()
    return render_template("tasks/edit.html", task=task)


@app.route("/tasks/update/<int:task_id>", methods=["POST"])
def update_task_ui(task_id):
    title = request.form["title"]
    description = request.form.get("description")
    status = request.form.get("status")

    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tasks
        SET title = ?, description = ?, status = ?
        WHERE id = ?
    """, (title, description, status, task_id))
    conn.commit()
    conn.close()

    return redirect(url_for("tasks"))


#API endpoints Testing 

@app.route("/api/tasks", methods=["GET"])
def api_get_tasks():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    conn.close()
    return jsonify(tasks), 200

@app.route("/api/tasks", methods=["POST"])
def api_create_task():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description", "")

    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, description) VALUES (?, ?)", (title, description))
    conn.commit()
    conn.close()

    return jsonify({"title": title, "description": description}), 201


if __name__ == "__main__":
    app.run(debug=True)
