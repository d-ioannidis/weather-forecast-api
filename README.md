# Weather Forecast API

# Project Structure

The project is structured as follows:

```bash
.
├── app
│   ├── core
│   │   ├── __init__.py
│   │   ├── database.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── forecast.py
│   ├── routers
│   │   ├── __init__.py
│   │   ├── forecast.py
│   ├── services
│   │   ├── __init__.py
│   │   ├── forecast.py
│   ├── db
│   │   ├── weather.db
│   ├── main.py
│   ├── __init__.py
│   ├── requirements.txt
│   ├── .env
│   ├── .gitignore
│   └── README.md
```

- **app**: Contains the main FastAPI application.
- **core**: Contains the core logic of the application.
- **models**: Contains the data models used by the application.
- **routers**: Contains the FastAPI routers for the application.
- **services**: Contains the service classes used by the application.
- **db**: Contains the database schema for the application.
- **main.py**: The main entry point of the application.
- **requirements.txt**: Lists the required Python packages for the application.
- **.env**: Contains environment variables used by the application.
- **.gitignore**: Lists files to be ignored by Git.
- **README.md**: Contains project documentation.

# Setup

To set up the environment, run the following commands:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

- **venv**: Creates a virtual environment named "venv".
- **source venv/bin/activate**: Activates the virtual environment.
- **pip install -r requirements.txt**: Installs the required Python packages.

## Running the Server

To run the FastAPI server, use the following command:

```bash
# Development
fastapi dev main.py

# Production
fastapi run main.py
```

- **fastapi dev main.py**: Runs the FastAPI server in development mode.
- **fastapi run main.py**: Runs the FastAPI server in production mode.

## API Documentation

The Weather Forecast API provides a set of endpoints to manage and retrieve weather forecast data. The preferred way to test these endpoints is through the integrated Swagger UI provided by FastAPI. Swagger UI is automatically available when running the FastAPI server and can be accessed by visiting `http://localhost:8000/docs` in your web browser.

There are two ways to make use of the API:
- One way is to access it locally through localhost `http://localhost:8000/docs`.
- Another way is to visit the domain `https://weather.ioannidis.dev/docs`.

Both of these two links are interchangeable and lead to the same documentation.

### Available Endpoints

- **`GET /forecast`**: Retrieve the current weather forecast for a specific location.
  - **Query Parameters**:
    - `latitude` (float): Latitude in decimal degrees.
    - `longitude` (float): Longitude in decimal degrees.

- **`POST forecast/saveLocation`**: Save a new forecast location.
  - **Request Body**:
    - `latitude` (float): Latitude of the location.
    - `longitude` (float): Longitude of the location.

- **`POST forecast/saveForecast`**: Save a new forecast.
  - **Request Body**:
    - `forecast` (str): The forecast data in JSON format.

- **`GET forecast/latestForecasts`**: Get the latest forecast for each location.
  
- **`POST forecast/saveForecastData`**: Save all forecast data for multiple locations.

- **`GET forecast/averageTemperature`**: Get the average temperature of the last 3 forecasts for each location for every day.

- **`GET forecast/listLocations`**: Get a list of all locations.

- **`GET forecast/topLocations`**: Retrieve the top `n` locations ranked by a specified weather metric.
  - **Query Parameters**:
    - `metric` (str): The weather metric for ranking (e.g., temperature, humidity).
    - `n` (int): Number of top locations to retrieve.

### How to Use Swagger UI

1. **Run the FastAPI Server**: Make sure your FastAPI server is running by following the instructions in the "Running the Server" section above.

2. **Access Swagger UI**: Open your web browser and navigate to `http://localhost:8000/docs` (or `https://weather.ioannidis.dev/docs` if using the Hetzner server).

3. **Explore Endpoints**: The Swagger UI provides an interactive interface where you can see the available endpoints, their descriptions, and example requests.

4. **Test Endpoints**: You can test the endpoints directly from the Swagger UI by filling in the required parameters and sending requests. The responses will be displayed in the UI.

Swagger UI is a powerful tool to explore and test your API endpoints effortlessly, ensuring that they work as expected.

## Examples of Usage through Curl

### Get Forecast

```bash
curl "http://localhost:8000/forecast?latitude=40.6401&longitude=22.9444"
```

### Get Latest for locations

```bash
curl -X 'GET' \
  'http://localhost:8000/forecast/latestForecasts' \
  -H 'accept: application/json'
```

### Get Average Temperature

```bash
curl -X 'GET' \
  'http://localhost:8000/forecast/averageTemperature' \
  -H 'accept: application/json'
```

### Get List of Locations

```bash
curl -X 'GET' \
  'http://localhost:8000/forecast/listLocations' \
  -H 'accept: application/json'
```

### Get Top Locations

```bash
curl -X 'GET' \
  'http://localhost:8000/forecast/topLocations?metric=temperature&n=5' \
  -H 'accept: application/json'
```

### Save Location

```bash
curl -X 'POST' \
  'http://localhost:8000/forecast/saveLocation' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "latitude": 40.6401,
    "longitude": 22.9444
  }'
```

### Save Forecast

```bash
curl -X 'POST' \
  'http://localhost:8000/forecast/saveForecast' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
      "temperature": 20.0,
      "humidity": 50.0,
      "start_date": "2023-08-01T00:00:00Z",
      "end_date": "2023-08-31T00:00:00Z",
      "location_id": 1
    }
```

### Save Forecast Data

```bash
curl -X 'POST' \
  'http://localhost:8000/forecast/saveForecastData' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
```

Instead of using a public cloud service such AWS or Azure, I made use of a combination between Docker, Caddy and Cloudflare DNS to self-host the application on a Hetzner VPS. 

One reason is that a public cloud service ask for some sensitive data, such as credit card information, that I do not want to share due to the possible
fees that may be associated with it as well as any other privacy concerns.

Following, is a guide to deploy the application on a Hetzner VPS.

## Deployment Guide: FastAPI + SQLite on Hetzner with Caddy & Cloudflare DNS

1. **Provision VPS**

   - On Hetzner Cloud, made use of an Ubuntu 22.04 server.
   - To restrict access to unwanted traffic on the VPS, used an SSH configuration and enabled UFW firewall, allowing only ports 22, 80, and 443.

2. **Install Docker & Compose**

   - Followed Docker’s official Ubuntu installation instructions to install `docker-ce`, add my user to the `docker` group, and enable the `docker` service.

3. **Prepare DNS & SSL**

   - In Cloudflare, created a record (`weather.ioannidis.dev`) pointing to the VPS’s public IPv4.
   - Generated a Cloudflare API token scoped to DNS-edit permissions.

4. **Clone & Configure Project**

   - Pulled my FastAPI repo (with all the files, e.g. `forecast.py` from services, routers, and models,`Dockerfile`, `requirements.txt`, `etc`).
   - Ensured the code reads `METEOMATICS_API_USERNAME`, `METEOMATICS_API_PASSWORD`, and `DATABASE_URL` from environment variables.

5. **Compose File & Caddy Proxy**

   - Wrote `docker-compose.yml` which defines two services:
     - **api**: builds the FastAPI image, mounts a Docker volume for SQLite persistence, and injects environment variables.
     - **caddy**: uses the publicly maintained `lucaslorentz/caddy-docker-proxy` image, configured to automatically obtain TLS certs using Cloudflare DNS-01 challenge and reverse-proxy `api:8000`.
   - Declared and attached both services to an external Docker network (`caddy-net`) to isolate ingress traffic.

6. **Launch & Verify**

   - Ran `docker compose up -d` to build images and start containers.
   - Kept a watch on logs with `docker compose logs -f` to confirm that Caddy successfully requested certificates and to ensure FastAPI came online.
   - Visited `https://weather.ioannidis.dev/docs` to test the deployed API and validate the endpoints.

7. **Maintenance**

   - Updated code to fetch new commits and rebuild the FastAPI image by rebuilding just the `api` service (`docker compose build api`), and then `docker compose up -d api` to restart the container.
   - SQLite data persists in the named volume, and Caddy auto-renews certs via Cloudflare.