## System Requirements

Before installing Apache InLong, ensure your system meets the following requirements:

- **Docker Engine**: Version 19.03.0 or higher
- **Docker Compose**: Version 1.27.0 or higher
- **Memory**: At least 4GB of RAM allocated to Docker
- **Disk Space**: At least 10GB of free disk space
- **Operating System**: Linux, macOS, or Windows with WSL2
- **Network**: Internet connection for downloading Docker images

## Installing Apache InLong with Docker

Our demo project uses a simplified version of Apache InLong implemented with Docker Compose and Python components. Follow these steps to install:

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd apache-inlong-demo
   ```

2. **Check System Compatibility**
   For Apple Silicon Macs (M1/M2/M3/M4), the Docker Compose file is already configured with platform-specific images:

   ```yaml
   # Example from docker-compose.yml
   zookeeper:
     image: confluentinc/cp-zookeeper:7.3.2
     platform: linux/arm64  # For Apple Silicon compatibility
   ```

## Configuring Docker Compose
The `docker-compose.yml` file defines the following services:

1. **Zookeeper**: Coordination service for Kafka
   ```yaml
   zookeeper:
     image: confluentinc/cp-zookeeper:7.3.2
     ports:
       - "2181:2181"
     environment:
       ZOOKEEPER_CLIENT_PORT: 2181
       ZOOKEEPER_TICK_TIME: 2000
   ```

2. **Kafka**: Message broker for data streaming
   ```yaml
   kafka:
     image: confluentinc/cp-kafka:7.3.2
     ports:
       - "9092:9092"
     environment:
       KAFKA_BROKER_ID: 1
       KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
       KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
       KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
       KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
   ```

3. **Elasticsearch**: Data storage and search engine
   ```yaml
   elasticsearch:
     image: docker.elastic.co/elasticsearch/elasticsearch:7.14.0
     environment:
       - discovery.type=single-node
       - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
     ports:
       - "9200:9200"
       - "9300:9300"
   ```

4. **Kibana**: Visualization platform for Elasticsearch
   ```yaml
   kibana:
     image: docker.elastic.co/kibana/kibana:7.14.0
     environment:
       ELASTICSEARCH_HOSTS: http://elasticsearch:9200
     ports:
       - "5601:5601"
   ```

5. **Custom Python Components**:
   - **User Behavior Generator**: Simulates user activity data
   - **InLong Agent**: Collects data from files
   - **DataProxy**: Transfers data to Kafka
   - **InLong Sort**: Processes data and loads into Elasticsearch