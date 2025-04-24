#!/usr/bin/env python3
"""
InLong Agent

This script monitors the data directory for new files, processes them,
and forwards the data to the DataProxy service.
"""
import json
import time
import os
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# DataProxy service endpoint
DATAPROXY_URL = "http://dataproxy:5000/api/data"

class NewFileHandler(FileSystemEventHandler):
    
    def on_created(self, event):
        """Handle file creation events"""
        if event.is_directory:
            return
        
        # Only process JSON files
        if not event.src_path.endswith('.json'):
            return
            
        print(f"New file detected: {event.src_path}")
        self.process_file(event.src_path)
    
    def process_file(self, file_path):
        try:
            # Wait a bit to ensure file is completely written
            time.sleep(1)
            
            # Read the file
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            print(f"Processing {len(data)} events from {file_path}")
            
            # Send data to DataProxy
            response = requests.post(
                DATAPROXY_URL,
                json={"source": "user_behavior", "data": data}
            )
            
            if response.status_code == 200:
                print(f"Successfully sent data to DataProxy")
                # Move or delete the file after successful processing
                os.rename(file_path, f"{file_path}.processed")
            else:
                print(f"Failed to send data to DataProxy: {response.status_code}")
                
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")

def main():
    print("Starting InLong Agent...")
    
    # Path to monitor
    data_path = "/data"
    
    # Create an observer and event handler
    event_handler = NewFileHandler()
    observer = Observer()
    
    # Schedule the observer to monitor the data directory
    observer.schedule(event_handler, data_path, recursive=False)
    observer.start()
    
    try:
        print(f"Monitoring directory: {data_path}")
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()

if __name__ == "__main__":
    # Wait for the DataProxy service to be available
    print("Waiting for DataProxy service...")
    while True:
        try:
            response = requests.get("http://dataproxy:5000/health")
            if response.status_code == 200:
                print("DataProxy service is available")
                break
        except:
            print("DataProxy service not available yet, retrying in 5 seconds...")
            time.sleep(5)
    
    main()
