# Student Name: Sujan Rathnakumar
# Student ID: 100893497
# Module: TPRG 2131 Fall 2024 Project 1
# Date: November 17, 2024
# This program is strictly my own work. Any material
# beyond course learning materials that is taken from
# the Web or other sources is properly cited, giving
# credit to the original author(s).

import os
import time
import socket
import json
import PySimpleGUI as sg

# Server configuration
HOST_ADDRESS = "127.0.0.1"  # Localhost
SERVER_PORT = 12345

# Function to initialize the server socket
def initialize_server():
    try:
        server = socket.socket()
        server.bind((HOST_ADDRESS, SERVER_PORT))
        server.listen(1)
        print(f"Server is live at {HOST_ADDRESS}:{SERVER_PORT}")
        return server
    except Exception as e:
        print(f"Error initializing server: {e}")
        raise

# Function to set up the GUI
def setup_gui():
    layout = [
        [sg.Text("Waiting for data...", size=(30, 1), key=f"Data_{i}", font=("Arial", 12))] for i in range(6)
    ]
    layout.append([
        sg.Button("Close", font=("Arial", 12))
    ])
    return sg.Window("Server Viewer", layout, finalize=True)

# Main server logic
def start_server():
    server = None
    conn = None
    window = None

    try:
        # Initialize server socket
        server = initialize_server()
        
        # Accept a client connection
        conn, client_address = server.accept()
        print(f"Connected to client at {client_address}")

        # Set up the GUI window
        window = setup_gui()

        while True:
            # Check for GUI events
            event, _ = window.read(timeout=100)
            if event == "Close" or event == sg.WINDOW_CLOSED:
                print("Server GUI closed by user.")
                break

            # Receive data from the client
            try:
                data = conn.recv(1024)
                if not data:
                    print("No data received. Closing connection.")
                    break

                # Decode and parse the JSON data
                parsed_data = json.loads(data.decode('utf-8'))
                for idx, (key, value) in enumerate(parsed_data.items()):
                    if idx < 6:
                        window[f"Data_{idx}"].update(f"{key}: {value}")

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON data: {e}")
            except Exception as e:
                print(f"Error receiving data: {e}")

    except Exception as e:
        print(f"Server encountered an error: {e}")

    finally:
        # Clean up resources
        if conn:
            try:
                conn.close()
                print("Connection to client closed.")
            except Exception as e:
                print(f"Error closing connection: {e}")
        if server:
            try:
                server.close()
                print("Server shut down.")
            except Exception as e:
                print(f"Error shutting down server: {e}")
        if window:
            window.close()

if __name__ == "__main__":
    start_server()
