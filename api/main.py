from fastapi import FastAPI, Request, HTTPException
import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv('API_KEY')

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello World!"}

# Function to get client IP address (considering potential proxy environments)
def get_client_ip(request: Request):
    remote_addr = request.client.host
    if request.headers.get('X-Forwarded-For', None):
        proxy_ips = request.headers.get('X-Forwarded-For').split(',')
        remote_addr = proxy_ips[0].strip()  # Use the first IP from the list
    return remote_addr


# Function to get the location, and temperature of the location data using IP address
def get_location_and_temperature(ip_address):
    url = "https://weatherapi-com.p.rapidapi.com/current.json"
    querystring = {"q":ip_address}
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "weatherapi-com.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        data = response.json()
        location = data['location']['name']
        temperature = data['current']['temp_c']
        return location, temperature
    else:
        raise HTTPException(status_code=500, detail="Failed to retrieve location and temperature data")


@app.get("/api/{greeting}")
def get_info(request: Request, greeting:str = "hello", visitor_name:str = "mark"):
    client_ip = get_client_ip(request)
    try:
        city, temperature = get_location_and_temperature(client_ip)
        if city and temperature:
            return {
                    "client_ip": client_ip,
                    "location": f"{city}",
                    "greeting": f"{greeting.title()}, {visitor_name.title()}!, the temperature is {int(temperature)} degrees Celsius in {city}",
                }
        else:
            return {
                "client_ip": client_ip,
                "location": "Unavailable",
                "temperature": "Unavailable",
            }
    except HTTPException as e:
        return e.detail

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    # uvicorn main:app --host 0.0.0.0 --port 8000 --proxy-headers