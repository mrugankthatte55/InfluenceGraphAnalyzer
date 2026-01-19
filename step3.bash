
echo "Waiting for Kafka at kafka-service:29092..."
              while ! nc -z kafka-service 29092; do sleep 2; done
              echo "Kafka is up."

              echo "Waiting for Neo4j at neo4j-service:7687..."
              while ! nc -z neo4j-service 7687; do sleep 2; done
              echo "Neo4j is up."

              echo "Starting Kafka Connect..."
              /etc/confluent/docker/run
