from flask import Flask, render_template, jsonify
import threading, random, time
from collections import defaultdict

app = Flask(__name__)
packets = []
connections = defaultdict(int)
traffic_running = False

def generate_demo_traffic():
    global traffic_running
    protocols = ['TCP', 'UDP', 'ICMP', 'ARP']
    ips = ['192.168.1.', '10.0.0.', '172.16.0.', '8.8.8.']
    
    traffic_running = True
    while traffic_running:
        src_base = random.choice(ips)
        dst_base = random.choice(ips)
        src = f"{src_base}{random.randint(10,250)}"
        dst = f"{dst_base}{random.randint(10,250)}"
        
        proto = random.choice(protocols)
        connections[f"{src}→{dst}"] += 1
        
        packets.append({
            'time': time.strftime('%H:%M:%S'),
            'src': src, 
            'dst': dst, 
            'proto': proto,
            'len': random.randint(64, 1500)
             })
        
        if len(packets) > 100: 
            packets.pop(0)
        time.sleep(0.8)

# AUTO-START traffic when server starts
threading.Thread(target=generate_demo_traffic, daemon=True).start()

@app.route('/')
def dashboard():
    return render_template('dashboard.html', 
                         packets=packets[-20:], 
                         connections=dict(sorted(connections.items(), 
                                               key=lambda x: x[1], reverse=True)[:10]))

@app.route('/start')
def start_capture():
    global traffic_running
    if not traffic_running:
        threading.Thread(target=generate_demo_traffic, daemon=True).start()
        traffic_running = True
    return jsonify({"status": " Demo traffic running! Refresh page..."})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

