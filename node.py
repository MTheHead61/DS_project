import socket
import threading
import json
import time
import route


class Node:
    def __init__(self, server_host, server_port, truck, calculator):
        self.server_host = server_host
        self.server_port = server_port
        self.node_id = None
        self.nodes_list = {}
        self.is_active = True
        self.shutdown_flag = False  # Flag to indicate a graceful shutdown
        self.wave_id = None
        self.wave_weight = None
        self.counter = 0
        self.lock = threading.Lock()
        self.truck = truck
        self.calculator = calculator

    def send_message(self, target_ip, message_type, payload=None):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                client_socket.connect((target_ip, self.server_port))
                message = {"type": message_type, "payload": payload, "sender_id": self.node_id,
                           "sender_ip": self.server_host}
                client_socket.send(json.dumps(message).encode('utf-8'))
            except ConnectionRefusedError:
                self.is_active = False

    def handle_initialize_response(self, response):
        with self.lock:
            self.node_id = response["id"]
            self.nodes_list.update(response["nodes"])

    def handle_greeting(self, message):
        with self.lock:
            sender_id = message["sender_id"]
            sender_ip = message["sender_ip"]
            self.nodes_list[sender_id] = {"ip": sender_ip, "active": False}
            self.send_message(sender_ip, "GREETING_RESPONSE")

    def handle_greeting_response(self, response):
        with self.lock:
            sender_id = response["sender_id"]
            self.nodes_list[sender_id]["active"] = True

    def handle_job(self, message):
        with self.lock:
            job = json.load(message['job'], cls=route.JobDecoder)
            print(type(job))
            '''result = self.calculator.shortest_deviation(self.truck.get_route_list(), self.truck.get_path())
            self.wave(result["distance"])'''

    def wave(self, wave_weight):
        with self.lock:
            # Initialization phase
            self.counter = 0
            self.wave_id = self.node_id
            self.wave_weight = wave_weight

            # Main phase
            for node_id, node_info in self.nodes_list.items():
                if self.node_id != node_id and node_info["active"]:
                    message = {"type": "WAVE", "wave_id": self.wave_id, "wave_weight": self.wave_weight}
                    self.send_message(node_info["ip"], "WAVE", message)

    def handle_wave(self, message):
        with self.lock:
            wave_id = message["wave_id"]
            wave_weight = message["wave_weight"]

            if wave_id == self.node_id:
                # Discard the message and increment the counter
                self.counter += 1
            elif wave_id == self.wave_id:
                # Discard the message
                pass
            elif wave_weight > self.wave_weight:
                # Discard the message
                pass
            elif wave_weight < self.wave_weight:
                # Change wave_id and wave_weight, forward the message to all other nodes, and exit the algorithm
                self.wave_id = wave_id
                self.wave_weight = wave_weight

                for node_id, node_info in self.nodes_list.items():
                    if self.node_id != node_id and node_info["active"]:
                        self.send_message(node_info["ip"], "WAVE", message)

                return

            if self.counter == len(self.nodes_list) - 1:
                # The node has reached the counter value, take the job (further action described)
                self.take_job()

    def take_job(self):
        with self.lock:
            print(f"Node {self.node_id} is taking the job")
            self.send_message(self.server_host, "TAKE_JOB", {"node_id": self.node_id})

    def handle_message(self, client_socket):
        data = client_socket.recv(1024).decode('utf-8')
        message = json.loads(data)
        message_type = message.get("type")

        handlers = {
            "INITIALIZE_RESPONSE": self.handle_initialize_response,
            "GREETING": self.handle_greeting,
            "GREETING_RESPONSE": self.handle_greeting_response,
            "JOB": self.handle_job,
            "WAVE": self.handle_wave,
            # Add more message types and corresponding handlers as needed
        }

        if message_type in handlers:
            handlers[message_type](message)

    def start(self):
        initialize_thread = threading.Thread(target=self.initialize)
        initialize_thread.start()
        initialize_thread.join()

        greetings_thread = threading.Thread(target=self.greetings)
        greetings_thread.start()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(('0.0.0.0', 0))
            server_socket.listen(5)
            while not self.shutdown_flag:
                client_socket, _ = server_socket.accept()
                message_handler = threading.Thread(target=self.handle_message, args=(client_socket,))
                message_handler.start()

    def initialize(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.server_host, self.server_port))
            message = {"type": "INITIALIZE"}
            client_socket.send(json.dumps(message).encode('utf-8'))
            data = client_socket.recv(1024).decode('utf-8')
            response = json.loads(data)

            if response.get("type") == "INITIALIZE_RESPONSE":
                self.handle_initialize_response(response)

    def greetings(self):
        for node_id, node_info in self.nodes_list.items():
            if node_id != self.node_id and self.is_active:
                self.send_message(node_info["ip"], "GREETING")
                time.sleep(2)  # Adjust the timeout as needed
                with self.lock:
                    if not node_info.get("active"):
                        node_info["active"] = False

    def shutdown(self):
        self.shutdown_flag = True

# Example usage:
# node = Node('127.0.0.1', 8080)
# node.start()
# # To shutdown the node gracefully:
# node.shutdown()
