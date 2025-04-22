# Apache InLong Installation Guide

This guide provides detailed instructions for installing and configuring Apache InLong in a production environment. Our demo project uses a simplified Docker Compose setup, but a full production deployment would involve installing the complete Apache InLong stack.

## Prerequisites

- Java 8 or 11 (required)
- MySQL 5.7+ or PostgreSQL 9.6+ (for metadata storage)
- ZooKeeper 3.6.x (for coordination)
- Kafka 2.x or Pulsar 2.8.x (for message queuing)
- Elasticsearch 7.x (for data storage and search)
- Flink 1.13.x (for stream processing, optional)

## Installation Options

### 1. Docker-based Installation (Recommended for Testing)

```bash
# Clone the InLong repository
git clone https://github.com/apache/inlong.git
cd inlong

# Build the InLong docker images
mvn package -DskipTests -Pdocker

# Start the InLong cluster
docker-compose up -d
```

### 2. Binary Package Installation (Recommended for Production)

```bash
# Download the latest InLong binary package
wget https://downloads.apache.org/inlong/1.6.0/apache-inlong-1.6.0-bin.tar.gz

# Extract the package
tar -xzvf apache-inlong-1.6.0-bin.tar.gz
cd apache-inlong-1.6.0-bin
```

## Component Installation

### 1. InLong Manager

```bash
# Initialize the database
mysql -h <mysql_host> -P <mysql_port> -u <mysql_user> -p<mysql_password> < sql/apache_inlong_manager.sql

# Configure the Manager
vi conf/application.properties
# Update the following properties:
# server.port=8083
# spring.datasource.url=jdbc:mysql://<mysql_host>:<mysql_port>/apache_inlong_manager
# spring.datasource.username=<mysql_user>
# spring.datasource.password=<mysql_password>

# Start the Manager
bash bin/manager.sh start
```

### 2. InLong Dashboard

```bash
# Configure the Dashboard
vi conf/application.properties
# Update the following properties:
# server.port=8080
# manager.url=http://<manager_host>:8083

# Start the Dashboard
bash bin/dashboard.sh start
```

### 3. InLong Agent

```bash
# Configure the Agent
vi conf/agent.properties
# Update the following properties:
# agent.local.ip=<agent_ip>
# agent.manager.url=http://<manager_host>:8083/api/inlong/manager/openapi

# Start the Agent
bash bin/agent.sh start
```

### 4. InLong DataProxy

```bash
# Configure the DataProxy
vi conf/dataproxy.properties
# Update the following properties:
# dataproxy.cluster.name=<cluster_name>
# dataproxy.manager.url=http://<manager_host>:8083/api/inlong/manager/openapi
# dataproxy.mq.type=kafka
# dataproxy.kafka.bootstrap.servers=<kafka_host>:<kafka_port>

# Start the DataProxy
bash bin/dataproxy.sh start
```

### 5. InLong Sort

```bash
# Configure the Sort
vi conf/sort.properties
# Update the following properties:
# sort.manager.url=http://<manager_host>:8083/api/inlong/manager/openapi
# sort.elasticsearch.hosts=<es_host>:<es_port>
# sort.flink.checkpoint.interval=60000

# Start the Sort
bash bin/sort.sh start
```

## Configuration

### 1. Create a Data Stream

1. Log in to the InLong Dashboard (http://<dashboard_host>:8080)
2. Create a new InLong Group
   - Group ID: Unique identifier for the group
   - Group Name: Descriptive name
   - Stream Source: Select data source type (e.g., File, Kafka, MySQL)
   - Stream Sink: Select data sink type (e.g., Elasticsearch, Hive, ClickHouse)
3. Configure Data Stream
   - Stream ID: Unique identifier for the stream
   - Stream Fields: Define the data schema
   - Data Source Configuration: Configure connection details
   - Data Sink Configuration: Configure destination details
4. Submit and Approve the Group
5. Start the Data Flow

### 2. Configure Data Transformation

InLong supports various data transformations using Flink SQL:

```sql
-- Example: Filter and transform data
CREATE VIEW filtered_data AS
SELECT 
    user_id,
    action,
    TIMESTAMP(timestamp) AS event_time,
    category,
    platform
FROM user_behavior
WHERE action IN ('view', 'purchase', 'click')
```

### 3. Monitoring and Management

1. Access the InLong Dashboard
2. Navigate to the "Monitoring" section
3. View metrics for:
   - Data Ingestion Rate
   - Data Processing Latency
   - Error Rates
   - Resource Utilization

## Scaling and High Availability

### 1. Scaling Components

- **InLong Manager**: Deploy multiple instances behind a load balancer
- **InLong DataProxy**: Add more instances and configure load balancing
- **InLong Sort**: Increase Flink parallelism and task slots

### 2. High Availability Configuration

```properties
# ZooKeeper HA Configuration
zookeeper.quorum=zk1:2181,zk2:2181,zk3:2181

# Kafka HA Configuration
kafka.bootstrap.servers=kafka1:9092,kafka2:9092,kafka3:9092

# Flink HA Configuration
flink.jobmanager.ha.mode=zookeeper
flink.jobmanager.ha.zookeeper.quorum=zk1:2181,zk2:2181,zk3:2181
```

## Troubleshooting

### Common Issues

1. **Connection Failures**
   - Check network connectivity between components
   - Verify firewall settings
   - Ensure correct hostnames and ports

2. **Data Processing Issues**
   - Check Flink job status
   - Verify data schema compatibility
   - Examine error logs

3. **Performance Problems**
   - Monitor resource utilization
   - Adjust buffer sizes and batch settings
   - Scale components as needed

### Log Locations

- InLong Manager: `logs/manager.log`
- InLong Agent: `logs/agent.log`
- InLong DataProxy: `logs/dataproxy.log`
- InLong Sort: `logs/sort.log`

## Security Configuration

### 1. Authentication

```properties
# Enable authentication
auth.enabled=true

# LDAP authentication
auth.ldap.url=ldap://<ldap_host>:<ldap_port>
auth.ldap.baseDn=dc=example,dc=com
```

### 2. Authorization

```properties
# Role-based access control
auth.rbac.enabled=true
```

### 3. Data Encryption

```properties
# Enable TLS
ssl.enabled=true
ssl.keystore.path=/path/to/keystore.jks
ssl.keystore.password=<password>
```
