########################################################################################################################
#  Method: get_ltng24hr(bbox, outputpath, csvname)                                                                     #
#                                                                                                                      #
#  Description: Obtains 24-hour lightning strike data (points) from the BLM lightning service                          #
#                                                                                                                      #
#  Variables:                                                                                                          #
#              bbox: (list) a bounding box in the format [xmin, ymin, xmax, ymax]                                      #
#              outputpath: (str) path to .csv file that will be created                                                #
#              csvname: (str) csv output file name                                                                     #
#                                                                                                                      #
#  Returns: None. Utility function. See output file                                                                    #
#                                                                                                                      #
########################################################################################################################

import requests
import csv
import time

def get_ltng24hr(bbox, outputpath, csvname):
    # Base URLs
    agol_token_url = 'https://egp.nwcg.gov/arcgis/tokens'
    blm_lightning_24hr_url = "https://egp.nwcg.gov/arcgis/rest/services/FireCOP/LightningStrikes/MapServer/1"
    referer = 'http://dnr.wa.gov'

    # Creating a token payload
    token_payload = {
        'client': 'referer',
        'f': 'json',
        'referer': referer,
        'username': 'kirkdavis',
        'password': 'WAdnregplogin3!',
        'expiration': 60
        }

    # Getting a token to make requests
    requested_token = requests.post(agol_token_url, params=token_payload)
    token_str = requested_token.json()['token']
    print("Token returned: {}".format(token_str))

    # Change input geometry here, spatial reference is WGS84
    geometry = {"xmin": bbox[0], "ymin": bbox[1], "xmax": bbox[2], "ymax": bbox[3], "spatialReference": {"wkid": 4326}}

    # Defining request parameters
    request_params = {
        'where': '1=1',
        'token': token_str,
        'returnCountOnly': 'false',
        'geometry': geometry,
        }

    # Make the request
    # There is an issue where passing the entire payload via data/params/json messes up the geometry and returns the
    # entire U.S. strikes. This is sometimes like 70K-150K points. This creates a bad time. The work around is just to
    # do string formatting.
    s = requests.Session()
    s.headers.update({'referer': referer})
    r = s.post(blm_lightning_24hr_url + "/query?where={}&outFields=TimeStamp,AgeInHours,Polarity,Latitude,Longitude&geometry={}&token={}&returnGeometry=false"
                                        "&f=json&returnCountOnly={}".format(request_params['where'], request_params['geometry'],
                                                         request_params['token'], request_params['returnCountOnly']))

    # # Store the results
    results = r.json()
    # print("Resulting JSON: {}".format(results))

    # Create CSV file
    output = open(outputpath + csvname, 'w')
    csvwriter = csv.writer(output)

    # Write headers
    csvwriter.writerow(["STRIKE_ID", "TIMESTAMP", "AGEINHOURS", "POLARITY", "LATITUDE", "LONGITUDE"])

    # Write data
    id_count = 0
    for x in results['features']:
        csvwriter.writerow([id_count, x['attributes']['TimeStamp'], x['attributes']['AgeInHours'], x['attributes']['Polarity'], x['attributes']['Latitude'], x['attributes']['Longitude']])
        id_count += 1
    output.close()

    return print("Finished writing CSV. Check output at " + outputpath + csvname)

# Call above function, read documentation for inputs
# This bbox is just WA-ish
get_ltng24hr([-124.8313444159, 45.4387975478, -116.7685442023,49.1577895452], "/Users/joshuaclark/Desktop/repos/Lightning/", time.strftime("%Y%m%d%H%M") + 'strikes.csv')


