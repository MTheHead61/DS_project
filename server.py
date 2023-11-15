import socket
import threading
import json
import datetime
import route
from random import uniform


class Server:
    def __init__(self, host, port, interval=60):  # Set a default interval of 60 seconds
        self.host = host
        self.port = port
        self.node_count = 0
        self.nodes = {}  # Dictionary to store node_id: node_ip pairs
        self.jobs = []
        self.interval = interval
        self.timer = None
        self.lock = threading.Lock()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)

    def handle_client(self, client_socket, address):
        data = client_socket.recv(1024).decode('utf-8')
        message = json.loads(data)

        if message.get("type") == "INITIALIZE":
            with self.lock:
                if address[0] not in self.nodes.values():
                    self.node_count += 1
                    node_id = self.node_count
                    self.nodes[node_id] = {"ip": address[0], "active": True}

                    response = {"type": "INITIALIZE_RESPONSE", "id": node_id, "nodes": self.nodes}
                    client_socket.send(json.dumps(response).encode('utf-8'))
                else:
                    response = {"type": "ERROR", "message": "Node already initialized."}
                    client_socket.send(json.dumps(response).encode('utf-8'))

        elif message.get("type") == "JOB_REQUEST":
            pass

        elif message.get("type") == "TAKE_JOB":
            with self.lock:
                node_id = message.get("node_id")
                if node_id in self.nodes:
                    response = {"type": "JOB_ACK"}
                    client_socket.send(json.dumps(response).encode('utf-8'))

        client_socket.close()

    def send_job_request(self, job):
        with self.lock:
            for node_id, node_info in self.nodes.items():
                if node_info["active"]:
                    self.send_job(node_info["ip"], job)

    def send_job(self, target_ip, job):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                client_socket.connect((target_ip, self.port))
                message = {"type": "JOB", "job": json.dumps(job, cls=route.JobEncoder)}
                client_socket.send(json.dumps(message).encode('utf-8'))
            except ConnectionRefusedError:
                # Handle connection error
                pass

    def start_job_timer(self):
        self.timer = threading.Timer(self.interval, self.send_dummy_job)
        self.timer.start()

    def stop_job_timer(self):
        if self.timer:
            self.timer.cancel()

    def send_dummy_job(self):
        with self.lock:
            d = datetime.datetime.now()
            job = route.Job(route.Stop(uniform(38.12, 38.26), uniform(15.49, 15.65), True, d, 1, uniform(0, 10000)),
                            route.Stop(uniform(38.12, 38.26), uniform(15.49, 15.65), False, d, 1, uniform(0, 10000)))
            self.send_job_request(job)
        self.start_job_timer()  # Schedule the next job after the predefined interval

    def start(self):
        self.start_job_timer()  # Start the job timer
        while True:
            client_socket, address = self.server_socket.accept()
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket, address))
            client_handler.start()


server = Server('127.0.0.1', 8080)
server.start()
