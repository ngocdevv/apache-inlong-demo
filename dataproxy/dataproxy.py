#!/usr/bin/env python3
"""
DataProxy Service

This service receives data from the InLong Agent and forwards it to Kafka.
It provides a REST API for data ingestion.
"""
import json
import time
from flask import Flask, request, jsonify
from kafka import KafkaProducer
from kafka.errors import KafkaError

app = Flask(__name__)

# Initialize Kafka producer with retry logic
def get_kafka_producer():
    for _ in range(30):  # Try for 5 minutes (30 * 10 seconds)
        try:
            producer = KafkaProducer(
                bootstrap_servers=['kafka:9092'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda v: v.encode('utf-8') if v else None,
                acks='all',
                retries=3
            )
            return producer
        except Exception as e:
            print(f"Failed to connect to Kafka: {str(e)}")
            print("Retrying in 10 seconds...")
            time.sleep(10)
    
    raise Exception("Failed to connect to Kafka after multiple attempts")

# Global Kafka producer
kafka_producer = None

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/data', methods=['POST'])
def receive_data():
    global kafka_producer
    
    # Initialize Kafka producer if not already initialized
    if kafka_producer is None:
        try:
            kafka_producer = get_kafka_producer()
            print("Kafka producer initialized")
        except Exception as e:
            return jsonify({"error": f"Failed to connect to Kafka: {str(e)}"}), 500
    
    if not request.json:
        return jsonify({"error": "Invalid request, JSON required"}), 400
    
    # Extract data from request
    source = request.json.get('source')
    data = request.json.get('data')
    
    if not source or not data:
        return jsonify({"error": "Missing required fields: source, data"}), 400
    
    # Determine Kafka topic based on source
    topic = f"{source}"
    
    # Send each event to Kafka
    success_count = 0
    error_count = 0
    
    for event in data:
        try:
            # Use user_id as key for partitioning if available
            key = event.get('user_id', None)
            
            # Send to Kafka
            future = kafka_producer.send(topic, key=key, value=event)
            future.get(timeout=10)  # Block until the message is sent or timeout
            success_count += 1
        except Exception as e:
            print(f"Error sending event to Kafka: {str(e)}")
            error_count += 1
    
    # Flush to ensure all messages are sent
    kafka_producer.flush()
    
    return jsonify({
        "status": "success",
        "processed": len(data),
        "success": success_count,
        "errors": error_count
    }), 200

if __name__ == '__main__':
    print("Starting DataProxy service...")
    
    # Wait for Kafka to be available
    print("Waiting for Kafka to be available...")
    try:
        kafka_producer = get_kafka_producer()
        print("Kafka is available")
    except Exception as e:
        print(f"Warning: Could not connect to Kafka initially: {str(e)}")
        print("Will try again when receiving data")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
