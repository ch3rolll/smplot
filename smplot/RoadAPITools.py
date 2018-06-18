import googlemaps
from googlemaps import convert
import math
from smplot import smplot
import webbrowser, os
import urllib
from PIL import Image
from selenium import webdriver 

def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

## https://stackoverflow.com/questions/6048975/google-maps-v3-how-to-calculate-the-zoom-level-for-a-given-bounds/13274361#13274361

## Calculate zoom value based on 
## https://developers.google.com/maps/documentation/javascript/coordinates
def zoom(mapPixel, worldPixel, fraction):
    return math.floor(math.log(mapPixel / worldPixel / fraction)/math.log(2))

## Calculate Mercator projector scale for a given latitude
def lat2Rad (lat):
    sin = math.sin(lat * math.pi / 180)
    radX2 = math.log(( 1 + sin) / (1 - sin)) / 2
    return max(min(radX2, math.pi), -math.pi) / 2


def getBoundsZoomLevel (lats, longs, map_h = 256, map_w = 256):
    world_h = 256
    world_w = 256
    zoom_max = 21
    
    min_lats = min(lats)
    max_lats = max(lats)
    
    
    # Based on Mercator projection, the latFraction is calculated
    latFraction = (lat2Rad (max_lats) - lat2Rad(min_lats)) / math.pi
    longDiff = max(longs) - min(longs)
    
    longFraction = (longDiff + 360 if (longDiff < 0) else longDiff) / 360
    
    latZoom = zoom(map_h,world_h, latFraction)
    longZoom = zoom(map_w,world_w, longFraction)
    
    return min(latZoom, longZoom, zoom_max)

def drawRoad(path, line_size = 2, image_h = 256, image_w = 256, interpolate=True):

    road_lats, road_lons = findPathFromRoad (path, interpolate=interpolate)

    center_lat = mean(road_lats)
    center_long = mean(road_lons)
        
    # Place map
    zoom = getBoundsZoomLevel (road_lats, road_lons, map_h = image_h, map_w = image_w)
    smap = smplot.GoogleSatelliteMapPlot(center_lat, center_long, zoom, map_h = image_h, map_w = image_w)

    # gmap.plot(road_lats, road_lons, 'cornflowerblue', edge_width=10)
    smap.scatter(road_lats, road_lons, size = line_size, marker=False)

    # Draw
    filename = 'my_map.html'
    smap.draw(filename)
    
    # Open the local html file
    url = 'file://' + os.path.realpath(filename)
    # webbrowser.open(url)
    return url


def findPathFromRoad (path, interpolate=True):
    gmaps = googlemaps.Client(key='AIzaSyBiRlZF9HEyYGEFTcxOTWJ6LYk1gzZ-QnE')
    
    _ROADS_BASE_URL = "https://roads.googleapis.com"
    
    params = {"path": convert.location_list(path),
              "interpolate": interpolate}
    
    response_result = gmaps._request("/v1/snapToRoads", params,
                       base_url=_ROADS_BASE_URL,
                       accepts_clientid=False,
                       extract_body=_roads_extract)
    
    # Check if there is a warning error there
    status_result = response_result.get("warningMessage", [])
    
    if status_result:
        print (status_result)
    
    road_result = response_result.get("snappedPoints", [])
    
    
    # Polygon
    road_lats = []
    road_lons = []

    for r in road_result:
        road_lats.append (r['location']['latitude'])
        road_lons.append (r['location']['longitude'])
    
    return road_lats, road_lons


## A function from Google Maps Python API
def _roads_extract(resp):
    """Extracts a result from a Roads API HTTP response."""

    try:
        j = resp.json()
    except:
        if resp.status_code != 200:
            raise googlemaps.exceptions.HTTPError(resp.status_code)

        raise googlemaps.exceptions.ApiError("UNKNOWN_ERROR",
                                             "Received a malformed response.")

    if "error" in j:
        error = j["error"]
        status = error["status"]

        if status == "RESOURCE_EXHAUSTED":
            raise googlemaps.exceptions._OverQueryLimit(status,
                                                        error.get("message"))

        raise googlemaps.exceptions.ApiError(status, error.get("message"))

    if resp.status_code != 200:
        raise googlemaps.exceptions.HTTPError(resp.status_code)

    return j


def downloadImage(path, image_h = 256, image_w = 256, interpolate=True):
            
    #Create a new image of the size require
    map_img = Image.new('RGB', (image_w,image_h))

    url = drawRoad(path, image_h = image_h, image_w = image_w, interpolate=interpolate)

     # open in webpage
    driver = webdriver.Chrome()
    driver.get(url)
    save_name = '00.png'       
    driver.get_screenshot_as_file(save_name) 
    driver.quit()

    # crop as required
    img = Image.open(save_name)
    box = (0, 0, 2 * image_w, 2 * image_h)
    area = img.crop(box)
    area.save(save_name)
    
    return map_img
    