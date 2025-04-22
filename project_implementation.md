# InLong Demo Project Implementation Guide

This document describes the specific implementation of our Apache InLong demo project using Docker Compose and Python.

## Components Installed

Our implementation includes the following containerized components:

1. **Zookeeper**: Coordination service required by Kafka
   - Image: `confluentinc/cp-zookeeper:7.3.2`
   - Platform: `linux/arm64` (for Apple Silicon compatibility)
   - Port: 2181

2. **Kafka**: Message broker for data streaming
   - Image: `confluentinc/cp-kafka:7.3.2`
   - Platform: `linux/arm64` (for Apple Silicon compatibility)
   - Port: 9092
   - Topic: `user_behavior`

3. **Elasticsearch**: Data storage and search engine
   - Image: `docker.elastic.co/elasticsearch/elasticsearch:7.14.0`
   - Port: 9200, 9300
   - Index: `user_behavior`

4. **Kibana**: Visualization platform for Elasticsearch
   - Image: `docker.elastic.co/kibana/kibana:7.14.0`
   - Port: 5601

5. **Custom Python Components**:
   - **User Behavior Generator**: Simulates user activity data
   - **InLong Agent**: Collects data from files
   - **DataProxy**: Transfers data to Kafka
   - **InLong Sort**: Processes data and loads into Elasticsearch

## Project Structure

```
inlong-demo/
├── docker-compose.yml        # Docker Compose configuration
├── data/                     # Shared data directory
├── user-behavior/            # User behavior data generator
│   ├── Dockerfile
│   ├── requirements.txt
│   └── generator.py
├── inlong-agent/             # InLong Agent component
│   ├── Dockerfile
│   ├── requirements.txt
│   └── agent.py
├── dataproxy/                # DataProxy component
│   ├── Dockerfile
│   ├── requirements.txt
│   └── dataproxy.py
└── inlong-sort/              # InLong Sort component
    ├── Dockerfile
    ├── requirements.txt
    └── sort.py
```

## Docker Compose Configuration

Our `docker-compose.yml` file defines and connects all services:

```yaml
version: '3.8'

services:
  # Zookeeper - required for Kafka
  zookeeper:
    image: confluentinc/cp-zookeeper:7.3.2
    platform: linux/arm64
    ports:
      - "2181:2181"
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    networks:
      - inlong-network

  # Kafka - message broker
  kafka:
    image: confluentinc/cp-kafka:7.3.2
    platform: linux/arm64
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
    depends_on:
      - zookeeper
    networks:
      - inlong-network

  # Elasticsearch - data storage and visualization
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.14.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
      - "9300:9300"
    networks:
      - inlong-network
    volumes:
      - es-data:/usr/share/elasticsearch/data

  # Kibana - visualization for Elasticsearch
  kibana:
    image: docker.elastic.co/kibana/kibana:7.14.0
    environment:
      ELASTICSEARCH_HOSTS: http://elasticsearch:9200
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
    networks:
      - inlong-network

  # Custom Python components
  inlong-agent:
    build: ./inlong-agent
    volumes:
      - ./data:/data
    depends_on:
      - dataproxy
    networks:
      - inlong-network

  dataproxy:
    build: ./dataproxy
    depends_on:
      - kafka
    networks:
      - inlong-network

  inlong-sort:
    build: ./inlong-sort
    depends_on:
      - kafka
      - elasticsearch
    networks:
      - inlong-network

  user-behavior-generator:
    build: ./user-behavior
    volumes:
      - ./data:/data
    networks:
      - inlong-network

networks:
  inlong-network:
    driver: bridge

volumes:
  es-data:
```

## Python Component Implementation

### User Behavior Generator

A Python script that:
- Generates random user behavior data (views, clicks, purchases, etc.)
- Creates JSON files in the shared `/data` directory
- Runs continuously to simulate real-time data generation

### InLong Agent

A Python service that:
- Monitors the `/data` directory using the Watchdog library
- Processes new JSON files as they appear
- Sends data to the DataProxy service via HTTP
- Marks processed files to avoid duplication

### DataProxy

A Flask-based REST API that:
- Receives data from the InLong Agent
- Validates and processes the incoming data
- Produces messages to the Kafka topic `user_behavior`
- Provides a health check endpoint

### InLong Sort

A Python service that:
- Consumes messages from the Kafka topic `user_behavior`
- Processes and enriches the data (adds timestamps, engagement levels, etc.)
- Indexes the processed data into Elasticsearch
- Uses bulk operations for efficiency

## Data Flow

1. **User Behavior Generator** creates JSON files with simulated data
2. **InLong Agent** detects new files and sends data to DataProxy
3. **DataProxy** forwards data to Kafka
4. **InLong Sort** consumes from Kafka, processes data, and loads into Elasticsearch
5. **Kibana** provides visualization of the data in Elasticsearch

## Running the Project

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Access Kibana
# Open http://localhost:5601 in your browser

# Stop all services
docker-compose down
```

## Creating Kibana Visualizations

1. Access Kibana at http://localhost:5601
2. Create an index pattern:
   - Go to Stack Management > Index Patterns
   - Create pattern: `user_behavior`
   - Time field: `timestamp`
3. Explore data in Discover
4. Create visualizations:
   - User actions by category
   - Platform distribution
   - Time-based activity trends
   - Geographic distribution of users

## Troubleshooting

### Common Issues

1. **Platform Compatibility**
   - Ensure Docker images are compatible with your architecture (ARM64/AMD64)
   - Use `platform: linux/arm64` for Apple Silicon Macs

2. **Kafka Connection Issues**
   - Check Zookeeper is running properly
   - Verify Kafka broker configuration
   - Ensure proper network connectivity between containers

3. **Elasticsearch Issues**
   - Check Elasticsearch logs for startup errors
   - Verify memory settings are appropriate
   - Ensure index mapping is correct

4. **Python Component Errors**
   - Check component logs for Python exceptions
   - Verify dependencies are installed correctly
   - Ensure proper configuration of endpoints and connections
