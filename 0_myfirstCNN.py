import os, random
import geopandas as gpd
import rasterio
from rasterio.windows import Window
from shapely.geometry import box
from shapely.geometry import Point
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# making my first cnn!
# first, I want to read in my regions
regions_file = r"C:\Users\X\Documents\uCalgary\DeepLearningGroup_2025\data\regions\regions.gpkg"

# Load as GeoDataFrame
regions = gpd.read_file(regions_file)
print(regions.head())

# I want to set a random seed
random.seed(42)
np.random.seed(42)

# Function to generate N random points within a polygon
def generate_random_points_in_polygon(polygon, num_points):
    points = []
    minx, miny, maxx, maxy = polygon.bounds
    while len(points) < num_points:
        random_point = Point([random.uniform(minx, maxx), random.uniform(miny, maxy)])
        if polygon.contains(random_point):
            points.append(random_point)
    return points

# Create a new GeoDataFrame to store the points
random_points = []

for idx, row in regions.iterrows():
    poly = row.geometry
    points = generate_random_points_in_polygon(poly, 50)
    for pt in points:
        random_points.append({'geometry': pt, 'region_id': idx})  # add region_id or any attribute

points_gdf = gpd.GeoDataFrame(random_points, crs=regions.crs)

print(points_gdf.head())

# for now, hard coding the size of the patch.
# since the ortho is 0.015 m, I want a box of 7.68 x 7.68 m to make
# a patch of 512 x 512 pixels
box_size = 7.68  # meters
half_size = box_size / 2

# Create boxes around each point
points_gdf['patch'] = points_gdf.geometry.apply(
    lambda pt: box(pt.x - half_size, pt.y - half_size, pt.x + half_size, pt.y + half_size)
)

boxes_gdf = gpd.GeoDataFrame(points_gdf[['region_id']], geometry=points_gdf['patch'], crs=points_gdf.crs)
# Export GeoDataFrame to GPKG
boxes_gdf.to_file(r'C:\Users\X\Documents\uCalgary\DeepLearningGroup_2025\data\training\random_boxes.gpkg', driver="GPKG")

# now, I want to read in my orthos

# Define folder path
ortho_folder = r"C:\Users\X\Documents\uCalgary\DeepLearningGroup_2025\data\orthos"

# List all .tif files
ortho_files = [os.path.join(ortho_folder, f) for f in os.listdir(ortho_folder) if f.lower().endswith('.tif')]

# Print the list to verify
print(f"Found {len(ortho_files)} orthos:")
for f in ortho_files:
    print(f)


