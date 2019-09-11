"""
This file contains modules that can be used to fetch the data from the Open Air
Quality API. Defines a class that can be used to fetch the data and return it
in an appropriate format.
"""

import requests
import json
import pandas as pd


class OpenAQFetcher:
    """
    This class defines a template for an object that can fetch Open Air Quality
    Has the following attributes:

    """

    def __init__(self, api_url='https://api.openaq.org/v1'):
        """
        The class constructor. Can take in an alternative URL
        """
        self.api_url = api_url

    def get_city_list(self):
        url = self.api_url + '/cities'
        print(url)
        response = requests.get(url)
        try:
            assert response.status_code == 200
        except AssertionError:
            print('Bad URL!')

        resp_json = json.loads(response.content)
        print(resp_json)


test_fetcher = OpenAQFetcher()
test_fetcher.get_city_list()
