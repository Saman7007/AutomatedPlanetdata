#%%
#----------------Set up API Key-----------------#  
import os
import json
import requests
from requests.auth import HTTPBasicAuth

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
# Define the directory where images will be downloaded
DOWNLOAD_DIR = str(os.getcwd()) + '/data'

# Create the directory if it does not exist
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

def download_image(image_id, download_dir=DOWNLOAD_DIR):
    id_url = f'https://api.planet.com/data/v1/item-types/{item_type}/items/{image_id}/assets'

    # Returns JSON metadata for assets in this ID.
    result = requests.get(id_url, auth=HTTPBasicAuth(API_KEY, ''))
    assets = result.json()

    # Check the status of the asset and activate if necessary
    asset = assets['ortho_analytic_4b']
    if asset['status'] != 'active':
        activation_link = asset['_links']['activate']
        requests.get(activation_link, auth=HTTPBasicAuth(API_KEY, ''))

        # Poll the activation status
        while asset['status'] != 'active':
            result = requests.get(id_url, auth=HTTPBasicAuth(API_KEY, ''))
            asset = result.json()['ortho_analytic_4b']
    
    # Download the asset
    download_link = asset['location']
    img_data = requests.get(download_link, auth=HTTPBasicAuth(API_KEY, ''))

    # Ensure the directory exists
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    file_path = os.path.join(download_dir, f"{image_id}.tif")
    with open(file_path, 'wb') as f:
        f.write(img_data.content)
    print(f"Downloaded image {image_id} to {download_dir}")



#%%
# Loop through all image IDs and download each one
for image_id in image_ids:
    download_image(image_id)


