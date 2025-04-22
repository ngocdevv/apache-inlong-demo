# InLong Data Flow Architecture

## Overview Diagram

```mermaid
graph LR
    A[User Behavior Data] -->|Generates JSON files| B[InLong Agent]
    B -->|HTTP API| C[DataProxy]
    C -->|Produces messages| D[Kafka]
    D -->|Consumes messages| E[InLong Sort]
    E -->|Indexes data| F[Elasticsearch]
    F -->|Visualizes data| G[Kibana]
```

## Detailed Data Flow

### 1. User Behavior Data Generation
- Python script generates simulated user behavior events
- Events include user actions, timestamps, device info, etc.
- Data is written to JSON files in a shared volume

### 2. InLong Agent
- Monitors the data directory for new files
- When a new file is detected, reads the content
- Sends the data to DataProxy via HTTP API
- Marks processed files to avoid reprocessing

### 3. DataProxy
- Provides REST API endpoint to receive data
- Validates and processes incoming data
- Produces messages to Kafka topic
- Acts as a buffer between data sources and message queue

### 4. Kafka
- Message broker that stores streams of records
- Provides scalable, fault-tolerant message queue
- Enables decoupling of data producers and consumers
- Topic: `user_behavior`

### 5. InLong Sort
- Consumes messages from Kafka
- Processes and enriches the data
- Performs batch operations for efficiency
- Loads processed data into Elasticsearch

### 6. Elasticsearch
- Stores and indexes the processed data
- Provides powerful search and analytics capabilities
- Index: `user_behavior`

### 7. Kibana
- Visualization platform for Elasticsearch data
- Provides dashboards, charts, and analytics tools
- Enables real-time monitoring and analysis

## Data Transformation

The data undergoes several transformations as it flows through the system:

1. **Raw Data**: JSON files with user events
2. **Validated Data**: Structured data validated by DataProxy
3. **Streamed Data**: Messages in Kafka topic
4. **Enriched Data**: Processed data with additional fields
5. **Indexed Data**: Data stored in Elasticsearch with mapping
6. **Visualized Data**: Interactive visualizations in Kibana

## Error Handling

- **File Processing Errors**: InLong Agent marks failed files
- **API Errors**: DataProxy returns appropriate HTTP status codes
- **Kafka Errors**: Retry mechanism for failed message production
- **Processing Errors**: InLong Sort logs errors and continues processing
- **Indexing Errors**: Bulk indexing with error reporting
