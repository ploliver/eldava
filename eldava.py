#%%
import folium
import random
import colorsys
import subprocess, os, platform
import pandas as pd
import gpxpy

#%% define functions
def random_color():
    h,s,l = random.random(), 0.5 + random.random()/2.0, 0.4 + random.random()/5.0
    r,g,b = [int(256*i) for i in colorsys.hls_to_rgb(h,l,s)]
    return '#%02X%02X%02X' % (r,g,b)

def importFile(filename):
    file = open(f"data/{filename}", "r")
    gpx = gpxpy.parse(file)
    
    route = []

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                route.append({
                    'latitude': point.latitude,
                    'longitude': point.longitude,
                    'elevation': point.elevation
                })
    
    data = pd.DataFrame(route)
    trackname = gpx.tracks[0].name
    time_bounds = gpx.get_time_bounds()
    length = gpx.length_3d()

    return data, trackname, time_bounds, length

def addRouteToMap(filename):
    data, trackname, time_bounds, length = importFile(filename)
    coordinates = [tuple(x) for x in data[['latitude', 'longitude']].to_numpy()]
    start_time, end_time = time_bounds.start_time.strftime("%d/%m/%y, %H:%M:%S"), time_bounds.end_time.strftime("%d/%m/%y, %H:%M:%S")
    folium.PolyLine(coordinates, weight=6, smooth_factor=1.3, color=random_color(), tooltip=folium.map.Tooltip(f"<p><b>{trackname} · {round(length/1000,3)} km</b></p> <p>{start_time} - {end_time}", style="font-size:2rem;", sticky=False), opacity=0.8).add_to(route_map)

# %% create map centered around elda with current screen width and height
route_map = folium.Map(
    location=[38.48 , -0.785930],
    zoom_start=15.2,
    tiles='CartoDBPositron',
)

#%% add all routes to the map
filenames = next(os.walk("data/"), (None, None, []))[2]
for filename in filenames:
    if not filename.startswith("."):
        addRouteToMap(filename)

#%% save map in html, then open it with default browser (or at least, try to).
exportname = "map.html"
route_map.save(exportname)

#%% change tab name
fin = open(exportname, "r+")
lines = fin.readlines()
lines[3] = "    <title>RTPElda</title> \n"
fin.writelines(lines)
fin.close()

#%% open file when finished
if platform.system() == 'Darwin':       # macOS
    subprocess.call(('open', exportname))
elif platform.system() == 'Windows':    # Windows
    os.startfile(exportname)
else:                                   # linux variants
    subprocess.call(('xdg-open', exportname))
