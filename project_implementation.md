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
