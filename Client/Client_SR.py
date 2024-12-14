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

# Client configuration constants
SERVER_ADDRESS = "127.0.0.1"  # Server IP address (localhost for testing)
SERVER_PORT = 12345            # Port number to connect to the server
DATA_INTERVAL = 2              # Interval in seconds between data transmissions
MAX_ITERATIONS = 50            # Maximum number of iterations to send data

# Function to collect system data
# This function retrieves various system metrics from the Raspberry Pi.
def collect_system_data(iteration):
    try:
        # Collect CPU temperature
        temp = os.popen('vcgencmd measure_temp').readline().strip()
        temp = float(temp.split('=')[1].split("'")[0])
        
        # Collect throttling status
        throttled = os.popen('vcgencmd get_throttled').readline().strip()
        throttled = throttled.split('=')[1] if '=' in throttled else "Unknown"
        
        # Collect ARM clock speed
        clock_speed = os.popen('vcgencmd measure_clock arm').readline().strip()
        clock_speed = float(clock_speed.split('=')[1]) if '=' in clock_speed else 0.0
        
        # Collect GPU temperature
        gpu_temp = os.popen('vcgencmd measure_temp gpu').readline().strip()
        gpu_temp = float(gpu_temp.split('=')[1].split("'")[0]) if '=' in gpu_temp else 0.0
        
        # Collect core voltage
        core_voltage = os.popen('vcgencmd measure_volts core').readline().strip()
        core_voltage = float(core_voltage.split('=')[1].split('V')[0]) if '=' in core_voltage else 0.0

        # Return the collected data as a dictionary
        return {
            "Temperature": round(temp, 1),
            "Throttle State": throttled,
            "Clock Speed": round(clock_speed, 1),
            "GPU Temperature": round(gpu_temp, 1),
            "Core Voltage": round(core_voltage, 1),
            "Iteration": iteration
        }

    except Exception as e:
        # Handle and log any errors encountered during data collection
        print(f"Error gathering system data: {e}")
        return {}

# Function to initialize and connect the client socket
# This function sets up a connection to the server.
def connect_to_server():
    try:
        client = socket.socket()  # Create a TCP socket
        client.connect((SERVER_ADDRESS, SERVER_PORT))  # Connect to the server
        print(f"Connected to server at {SERVER_ADDRESS}:{SERVER_PORT}")
        return client
    except Exception as e:
        print(f"Failed to connect to server: {e}")
        raise

# Main client logic
# This function orchestrates the connection, data collection, and transmission.
def main():
    # Check if the script is running on a compatible platform (Raspberry Pi)
    if os.name != 'posix':
        print("This script is only for Raspberry Pi. Exiting.")
        return

    client_socket = None
    window = None

    try:
        # Establish connection to the server
        client_socket = connect_to_server()

        # Define the GUI layout for the client
        layout = [
            [sg.Text("Connected to server", text_color="green", font=("Arial", 14))],
            [sg.Button("Exit", font=("Arial", 12))]
        ]
        window = sg.Window("Client Connection", layout, finalize=True)

        # Loop for data collection and transmission
        for i in range(1, MAX_ITERATIONS + 1):
            data = collect_system_data(i)  # Collect system data
            if data:
                # Send the data to the server in JSON format
                try:
                    client_socket.sendall(json.dumps(data).encode('utf-8'))
                except Exception as e:
                    print(f"Error sending data to server: {e}")
                    break

            # Check for GUI events (e.g., user clicks "Exit")
            event, _ = window.read(timeout=10)
            if event == "Exit" or event == sg.WINDOW_CLOSED:
                print("User exited the application.")
                break

            # Wait for the specified data interval
            time.sleep(DATA_INTERVAL)

        print("Data transmission completed.")

    except Exception as e:
        # Handle any client-side errors and log them
        print(f"Client error: {e}")

    finally:
        # Ensure the socket and GUI window are properly closed
        if client_socket:
            try:
                client_socket.close()
                print("Disconnected from server.")
            except Exception as e:
                print(f"Error closing socket: {e}")
        if window:
            window.close()

# Entry point of the script
if __name__ == "__main__":
    main()
