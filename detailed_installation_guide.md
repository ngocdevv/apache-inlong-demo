# Detailed Apache InLong Installation Guide

This guide provides step-by-step instructions for installing and configuring Apache InLong in this demo project. The installation process is simplified using Docker Compose, which sets up all required components in containers.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Docker Engine (version 19.03.0+)
- Docker Compose (version 1.27.0+)
- Git (for cloning the repository)
- At least 4GB of RAM allocated to Docker

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd inlong-demo
```

### 2. Environment Setup

The project uses Docker Compose to set up the following components:

- Zookeeper (coordination service)
- Kafka (message broker)
- Elasticsearch (data storage)
- Kibana (visualization)
- Custom Python components:
  - User Behavior Generator
  - InLong Agent
  - DataProxy
  - InLong Sort

### 3. Docker Compose Configuration

The `docker-compose.yml` file is already configured with all necessary services. Key configurations include:

- **Zookeeper**: Runs on port 2181
- **Kafka**: Runs on port 9092 with auto topic creation enabled
- **Elasticsearch**: Runs on ports 9200 and 9300 as a single-node instance
- **Kibana**: Runs on port 5601 and connects to Elasticsearch
- **Custom Python components**: Built from local Dockerfiles

### 4. Start the Services

```bash
docker-compose up -d
```

This command builds and starts all services defined in the `docker-compose.yml` file in detached mode.

### 5. Verify Installation

Check if all services are running properly:

```bash
docker-compose ps
```

All services should show a status of "Up".

### 6. View Logs

To monitor the logs of all services:

```bash
docker-compose logs -f
```

To view logs for a specific service:

```bash
docker-compose logs -f <service-name>
```

Replace `<service-name>` with one of: zookeeper, kafka, elasticsearch, kibana, inlong-agent, dataproxy, inlong-sort, or user-behavior-generator.

## Component Configuration Details

### Zookeeper Configuration

```yaml
environment:
  ZOOKEEPER_CLIENT_PORT: 2181
  ZOOKEEPER_TICK_TIME: 2000
```

### Kafka Configuration

```yaml
environment:
  KAFKA_BROKER_ID: 1
  KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
  KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
  KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
  KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
  KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
  KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
```

### Elasticsearch Configuration

```yaml
environment:
  - discovery.type=single-node
  - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
```

### Kibana Configuration

```yaml
environment:
  ELASTICSEARCH_HOSTS: http://elasticsearch:9200
```

## Custom Component Configurations

### InLong Agent

The InLong Agent is configured to:
- Monitor the `/data` directory for new files
- Process JSON files containing user behavior data
- Send data to the DataProxy service

### DataProxy

The DataProxy is configured to:
- Receive data from the InLong Agent via HTTP
- Validate and process the incoming data
- Produce messages to the Kafka topic `user_behavior`

### InLong Sort

The InLong Sort is configured to:
- Consume messages from the Kafka topic `user_behavior`
- Process and enrich the data
- Index the processed data into Elasticsearch

## Production Deployment Considerations

For a production deployment of Apache InLong, consider the following additional steps:

1. **High Availability**: Deploy multiple instances of each component
2. **Security**: Configure authentication and encryption
3. **Monitoring**: Set up monitoring and alerting
4. **Backup**: Implement regular data backup procedures
5. **Scaling**: Configure resource limits and scaling policies

## Troubleshooting

### Common Issues

1. **Services fail to start**
   - Check Docker logs: `docker-compose logs <service-name>`
   - Ensure ports are not already in use
   - Verify Docker has sufficient resources

2. **Data not flowing through the pipeline**
   - Check if the User Behavior Generator is creating files
   - Verify the InLong Agent is processing files
   - Check Kafka topics and messages
   - Examine Elasticsearch indices

3. **Visualization not working**
   - Ensure Elasticsearch is running and accessible
   - Verify Kibana is connected to Elasticsearch
   - Check if data is being indexed into Elasticsearch

## Stopping the Services

To stop all services:

```bash
docker-compose down
```

To stop and remove all data (including volumes):

```bash
docker-compose down -v
```
