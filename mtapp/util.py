from math import radians, cos, sin, asin, sqrt


def get_distance(result, lat, lng):
    R = 6371000  # Radius of earth in kilometers
    dest_lat = result['geometry']['location']['lat']
    dest_lng = result['geometry']['location']['lng']

    lat1, lng1, lat2, lng2 = map(radians, map(float, [dest_lat, dest_lng, lat, lng]))

    # haversine formula
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
    c = 2 * asin(sqrt(a))
    distance = f'{(c * R):.0f}'
    return f'{distance} m'


def item_mapper(result, lat, lng):
    return {'id': result['id'],
            'name': result['name'],
            'address': result['vicinity'],
            'distance': get_distance(result, lat, lng)}
