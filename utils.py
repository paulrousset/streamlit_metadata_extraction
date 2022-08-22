from datetime import datetime
from PIL.ExifTags import TAGS, GPSTAGS
from PIL import Image

# Function to get human readable time
def get_readable_time(mytime):
    return datetime.fromtimestamp(mytime).strftime("%Y-%m-%d-%H-%M")


# Functions to get Image GeoTags
def get_exif(filename):
    exif = Image.open(filename)._getexif()
    new_exif = {}
    if exif is not None:
        for key, value in exif.items():
            name = TAGS.get(key, key)
            new_exif[name] = exif[key]

        if "GPSInfo" in exif:
            for key in exif["GPSInfo"].keys():
                name = GPSTAGS.get(key, key)
                new_exif["GPSInfo"][name] = exif["GPSInfo"][key]

    return new_exif


def get_decimal_coordinates(info):
    for key in ["Latitude", "Longitude"]:
        if "GPS" + key in info and "GPS" + key + "Ref" in info:
            e = info["GPS" + key]
            ref = info["GPS" + key + "Ref"]
            info[key] = (
                e[0][0] / e[0][1] + e[1][0] / e[1][1] / 60 + e[2][0] / e[2][1] / 3600
            ) * (-1 if ref in ["S", "W"] else 1)

    if "Latitude" in info and "Longitude" in info:
        return [info["Latitude"], info["Longitude"]]


# def get_coordinates(info):
#     for key in ["Latitude", "Longitude"]:
#         if "GPS" + key in info and "GPS" + key + "Ref" in info:
#             e = info["GPS" + key]
#             ref = info["GPS" + key + "Ref"]
#             info[key] = (
#                 str(e[0][0] / e[0][1])
#                 + "°"
#                 + str(e[1][0] / e[1][1])
#                 + "′"
#                 + str(e[2][0] / e[2][1])
#                 + "″ "
#                 + ref
#             )
#
#     if "Latitude" in info and "Longitude" in info:
#         return [info["Latitude"], info["Longitude"]]
