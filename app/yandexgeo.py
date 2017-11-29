import requests


def find_locations(lat, long, count=8):
    locations = []

    url = 'https://geocode-maps.yandex.ru/1.x/?geocode=%f,%f&kind=locality&lang=en_US&format=json&results=%i' % \
          (long, lat, count)

    print(url)

    r = requests.get(url)
    if r.status_code == 200:
        geo = r.json()

        try:
            if 'response' in geo:
                response = geo['response']
                found = int(response['GeoObjectCollection']['metaDataProperty']['GeocoderResponseMetaData']['found'])
                if found > 0:
                    for item in response['GeoObjectCollection']['featureMember']:
                        locations.append(item['GeoObject']['name'])
        except:
            pass
    else:
        print('Failed to find location at (%f, %f): %i' % (lat, long, r.status_code))

    return locations


if __name__ == '__main__':
    long = 43.996013
    lat = 56.281357

    loc = find_locations(lat, long)
    if loc:
        # obj = {
        #    'name': loc[0],
        #    'lat': lat,
        #    'long': long,
        # }
        # print(obj)
        print(loc)
    else:
        print('Where are you, friend?')
