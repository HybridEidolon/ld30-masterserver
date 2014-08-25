from flask import Flask, jsonify, request, abort
from datetime import datetime

app = Flask(__name__)

internal_servers = []


@app.route('/list')
def list_servers():
    now = datetime.now()
    for s in internal_servers:
        diff = now - s['last_heartbeat']
        if diff.total_seconds() > 5:
            internal_servers.remove(s)
            print('Removed ' + s['url'] + ' for heartbeat timeout')
    return jsonify(servers=internal_servers)


@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    name = request.form['name']
    if name is None:
        return abort(404)
    ip = request.remote_addr
    time = datetime.now()
    server_entry = {'name': name, 'url': ip, 'last_heartbeat': time}
    found_existing = False
    for s in internal_servers:
        if s['url'] == ip:
            s['last_heartbeat'] = time
            found_existing = True
    if not found_existing:
        print('Added server ' + ip + ' to log')
        internal_servers.append(server_entry)
    return jsonify(server_entry)


@app.route('/remove', methods=['POST'])
def remove():
    for s in internal_servers:
        if s['url'] == request.remote_addr:
            internal_servers.remove(s)
            return jsonify(success=True)
    return jsonify(success=False), 404
