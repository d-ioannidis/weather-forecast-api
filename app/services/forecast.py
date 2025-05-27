# app/services/book.py
import os
import requests
from app.models.forecast import ForecastResponse

class ForecastService:
    def __init__(self):
        """
        Initialize the ForecastService object.

        This constructor sets the base URL for the Meteomatics API by
        retrieving the username and password from environment variables.
        """
        self.base_url = f"https://{os.getenv('METEOMATICS_API_USERNAME')}:{os.getenv('METEOMATICS_API_PASSWORD')}@api.meteomatics.com"

    def get_forecast(self, start_date, end_date, latitude, longitude):
        """
        Get the weather forecast for a given location and time period.

        Args:
            start_date (str): The start date of the time period in the format 'YYYY-MM-DD'.
            end_date (str): The end date of the time period in the format 'YYYY-MM-DD'.
            latitude (float): The latitude of the location.
            longitude (float): The longitude of the location.

        Returns:
            list[ForecastResponse]: A list of ForecastResponse objects containing the weather data for each day in the specified time period.
        """
        url = f"{self.base_url}/{start_date}T00:00:00Z--{end_date}T00:00:00Z:PT1H/t_2m:C,relative_humidity_2m:p/{latitude},{longitude}/json?model=mix"
        headers = {"Content-Type": "application/json"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            weather_data = response.json()
            weather_list = []

            # Process temperature and humidity data for each day
            temperature_data = next((param for param in weather_data['data'] if param['parameter'] == 't_2m:C'), None)
            humidity_data = next((param for param in weather_data['data'] if param['parameter'] == 'relative_humidity_2m:p'), None)

            if temperature_data and humidity_data:
                for temp_coord, hum_coord in zip(temperature_data['coordinates'][0]['dates'], humidity_data['coordinates'][0]['dates']):
                    weather = ForecastResponse(
                        start_date=temp_coord['date'],
                        end_date=temp_coord['date'],
                        temperature=temp_coord['value'],
                        humidity=hum_coord['value'],
                        latitude=latitude,
                        longitude=longitude
                    )
                    weather_list.append(weather)

            return weather_list
        else:
            print(f"Error: {response.status_code}")
            return None

    def get_forecast_multiple_locations(self, start_date, end_date, locations):
        """
        Get the weather forecast for a given time period and multiple locations.

        Args:
            start_date (str): The start date of the time period in the format 'YYYY-MM-DD'.
            end_date (str): The end date of the time period in the format 'YYYY-MM-DD'.
            locations (list[tuple[float, float]]): A list of (latitude, longitude) tuples containing the locations to get the forecast for.

        Returns:
            list[dict]: A list of dictionaries, each containing the forecast data for a given location. The structure of each dictionary is as follows:
                {
                    'latitude': float,
                    'longitude': float,
                    'forecasts': list[dict]
                }
                The 'forecasts' list contains dictionaries with the following structure:
                {
                    'start_date': str,
                    'end_date': str,
                    'temperature': float,
                    'humidity': float
                }
        """
        forecasts = []
        for latitude, longitude in locations:
            url = f"{self.base_url}/{start_date}T00:00:00Z--{end_date}T00:00:00Z:PT1H/t_2m:C,relative_humidity_2m:p/{latitude},{longitude}/json?model=mix"
            headers = {"Content-Type": "application/json"}
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                weather_data = response.json()
                weather_list = []

                # Process temperature and humidity data for each day
                temperature_data = next((param for param in weather_data['data'] if param['parameter'] == 't_2m:C'), None)
                humidity_data = next((param for param in weather_data['data'] if param['parameter'] == 'relative_humidity_2m:p'), None)

                if temperature_data and humidity_data:
                    for temp_coord, hum_coord in zip(temperature_data['coordinates'][0]['dates'], humidity_data['coordinates'][0]['dates']):
                        date = temp_coord['date']
                        weather_list.append({
                            'start_date': date,
                            'end_date': date,
                            'temperature': temp_coord['value'],
                            'humidity': hum_coord['value'],
                        })

                    forecasts.append({
                        'latitude': latitude,
                        'longitude': longitude,
                        'forecasts': weather_list
                    })
            else:
                print(f"Error: {response.status_code}")
                forecasts.append(None)

        return forecasts