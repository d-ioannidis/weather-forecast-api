"""
This contains the routes for the forecast.
"""
from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlmodel import Session, select, func
from app.core.database import get_session
from app.services.forecast import ForecastService
from app.models.forecast import Location, Forecast
from datetime import datetime, timedelta

router = APIRouter()
forecast_service = ForecastService()
@router.get("/")
async def get_forecast(
    latitude: float = Query(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees"),
    longitude: float = Query(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees"),
    session: Session = Depends(get_session)
    ):
    """
    Get the current weather forecast starting from today's date up to a period of 7 days for the given location.

    Args:
        latitude (float): The latitude of the location for which to fetch the forecast.
        longitude (float): The longitude of the location for which to fetch the forecast.

    Returns:
        The current weather forecast.
    """
    today = datetime.now().date()
    dates = [(today + timedelta(days=i)).isoformat() for i in range(7)]
    locations = [(latitude, longitude)]
    return forecast_service.get_forecast_multiple_locations(dates[0], dates[-1], locations)

@router.post("/saveLocation")
async def save_location(
    latitude: float = Query(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees"),
    longitude: float = Query(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees"),
    session: Session = Depends(get_session)
):
    """
    Save a new forecast location if it does not already exist.

    Args:
        latitude (float): The latitude of the forecast location to be saved.
        longitude (float): The longitude of the forecast location to be saved.
        session (Session): The database session, obtained via dependency injection.

    Returns:
        Location: The existing or newly saved location.

    """
    # Round latitude and longitude to 4 decimal places for comparison
    rounded_lat = round(latitude, 4)
    rounded_lon = round(longitude, 4)

    # Check if the location already exists
    statement = select(Location).where(
        func.round(Location.latitude, 4) == rounded_lat,
        func.round(Location.longitude, 4) == rounded_lon
    )

    existing_location = session.exec(statement).first()

    if existing_location:
        return existing_location

    new_location = Location(latitude=latitude, longitude=longitude)
    session.add(new_location)
    session.commit()
    session.refresh(new_location)
    return new_location

@router.post("/saveForecast")
async def save_forecast(forecast_data: dict, session: Session = Depends(get_session)):
    """
    Save a new forecast.

    Args:
        forecast_data (dict): The forecast data to be saved.
        session (Session): The database session, obtained via dependency injection.

    Returns:
        Forecast: The saved forecast.

    """
    # Create a new forecast object
    forecast = Forecast(
        location_id=forecast_data["location_id"],
        start_date=forecast_data["start_date"],
        end_date=forecast_data["end_date"],
        temperature=forecast_data["temperature"],
        humidity=forecast_data["humidity"]
    )

    # Save the location if it does not already exist
    existing_location = session.exec(select(Location).where(Location.id == forecast.location_id)).first()

    if not existing_location:
        return {"error": "Location not found"}

    session.add(forecast)
    session.commit()
    session.refresh(forecast)
    return forecast

@router.post("/saveForecastData")
async def save_forecast_data(session: Session = Depends(get_session)):
    """
    Save all the forecast data returned from get_forecast_multiple_locations to the database.

    Args:
        session (Session): The database session, obtained via dependency injection.

    Returns:
        None
    """
    today = datetime.now().date()
    dates = [(today + timedelta(days=i)).isoformat() for i in range(7)]
    locations = [(37.983810, 23.727539), (40.629269, 22.947412), (34.923096, 33.634045)]
    forecast_data = forecast_service.get_forecast_multiple_locations(dates[0], dates[-1], locations)

    with session.no_autoflush:
        for location_data in forecast_data:
            latitude = location_data['latitude']
            longitude = location_data['longitude']
            forecasts = location_data['forecasts']

            # Save the location if it does not already exist
            existing_location = session.exec(select(Location).where(Location.latitude == latitude, Location.longitude == longitude)).first()

            if not existing_location:
                new_location = Location(latitude=latitude, longitude=longitude)
                session.add(new_location)
                session.commit()
                session.refresh(new_location)
                location_id = new_location.id
            else:
                location_id = existing_location.id

            # Save the forecast data
            for forecast in forecasts:
                new_forecast = Forecast(
                    location_id=location_id,
                    start_date=forecast['start_date'],
                    end_date=forecast['end_date'],
                    temperature=forecast['temperature'],
                    humidity=forecast['humidity']
                )
                session.add(new_forecast)

        session.commit()
        return {"message": "Forecast data saved successfully"}
    
@router.get("/listLocations")
async def list_locations(session: Session = Depends(get_session)):
    """
    Get a list of all locations.

    Returns:
        A list of all locations.
    """
    return session.exec(select(Location)).all()
    
@router.get("/latestForecasts")
async def get_latest_forecasts(session: Session = Depends(get_session)):
    """
    Get the latest forecast for each location for every day.

    Returns:
        A dictionary where each key is a location_id, and each value is another dictionary
        with dates as keys and the latest forecast for that date as values.
    """
    statement = select(Forecast).order_by(Forecast.start_date.desc())
    forecasts = session.exec(statement).all()

    result = defaultdict(dict)

    for forecast in forecasts:
        location_id = forecast.location_id
        
        start_datetime = datetime.strptime(forecast.start_date, "%Y-%m-%dT%H:%M:%SZ")
        date_key = start_datetime.date()

        if date_key not in result[location_id]:
            result[location_id][date_key] = forecast

    return result

@router.get("/averageTemperature")
async def get_average_temperature(session: Session = Depends(get_session)):
    """
    Get the average temperature for each location for every day.

    The average temperature is calculated by keeping only the last 3 forecasts for each location and date.

    Returns:
        A dictionary where each key is a location_id, and each value is another dictionary
        with dates as keys and the average temperature for that date as values.
    """
    statement = select(Forecast).order_by(Forecast.start_date.desc())
    forecasts = session.exec(statement).all()

    result = defaultdict(lambda: defaultdict(dict))

    for forecast in forecasts:
        location_id = forecast.location_id
        
        start_datetime = datetime.strptime(forecast.start_date, "%Y-%m-%dT%H:%M:%SZ")
        date_key = start_datetime.date()

        if date_key not in result[location_id]:
            result[location_id][date_key] = []

        result[location_id][date_key].append(forecast.temperature)

        # Keep only the last 3 forecasts for each location and date
        if len(result[location_id][date_key]) > 3:
            result[location_id][date_key].pop(0)

    # Calculate the average temperature for each location and date
    final_result = []

    for location_id, date_forecasts in result.items():
        for date_key, temperatures in date_forecasts.items():
            average_temperature = round(sum(temperatures) / len(temperatures), 2)
            final_result.append({
                "location_id": location_id,
                "date": date_key.isoformat(),
                "average_temperature": average_temperature
            })

    return final_result

@router.get("/topLocations")
async def get_top_locations(metric: str, n: int, session: Session = Depends(get_session)):
    """
    Retrieve the top `n` locations ranked by a specified weather metric.

    Args:
        metric (str): The weather metric for ranking locations (e.g., temperature, humidity).
        n (int): The number of top locations to retrieve.
        session (Session): Database session dependency.

    Returns:
        list[dict]: A list of dictionaries where each dictionary contains:
            - location_id: The ID of the location.
            - latitude: The latitude of the location.
            - longitude: The longitude of the location.
            - metric value: The value of the specified metric for the location.
            
    Raises:
        HTTPException: If the specified metric is not valid.
    """
    valid_metrics = ["temperature", "humidity"]

    if metric not in valid_metrics:
        raise HTTPException(status_code=400, detail=f"Invalid metric: {metric}. Valid metrics are {', '.join(valid_metrics)}")

    statement = select(Forecast).order_by(getattr(Forecast, metric).desc()).limit(n)
    forecasts = session.exec(statement).all()

    result = []

    seen_location_ids = set()

    for forecast in forecasts:
        location_id = forecast.location_id

        if location_id not in seen_location_ids:
            result.append({
                "location_id": location_id,
                "latitude": forecast.location.latitude,
                "longitude": forecast.location.longitude,
                metric: getattr(forecast, metric)
            })

            seen_location_ids.add(location_id)

        if len(result) == n:
            break

    return result