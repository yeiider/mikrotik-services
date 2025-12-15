from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
from core.config import settings
from typing import List, Optional
import time
from models.influx import InfluxPoint

class InfluxClient:
    def __init__(self):
        self.client = InfluxDBClient(
            url=settings.INFLUXDB_URL,
            token=settings.INFLUXDB_TOKEN,
            org=settings.INFLUXDB_ORG
        )
        self.write_api = self.client.write_api(write_options=WriteOptions(batch_size=500, flush_interval=10_000))
        self.query_api = self.client.query_api()
        self.bucket = settings.INFLUXDB_BUCKET

    def write_point(self, point: InfluxPoint):
        """Escribe un solo punto"""
        p = Point(point.measurement)
        for key, value in point.tags.items():
            p.tag(key, value)
        for key, value in point.fields.items():
            p.field(key, value)
        if point.time:
            p.time(point.time)
            
        self.write_api.write(bucket=self.bucket, org=settings.INFLUXDB_ORG, record=p)

    def write_batch(self, points: List[InfluxPoint]):
        """Escribe un lote de puntos"""
        batch = []
        for point in points:
            p = Point(point.measurement)
            for key, value in point.tags.items():
                p.tag(key, value)
            for key, value in point.fields.items():
                p.field(key, value)
            if point.time:
                p.time(point.time)
            batch.append(p)
        
        self.write_api.write(bucket=self.bucket, org=settings.INFLUXDB_ORG, record=batch)

    def close(self):
        self.client.close()

    def check_health(self) -> bool:
        try:
            return self.client.ping()
        except:
            return False

# Global instance
influx_db = InfluxClient()
