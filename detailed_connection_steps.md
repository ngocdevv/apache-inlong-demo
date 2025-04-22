# Detailed Connection Steps for Apache InLong Demo Project

This guide provides step-by-step instructions for connecting and running all components of the Apache InLong demo project.

## Prerequisites

Ensure you have completed the installation steps in the `detailed_installation_guide.md` file and all services are running.

## Connection Flow Overview

```mermaid
flowchart LR
    A[Start Services] --> B[Verify Component Health]
    B --> C[Monitor Data Generation]
    C --> D[Observe Data Flow]
    D --> E[Access Kibana]
    E --> F[Create Visualizations]
```

## Step 1: Start All Services

Start all services using Docker Compose:

```bash
docker-compose up -d
```

## Step 2: Verify Component Health

### Check Service Status

```bash
docker-compose ps
```

All services should show a status of "Up".

### Verify Kafka Setup

Check if Kafka is running and the topic is created:

```bash
docker exec -it inlong-demo_kafka_1 kafka-topics --bootstrap-server kafka:9092 --list
```

You should see the `user_behavior` topic in the list. If not, create it manually:

```bash
docker exec -it inlong-demo_kafka_1 kafka-topics --bootstrap-server kafka:9092 --create --topic user_behavior --partitions 1 --replication-factor 1
```

### Verify Elasticsearch Health

Check Elasticsearch's health:

```bash
curl -X GET "http://localhost:9200/_cluster/health?pretty"
```

The response should show `"status": "green"` or `"status": "yellow"`.

## Step 3: Monitor Data Generation

### Check Data Directory

Monitor the data directory to see if files are being generated:

```bash
ls -la data/
```

You should see JSON files being created by the User Behavior Generator.

### Monitor User Behavior Generator Logs

```bash
docker-compose logs -f user-behavior-generator
```

You should see log messages indicating that data is being generated.

## Step 4: Observe Data Flow Through Components

### Monitor InLong Agent Logs

```bash
docker-compose logs -f inlong-agent
```

You should see log messages indicating that files are being processed and data is being sent to DataProxy.

### Monitor DataProxy Logs

```bash
docker-compose logs -f dataproxy
```

You should see log messages indicating that data is being received from the InLong Agent and sent to Kafka.

### Check Kafka Messages

```bash
docker exec -it inlong-demo_kafka_1 kafka-console-consumer --bootstrap-server kafka:9092 --topic user_behavior --from-beginning --max-messages 5
```

This command will display up to 5 messages from the `user_behavior` topic.

### Monitor InLong Sort Logs

```bash
docker-compose logs -f inlong-sort
```

You should see log messages indicating that data is being consumed from Kafka and indexed into Elasticsearch.

## Step 5: Verify Data in Elasticsearch

Check if data is being indexed into Elasticsearch:

```bash
curl -X GET "http://localhost:9200/user_behavior/_count?pretty"
```

The response should show a count greater than 0.

To see the actual data:

```bash
curl -X GET "http://localhost:9200/user_behavior/_search?pretty&size=5"
```

## Step 6: Access Kibana and Create Visualizations

### Access Kibana

Open your browser and navigate to:

```
http://localhost:5601
```

### Create Index Pattern

1. Go to Stack Management > Index Patterns
2. Click "Create index pattern"
3. Enter `user_behavior*` as the index pattern
4. Click "Next step"
5. Select `@timestamp` as the Time field
6. Click "Create index pattern"

### Create Visualizations

1. Go to Visualize
2. Click "Create new visualization"
3. Choose a visualization type (e.g., Line, Bar, Pie)
4. Select the `user_behavior*` index pattern
5. Configure your visualization:
   - For metrics, you can use count, sum, average, etc.
   - For buckets, you can use date histogram, terms, etc.
6. Click "Save" to save your visualization

### Create Dashboard

1. Go to Dashboard
2. Click "Create new dashboard"
3. Click "Add" to add visualizations
4. Select the visualizations you created
5. Arrange the visualizations on the dashboard
6. Click "Save" to save your dashboard

## Step 7: Troubleshooting Connection Issues

### Component Connection Issues

If components are not connecting properly, check the following:

1. **Network Connectivity**:
   ```bash
   docker network inspect inlong-demo_inlong-network
   ```
   Verify all services are connected to the network.

2. **Service Health**:
   ```bash
   docker-compose ps
   ```
   Ensure all services are running.

3. **Log Analysis**:
   ```bash
   docker-compose logs <service-name>
   ```
   Look for error messages in the logs.

### Specific Component Troubleshooting

#### InLong Agent Issues

If the InLong Agent is not processing files:
- Check if the data directory is mounted correctly
- Verify file permissions
- Check if the DataProxy endpoint is accessible

#### DataProxy Issues

If DataProxy is not receiving data or not sending to Kafka:
- Check if the HTTP endpoint is working
- Verify Kafka connection settings
- Check for validation errors in the logs

#### Kafka Issues

If Kafka is not receiving or processing messages:
- Check if Zookeeper is running
- Verify Kafka broker settings
- Check topic configuration

#### InLong Sort Issues

If InLong Sort is not processing data:
- Check Kafka consumer configuration
- Verify Elasticsearch connection
- Check for processing errors in the logs

#### Elasticsearch Issues

If data is not being indexed:
- Check Elasticsearch health
- Verify index settings
- Check for indexing errors

## Step 8: Stopping and Restarting

### Stopping Services

```bash
docker-compose down
```

### Restarting Services

```bash
docker-compose up -d
```

### Resetting Data

To reset all data and start fresh:

```bash
docker-compose down -v
docker-compose up -d
```

## Step 9: Scaling Components (Optional)

For increased throughput, you can scale certain components:

```bash
docker-compose up -d --scale inlong-agent=2 --scale dataproxy=2 --scale inlong-sort=2
```

This will start multiple instances of the specified services.

## Step 10: Monitoring the System

### Check Resource Usage

```bash
docker stats
```

### Monitor All Logs

```bash
docker-compose logs -f
```

### Check Disk Usage

```bash
docker system df
```

## Conclusion

By following these steps, you should have a fully connected and functioning Apache InLong demo system. The data should flow from the User Behavior Generator through the InLong Agent, DataProxy, Kafka, and InLong Sort, and finally be stored in Elasticsearch and visualized in Kibana.
