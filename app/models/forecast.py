"""
Contains classes that represent database models.
These are the classes that map directly to database tables (i.e., SQLModel classes)
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Location(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    latitude: float
    longitude: float
    forecasts: List["Forecast"] = Relationship(back_populates="location")

class Forecast(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    location_id: int = Field(foreign_key="location.id")
    start_date: str
    end_date: str
    temperature: float
    humidity: float
    location: Optional[Location] = Relationship(back_populates="forecasts")

class ForecastResponse(SQLModel):
    start_date: str
    end_date: str
    temperature: float
    humidity: float
    latitude: float
    longitude: float