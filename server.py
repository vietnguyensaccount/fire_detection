import sys

from flask import Flask, render_template, request, redirect, session, url_for, send_from_directory
import json, os, subprocess

app = Flask(__name__)
app.secret_key = "fire_web_admin"

users_file = "users.json"
cams_file = "camera_config.json"
detections_file = "detections.json"
processes = {}

# === Utilities ===
def load_users():
    return json.load(open(users_file)) if os.path.exists(users_file) else {}

def save_users(users):
    with open(users_file, 'w') as f:
        json.dump(users, f, indent=2)

def load_cams():
    return json.load(open(cams_file)) if os.path.exists(cams_file) else {"cameras": []}

def save_cams(data):
    with open(cams_file, 'w') as f:
        json.dump(data, f, indent=2)

def find_cam(cid):
    cams = load_cams()
    for cam in cams["cameras"]:
        if cam["id"] == cid:
            return cam
    return None

# === Routes ===
@app.route('/')
def index():
    if 'admin' not in session:
        return redirect(url_for('login'))
    cams = load_cams()
    detections = json.load(open(detections_file)) if os.path.exists(detections_file) else []
    return render_template("dashboard.html", cameras=cams["cameras"], detections=detections)

@app.route('/events')
def events():
    if 'admin' not in session:
        return redirect(url_for('login'))
    detections = json.load(open(detections_file)) if os.path.exists(detections_file) else []
    return render_template("events.html", detections=detections)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username']
        session['username'] = username
        if users.get(username) == request.form['password']:
            session['admin'] = True
            return redirect('/')
        else:
            return render_template("login.html", error="Invalid credentials.")
    return render_template("login.html", error=None)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/login')

# === Camera Management ===
@app.route('/camera/', methods=['GET', 'POST'])
def camera():
    cams = load_cams()
    return render_template('camera.html',cameras=cams["cameras"])

@app.route('/camera/add', methods=['GET', 'POST'])
def camera_add():
    if request.method == 'POST':
        cams = load_cams()
        new_id = str(len(cams["cameras"]) + 1)  # Auto ID
        new_cam = {
            "id": new_id,
            "rtsp": request.form['rtsp'],
            "status": "stopped"
        }
        cams["cameras"].append(new_cam)
        save_cams(cams)
        return render_template("camera.html",cameras=cams["cameras"])
    return render_template("camera_add.html")

@app.route('/camera/<cid>/edit', methods=['GET', 'POST'])
def camera_edit(cid):
    cams = load_cams()
    cam = find_cam(cid)
    if not cam:
        return redirect('/')
    if request.method == 'POST':
        cam["name"] = request.form['name']
        cam["rtsp"] = request.form['rtsp']
        save_cams(cams)
        return redirect('/')
    return render_template("camera_edit.html", cam=cam)

@app.route('/camera/<cid>/delete', methods=['GET', 'POST'])
def delete_cam(cid):
    cams = load_cams()
    cam = find_cam(cid)
    if request.method == 'POST':
        cams["cameras"] = [c for c in cams["cameras"] if c["id"] != cid]
        save_cams(cams)
        return redirect('/camera')
    return render_template("camera_delete.html", cam=cam)


# === AI Start/Stop ===
@app.route('/camera/<cid>/start')
def camera_start(cid):
    cams = load_cams()
    cam = find_cam(cid)
    if cam and cam["status"] != "running":
        p = subprocess.Popen(['python', 'ai_worker.py', cam["rtsp"], cid])
        processes[cid] = p
        cam["status"] = "running"
        save_cams(cams)
    return redirect('/')

@app.route('/camera/<cid>/stop')
def camera_stop(cid):
    cams = load_cams()
    if cid in processes:
        processes[cid].terminate()
        del processes[cid]
    cam = find_cam(cid)
    if cam:
        cam["status"] = "stopped"
        save_cams(cams)
    return redirect('/')

# === Serve Thumbnails ===
@app.route('/thumbnails/<filename>')
def thumbnails(filename):
    return send_from_directory('thumbnails', filename)

if __name__ == '__main__':
    app.run(debug=True, port=8000)