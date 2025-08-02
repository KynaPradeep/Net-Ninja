from flask import Flask, jsonify, send_from_directory
import socket
import psutil

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "Flask is running!"})

@app.route('/network', methods=['GET'])
def network_info():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        net_io = psutil.net_io_counters()
        interfaces = psutil.net_if_addrs()

        return jsonify({
            "hostname": hostname,
            "local_ip": local_ip,
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "interfaces": list(interfaces.keys())
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stats', methods=['GET'])
def system_stats():
    try:
        return jsonify({
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": psutil.virtual_memory()._asdict(),
            "disk": psutil.disk_usage('/')._asdict()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/dashboard')
def serve_dashboard():
    return send_from_directory('.', 'dashboard.html')

import time

@app.route('/interfaces', methods=['GET'])
def get_interfaces():
    try:
        interfaces = psutil.net_if_addrs()
        interface_info = {}
        for name, addrs in interfaces.items():
            interface_info[name] = [{'family': str(addr.family), 'address': addr.address} for addr in addrs]
        return jsonify(interface_info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/uptime', methods=['GET'])
def get_uptime():
    try:
        boot_time = psutil.boot_time()
        uptime = time.time() - boot_time
        return jsonify({"uptime_seconds": int(uptime)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/connections', methods=['GET'])
def get_connections():
    try:
        conns = psutil.net_connections()
        connections = [{
            "fd": c.fd,
            "family": str(c.family),
            "type": str(c.type),
            "laddr": c.laddr.ip + ":" + str(c.laddr.port) if c.laddr else None,
            "raddr": c.raddr.ip + ":" + str(c.raddr.port) if c.raddr else None,
            "status": c.status
        } for c in conns if c.laddr]
        return jsonify(connections)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/processes', methods=['GET'])
def get_processes():
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
            processes.append(proc.info)
        top = sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:5]
        return jsonify(top)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ports', methods=['GET'])
def get_ports():
    try:
        conns = psutil.net_connections()
        listening_ports = list({c.laddr.port for c in conns if c.status == 'LISTEN'})
        return jsonify({"listening_ports": listening_ports})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
s