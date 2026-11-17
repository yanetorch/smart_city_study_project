from pydantic import BaseModel

class SensorDataCreate(BaseModel):
    sensor_id: int
    value: float

class SensorCreate(BaseModel):
    name: str
    location: str
    sensor_type: str = "temperature"

class SensorOut(BaseModel):
    id: int
    name: str
    location: str
    sensor_type: str