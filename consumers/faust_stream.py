"""Defines trends calculations for stations"""
import logging

import faust

logger = logging.getLogger(__name__)


# Faust will ingest records from Kafka in this format
class Station(faust.Record):
    stop_id: int
    direction_id: str
    stop_name: str
    station_name: str
    station_descriptive_name: str
    station_id: int
    order: int
    red: bool
    blue: bool
    green: bool


# Faust will produce records to Kafka in this format
class TransformedStation(faust.Record):
    station_id: int
    station_name: str
    order: int
    line: str


app = faust.App("stations-stream", broker="kafka://localhost:9092", store="memory://")

topic = app.topic("cta.postgres.tables.stations", value_type=Station)

out_topic = app.topic("cta.stations.transformed", value_type=TransformedStation, partitions=20, value_serializer='json')

table = app.Table(
    "cta.stations.table",
    default=int,
    partitions=1,
    changelog_topic=out_topic,
)


def transform_station(station):
    def get_color():
        if station.red:
            return "red"

        elif station.green:
            return "green"

        elif station.blue:
            return "blue"

    return TransformedStation(
        station_id=station.station_id,
        station_name=station.station_name,
        order=station.order,
        line=get_color()
    )


@app.agent(topic)
async def process(stream):
    async for value in stream:
        print(transform_station(value))
        await out_topic.send(value=transform_station(value))


if __name__ == "__main__":
    app.main()
