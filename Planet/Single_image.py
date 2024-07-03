#%%
#----------------Set up API Key-----------------#  
import os

# if your Planet API Key is not set as an environment variable, you can paste it below
if os.environ.get('PL_API_KEY', ''):
    API_KEY = os.environ.get('PL_API_KEY', '')
else:
    API_KEY = 'PLAKe10e401cd0fe4822a65c0f6dbb8b5a42'


# %%
#-----------------Define RoI-----------------#
# for this example, we will use a simple bounding box
geojson_geometry = {
  "type": "Polygon",
  "coordinates": [
    [ 
      [-121.59290313720705, 37.93444993515032],
      [-121.27017974853516, 37.93444993515032],
      [-121.27017974853516, 38.065932950547484],
      [-121.59290313720705, 38.065932950547484],
      [-121.59290313720705, 37.93444993515032]
    ]
  ]
}
# %%
#-----------------Create Filters-----------------#
# get images that overlap with our AOI 
geometry_filter = {
  "type": "GeometryFilter",
  "field_name": "geometry",
  "config": geojson_geometry
}

# get images acquired within a date range
date_range_filter = {
  "type": "DateRangeFilter",
  "field_name": "acquired",
  "config": {
    "gte": "2016-08-31T00:00:00.000Z",
    "lte": "2016-09-01T00:00:00.000Z"
  }
}

# only get images which have <50% cloud coverage
cloud_cover_filter = {
  "type": "RangeFilter",
  "field_name": "cloud_cover",
  "config": {
    "lte": 0.5
  }
}

# combine our geo, date, cloud filters
combined_filter = {
  "type": "AndFilter",
  "config": [geometry_filter, date_range_filter, cloud_cover_filter]
}
# %%
#-----------------Search: Items and Assets-----------------#
import json
import requests
from requests.auth import HTTPBasicAuth

item_type = "PSScene"

# API request object
search_request = {
  "item_types": [item_type], 
  "filter": combined_filter
}

# fire off the POST request
search_result = \
  requests.post(
    'https://api.planet.com/data/v1/quick-search',
    auth=HTTPBasicAuth(API_KEY, ''),
    json=search_request)

geojson = search_result.json()

# let's look at the first result
print(list(geojson.items())[1][1][0])

# %%
# extract image IDs only
image_ids = [feature['id'] for feature in geojson['features']]
print(image_ids)
# %%
# For demo purposes, just grab the first image ID
id0 = image_ids[0]
id0_url = 'https://api.planet.com/data/v1/item-types/{}/items/{}/assets'.format(item_type, id0)

# Returns JSON metadata for assets in this ID. Learn more: planet.com/docs/reference/data-api/items-assets/#asset
result = \
  requests.get(
    id0_url,
    auth=HTTPBasicAuth(API_KEY, '')
  )

# List of asset types available for this particular satellite image
print(result.json().keys())
# %%
# -----------------Activate and Download the Asset-----------------#
# This is "inactive" if the "ortho_analytic_4b" asset has not yet been activated; otherwise 'active'
print(result.json()['ortho_analytic_4b']['status'])
# %%
# Parse out useful links
links = result.json()[u"ortho_analytic_4b"]["_links"]
self_link = links["_self"]
activation_link = links["activate"]

# Request activation of the 'ortho_analytic_4b' asset:
activate_result = \
  requests.get(
    activation_link,
    auth=HTTPBasicAuth(API_KEY, '')
  )
  
print(activate_result.status_code)
# %%
activation_status_result = \
  requests.get(
    self_link,
    auth=HTTPBasicAuth(API_KEY, '')
  )
    
print(activation_status_result.json()["status"])
# %%
# Image can be downloaded by making a GET with your Planet API key, from here:
download_link = activation_status_result.json()["location"]
print(download_link)
# %%
