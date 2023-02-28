import json
import numpy as np

import utils.constants as c
from utils.requester import Requester

def scrap_wine_data(country_code):
    output_file = 'out/' + country_code
    start_page = 1

    # Instantiates a wrapper over the `requests` package
    r = Requester(c.BASE_URL)

    # Defines the payload, i.e., filters to be used on the search
    payload = {
        "country_codes[]": country_code,
        "min_rating": 3.6,
    }

    # Performs an initial request to get the number of records (wines)
    res = r.get('explore/explore?', params=payload)
    n_matches = res.json()['explore_vintage']['records_matched']
    wines_per_page = 25
    n_pages = int(np.ceil(n_matches / wines_per_page))

    print(f'[{country_code}] Number of matches: {n_matches}', end='\r')

    # Creates a dictionary to hold the data
    data = {}
    data['wines'] = []
    data['wines_minimal'] = []

    # Iterates through the amount of possible pages
    for i in range(start_page, max(1, int(n_matches / c.RECORDS_PER_PAGE)) + 1):
        print(f'[{country_code}] Number of matches: {n_matches} - Page {i}/{n_pages}', end='\r')

        # Performs the request and scraps the URLs
        res = r.get('explore/explore', params=payload)
        matches = res.json()['explore_vintage']['matches']

        # Iterates over every match
        for match in matches:
            # Gathers the wine-based data
            wine = match['vintage']['wine']

            # Popping redundant values
            if wine['style']:
                wine['style'].pop('country', None)
                wine['style'].pop('region', None)
                wine['style'].pop('grapes', None)

            # print(f'Scraping data from wine: {wine["name"]}')

            # Appends current match to the dictionary
            data['wines'].append(wine)

            # Gathers the full-taste profile from current match
            res = r.get(f'wines/{wine["id"]}/tastes')
            tastes = res.json()

            # Replaces the taste profile
            data['wines'][-1]['taste'] = tastes['tastes']

            # Appends match to the minimal dictionary
            data['wines_minimal'].append({
                'id': wine['id'],
                'name': wine['name'],
                'type_id': wine['type_id'],
                'region': {
                    'id': wine['region']['id'],
                    'name': wine['region']['name'],
                    'country_code': wine['region']['country']['code'],
                },
                'winery': {
                    'id': wine['winery']['id'],
                    'name': wine['winery']['name'],
                }
            })

    print(f'[{country_code.upper()} DONE] - Number of matches: {n_matches} - Number of pages: {n_pages}')

    # Output .json file
    with open(f'{output_file}.json', 'w') as file_detailed:
        # Dumps the data
        json.dump(data['wines'], file_detailed)
    file_detailed.close()

    # Output minimal .json file
    with open(f'{output_file}_minimal.json', 'w') as file_minimal:
        # Dumps the data
        json.dump(data['wines_minimal'], file_minimal)
    file_minimal.close()

if __name__ == '__main__':
    with open('countries.json') as f:
        countries = json.load(f)

        for country in countries:
            scrap_wine_data(country)