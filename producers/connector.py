"""Configures a Kafka Connector for Postgres Station data"""
import json
import logging

import requests

logger = logging.getLogger(__name__)

KAFKA_CONNECT_URL = "http://localhost:8083/connectors"
CONNECTOR_NAME = "stations"

DB_URL = "postgres:5432"
DB_USERNAME = "cta_admin"
DB_PASSWORD = "chicago"
DB_NAME = "cta"


def configure_connector():
    """Starts and configures the Kafka Connect connector"""
    logging.debug("creating or updating kafka connect connector...")

    resp = requests.get(f"{KAFKA_CONNECT_URL}/{CONNECTOR_NAME}")
    if resp.status_code == 200:
        logging.debug("connector already created skipping recreation")
        return

    logger.info("connector code not completed skipping connector creation")
    resp = requests.post(
        KAFKA_CONNECT_URL,
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "name": CONNECTOR_NAME,
            "config": {
                "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",
                "key.converter": "org.apache.kafka.connect.json.JsonConverter",
                "key.converter.schemas.enable": "false",
                "value.converter": "org.apache.kafka.connect.json.JsonConverter",
                "value.converter.schemas.enable": "false",
                "batch.max.rows": "500",
                "connection.url": f"jdbc:postgresql://{DB_URL}/{DB_NAME}",
                "connection.user": DB_USERNAME,
                "connection.password": DB_PASSWORD,
                "poll.interval.ms": 10000,
                "topic.prefix": "cta.postgres.tables.",
                "incrementing.column.name": "stop_id",
                "table.whitelist": "stations",
                "mode": "incrementing",
            }
        }),
    )

    resp.raise_for_status()
    logging.debug("connector created successfully")


if __name__ == "__main__":
    configure_connector()
