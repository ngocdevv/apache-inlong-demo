#!/usr/bin/env python3
"""
InLong Sort

This script consumes data from Kafka, processes it, and loads it into Elasticsearch.
"""
import json
import time
import threading
import sys
from datetime import datetime
from kafka import KafkaConsumer
from elasticsearch import Elasticsearch
import requests

# Configure logging to stdout
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Kafka configuration
KAFKA_SERVERS = ['kafka:9092']
KAFKA_TOPIC = 'user_behavior'
CONSUMER_GROUP = 'inlong-sort'

# Elasticsearch configuration
ES_HOST = 'elasticsearch'
ES_PORT = 9200
ES_INDEX = 'user_behavior'

def wait_for_kafka():
    """Wait for Kafka to be available"""
    logger.info("Waiting for Kafka to be available...")
    while True:
        try:
            consumer = KafkaConsumer(
                bootstrap_servers=KAFKA_SERVERS,
                group_id='healthcheck',
                consumer_timeout_ms=5000
            )
            consumer.close()
            logger.info("Kafka is available")
            return
        except Exception as e:
            logger.warning(f"Kafka not available yet: {str(e)}")
            time.sleep(5)

def wait_for_elasticsearch():
    """Wait for Elasticsearch to be available"""
    logger.info("Waiting for Elasticsearch to be available...")
    while True:
        try:
            response = requests.get(f"http://{ES_HOST}:{ES_PORT}")
            if response.status_code == 200:
                logger.info("Elasticsearch is available")
                return
        except Exception as e:
            logger.warning(f"Elasticsearch not available yet: {str(e)}")
            time.sleep(5)

def create_elasticsearch_index():
    """Create Elasticsearch index with mapping"""
    es = Elasticsearch([f"http://{ES_HOST}:{ES_PORT}"])
    
    # Define index mapping
    mapping = {
        "mappings": {
            "properties": {
                "user_id": {"type": "keyword"},
                "session_id": {"type": "keyword"},
                "timestamp": {"type": "date"},
                "action": {"type": "keyword"},
                "category": {"type": "keyword"},
                "product_id": {"type": "keyword"},
                "platform": {"type": "keyword"},
                "device_info": {
                    "properties": {
                        "os": {"type": "keyword"},
                        "browser": {"type": "keyword"},
                        "version": {"type": "keyword"}
                    }
                },
                "location": {
                    "properties": {
                        "country": {"type": "keyword"},
                        "city": {"type": "keyword"},
                        "ip": {"type": "ip"}
                    }
                },
                "referrer": {"type": "keyword"},
                "time_spent": {"type": "integer"}
            }
        }
    }
    
    # Create index if it doesn't exist
    if not es.indices.exists(index=ES_INDEX):
        es.indices.create(index=ES_INDEX, body=mapping)
        logger.info(f"Created Elasticsearch index: {ES_INDEX}")
    else:
        logger.info(f"Elasticsearch index {ES_INDEX} already exists")

def process_and_enrich(event):
    """Process and enrich the event data"""
    # Add processing timestamp
    event['processed_at'] = datetime.now().isoformat()
    
    # Add any additional enrichment here
    # For example, categorize time spent
    if event.get('time_spent') is not None:
        if event['time_spent'] < 30:
            event['engagement_level'] = 'low'
        elif event['time_spent'] < 120:
            event['engagement_level'] = 'medium'
        else:
            event['engagement_level'] = 'high'
    
    return event

def consume_and_process():
    """Consume messages from Kafka, process them, and load into Elasticsearch"""
    # Initialize Kafka consumer
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_SERVERS,
        group_id=CONSUMER_GROUP,
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        enable_auto_commit=False,
        max_poll_interval_ms=300000,  # 5 minutes
        session_timeout_ms=30000      # 30 seconds
    )
    
    # Initialize Elasticsearch client
    es = Elasticsearch([f"http://{ES_HOST}:{ES_PORT}"])
    
    logger.info(f"Starting to consume from Kafka topic: {KAFKA_TOPIC}")
    
    # Process messages in batches
    batch_size = 100
    batch = []
    
    try:
        for message in consumer:
            event = message.value
            
            # Process and enrich the event
            processed_event = process_and_enrich(event)
            
            # Add to batch
            batch.append(processed_event)
            
            # If batch is full, index to Elasticsearch
            if len(batch) >= batch_size:
                bulk_index_to_elasticsearch(es, batch)
                batch = []
                consumer.commit()
    
    except Exception as e:
        logger.error(f"Error in consume_and_process: {str(e)}")
        if batch:  # Index any remaining events
            bulk_index_to_elasticsearch(es, batch)
            consumer.commit()
    finally:
        consumer.close()

def bulk_index_to_elasticsearch(es, events):
    """Bulk index events to Elasticsearch"""
    if not events:
        return
    
    # Prepare bulk request
    bulk_data = []
    for event in events:
        # Add index action
        bulk_data.append({"index": {"_index": ES_INDEX, "_id": event.get('user_id') + '-' + event.get('timestamp')}})
        # Add document
        bulk_data.append(event)
    
    # Execute bulk request
    response = es.bulk(index=ES_INDEX, body=bulk_data, refresh=True)
    
    # Check for errors
    if response.get('errors'):
        error_count = sum(1 for item in response['items'] if item.get('index', {}).get('error'))
        logger.warning(f"Bulk indexing completed with {error_count} errors out of {len(events)} events")
    else:
        logger.info(f"Successfully indexed {len(events)} events to Elasticsearch")

def main():
    """Main function"""
    logger.info("Starting InLong Sort...")
    
    # Wait for dependencies
    wait_for_kafka()
    wait_for_elasticsearch()
    
    # Create Elasticsearch index
    create_elasticsearch_index()
    
    # Start processing in a separate thread
    processing_thread = threading.Thread(target=consume_and_process)
    processing_thread.daemon = True
    processing_thread.start()
    
    # Keep the main thread running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")

if __name__ == "__main__":
    main()
