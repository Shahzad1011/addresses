import gspread
from oauth2client.service_account import ServiceAccountCredentials
import googlemaps
import math
import json
import requests

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in kilometers

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

def run_script():
    # Set up Google Sheets API credentials
    scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    creds_url = 'https://raw.githubusercontent.com/Shahzad1011/addresses/main/creds.json'
    creds_json = requests.get(creds_url).text
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    # Fetch addresses from Google Sheet
    sheet_id = '1pcJjI3iTMI4PupRW8_A90CaTJ1TLcSPH2QUoWvAyfkk'
    worksheet_name = 'Sheet1'
    worksheet = client.open_by_key(sheet_id).worksheet(worksheet_name)
    addresses = worksheet.col_values(1)[1:]  # Fetch values from column A starting from row 2

    # Set up Google Maps Geocoding API client
    gmaps = googlemaps.Client(key='AIzaSyCoM0UnGPiQeY3Y_dwLMqhAqWnEhCML5ss')

    nearest_addresses = []
    for address in addresses:
        # Retrieve latitude and longitude for the current address
        geocode_result = gmaps.geocode(address)
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            current_lat, current_lng = location['lat'], location['lng']

            # Retrieve nearby places for the current address
            places_result = gmaps.places_nearby(location=(current_lat, current_lng), radius=1000)
            nearby_places = places_result.get('results', [])

            # Sort nearby places by distance
            nearby_places.sort(key=lambda x: haversine(current_lat, current_lng, x['geometry']['location']['lat'], x['geometry']['location']['lng']))

            # Get the ten nearest addresses
            nearest_addresses.extend([place['vicinity'] for place in nearby_places[:10]])

    return nearest_addresses

# Run the script
result = run_script()
for address in result:
    print(address)
