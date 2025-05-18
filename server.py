import socket
import threading
import queue
import json
from typing import Optional

from common import send_message, receive_message

import requests
import glob

class JSONServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.message_queue = queue.Queue()
        self.running = False
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def __del__(self):
        self.stop()
        self.server_socket.close()

    def start(self):
        """Запускает сервер и потоки обработки."""
        self.running = True

        threading.Thread(target=self._process_messages, daemon=True).start()


        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server listening on {self.host}:{self.port}")

        while self.running:
            try:
                client_sock, addr = self.server_socket.accept()
                threading.Thread(target=self._handle_client, args=(client_sock, addr)).start()
            except Exception as e:
                if self.running:
                    print(f"Server error: {e}")

    def _handle_client(self, client_sock, addr):
        """Обрабатывает одного клиента."""
        try:
            data = receive_message(client_sock)
            self.message_queue.put([client_sock,data])
            print(f"Received data from {addr}")
        except Exception as e:
            print(f"Error with {addr}: {e}")



    def _process_messages(self):
        while self.running:
            client_sock = None
            try:
                [client_sock, msg] = self.message_queue.get(timeout=0.1)

                #print(f"received prompt: {msg}")

                response_text = self._get_model_response(msg)

                send_message(client_sock, response_text)

                self.message_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                if self.running:
                    print(f"Server error: {e}")
            finally:
                if client_sock is not None:
                    client_sock.close()

    def _get_model_response(self, prompt):
        """Оптимизированный запрос к модели с потоковой обработкой"""
        try:
            print(f" receiver prompt {prompt}")

            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'deep-seek7b-big-ctx',
                    'prompt': prompt,
                    'stream': False,
                    'temperature': 0.3,  # Контроль креативности ответа
                    'max_tokens': 20000  # Максимальное количество токенов в ответе

                }

            )
            print(f" response from model {response}")
            if response.status_code == 200:
                response_text = response.json().get('response', 'Нет ответа')
            else:
                response_text = f"Ошибка API: {response.status_code}"

            return ''.join(response_text)

        except Exception as e:
            return f"Ошибка генерации: {str(e)}"

    def stop(self):
        """Останавливает сервер."""
        self.running = False


if __name__ == '__main__':
    #server = JSONServer('localhost', 9999)
    server = JSONServer('0.0.0.0', 9999)
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
        print("Server stopped.")
