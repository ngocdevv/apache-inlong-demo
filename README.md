# Apache InLong Demo Project

This project demonstrates a simplified version of the Apache InLong architecture using Docker Compose and Python. It simulates a data pipeline for processing user behavior data.

## Architecture Components

The architecture follows the flow shown in the diagram:

1. **User Behavior Data Generator**: Simulates user activity data
2. **InLong Agent**: Collects data from files and forwards to DataProxy
3. **DataProxy**: Receives data and sends it to Kafka
4. **Kafka**: Message broker for data streaming
5. **InLong Sort**: Processes data from Kafka and loads it into Elasticsearch
6. **Elasticsearch**: Stores processed data for analysis and visualization
7. **Kibana**: Provides visualization interface for Elasticsearch data

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

## How to Run

1. Make sure you have Docker and Docker Compose installed on your system.

2. Clone or download this repository.

3. Navigate to the project directory:
   ```bash
   cd /Users/admin/CascadeProjects/inlong-demo
   ```

4. Start the services:
   ```bash
   docker-compose up -d
   ```

5. Check the status of the services:
   ```bash
   docker-compose ps
   ```

6. View the logs:
   ```bash
   docker-compose logs -f
   ```

7. Access Kibana to visualize the data:
   - Open your browser and navigate to http://localhost:5601
   - Create an index pattern for "user_behavior"
   - Explore the data using Kibana's Discover, Visualize, and Dashboard features

## Data Flow

1. The User Behavior Generator creates JSON files with simulated user activity data
2. InLong Agent monitors the data directory and picks up new files
3. Agent sends the data to DataProxy via HTTP
4. DataProxy forwards the data to Kafka
5. InLong Sort consumes data from Kafka, processes it, and loads it into Elasticsearch
6. Data can be visualized and analyzed using Kibana

## Stopping the Demo

To stop all services:
```bash
docker-compose down
```

To stop and remove all data (including volumes):
```bash
docker-compose down -v
```

## Customization

You can customize the demo by modifying the following:

- **User behavior data**: Edit the `generator.py` file to change the types of events generated
- **Processing logic**: Modify the `sort.py` file to change how data is processed
- **Elasticsearch mapping**: Update the mapping in `sort.py` to change how data is indexed
- **Visualization**: Create custom dashboards in Kibana

## Requirements

- Docker Engine 19.03.0+
- Docker Compose 1.27.0+
- At least 4GB of RAM allocated to Docker
