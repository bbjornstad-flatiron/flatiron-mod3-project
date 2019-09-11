"""
This file contains modules that can be used to fetch the data from the EPA's
Air Quality Services API. Defines a class that can be used to fetch the data and 
return it in an appropriate format.
"""

import requests
import json
import pandas as pd


class AQSFetcher:
    """
    This class defines a template for an object that can fetch EPA open
    air quality data. Has the following attributes.
    """

    def __init__(self, email, key, api_url='https://aqs.epa.gov/data/api'):
        """
        The class constructor. Can take in an alternative URL
        """
        self.email = email
        self.key = key
        self.api_url = api_url
        self.stub = f'?email={self.email}&key={self.key}'

    def get_cbsas(self):
        url = self.api_url + '/list/cbsas' + self.stub
        response = requests.get(url)
        try:
            assert response.status_code == requests.codes.ok
        except AssertionError:
            print('Bad URL!')

        json_data = json.loads(response.content)

    def get_state_codes(self):
        """
        Gets a list of states and their associated codes that can be used to
        construct additional queries.
        """
        url = self.api_url + '/list/states' + self.stub
        response = requests.get(url)
        try:
            assert response.status_code == requests.codes.ok

            json_data = json.loads(response.content)['Data']
            df = pd.DataFrame.from_records(json_data)
            df.rename(
                columns={'value_represented': 'state_name'}, inplace=True)
            return df

        except AssertionError:
            print('Bad URL!')

    def get_counties_by_state(self, state):
        """
        Gets a list of counties for the given state, and their associated
        county ids. Takes in a state id as an integer.
        """
        url = self.api_url + '/list/countiesByState' + self.stub
        url += f'&state={state}'
        response = requests.get(url)

        try:
            assert response.status_code == requests.codes.ok

            jsn = json.loads(response.content)
            json_header = jsn['Header']
            json_data = jsn['Data']

            if json_header[0]['rows'] == 0:
                raise ValueError

            df = pd.DataFrame.from_records(json_data)
            df.rename(
                columns={'value_represented': 'county_name'}, inplace=True)
            return df

        except AssertionError:
            print('Bad URL!')
        except ValueError:
            print('No matching data could be found!')

    def get_sites_by_county(self, state, county):
        """
        Gets the ids of measurement sites by county. Takes in a state id and
        county id.
        """
        url = self.api_url + '/list/sitesByCounty' + self.stub
        url += f'&state={state}&county={county}'
        response = requests.get(url)

        try:
            assert response.status_code == requests.codes.ok
            jsn = json.loads(response.content)
            json_header = jsn['Header']
            json_data = jsn['Data']

            if json_header[0]['rows'] == 0:
                raise ValueError

            df = pd.DataFrame.from_records(json_data)
            df.rename(columns={'value_represented': 'site_name'}, inplace=True)
            return df

        except AssertionError:
            print('Bad URL!')
        except ValueError:
            print('No matching data could be found!')

    def get_parameter_classes(self):
        """
        Gets the possible classes of parameters
        """
        url = self.api_url + '/list/classes' + self.stub
        response = requests.get(url)

        try:
            assert response.status_code == requests.codes.ok
        except AssertionError:
            print('Bad URL!')

        json_data = json.loads(response.content)['Data']
        df = pd.DataFrame.from_records(json_data)
        df.rename(columns={
            'code': 'class_name',
            'value_represented': 'class_description'},
            inplace=True)
        return df

    def get_parameter_list_by_class(self, _class):
        url = self.api_url + '/list/parametersByClass' + self.stub
        url += f'&pc={_class}'

        response = requests.get(url)

        try:
            assert response.status_code == requests.codes.ok

            jsn = json.loads(response.content)
            json_header = jsn['Header']
            json_data = jsn['Data']

            if json_header[0]['rows'] == 0:
                raise ValueError

            df = pd.DataFrame.from_records(json_data)
            df.rename(
                columns={'value_represented': 'parameter_description'},
                inplace=True)
            return df

        except AssertionError:
            print('Bad URL!')
        except ValueError:
            print('No matching data could be found!')

    def annual_data_by_cbsa(self, cbsa_code, params, bdate, edate):
        """
        Searches for annual data by the CBSA. These are generally large regions
        Takes the following arguments:
        - cbsa_code: code for the cbsa area
        - params: integer id for the specified readings
        - bdate, edate: beginning and end dates in YYYYMMDD format
        """
        search_params = '&param='
        for p in params:
            search_params += str(p)
            search_params += ','
        search_params = search_params[:-1]
        search_params += f'&bdate={bdate}&edate={edate}&cbsa={cbsa_code}'
        url = self.api_url + '/annualData/byCBSA' + self.stub + search_params

        response = requests.get(url)

        try:
            assert response.status_code == requests.codes.ok
            jsn = json.loads(response.content)
            json_header = jsn['Header']
            json_data = jsn['Data']

            if json_header[0]['rows'] == 0:
                raise ValueError

            df = pd.DataFrame.from_records(json_data)
            return df

        except AssertionError:
            print('Bad URL!')
        except ValueError:
            print('No matching data could be found!')

    def annual_data_by_site(self, state, county, site, params, bdate, edate):
        """
        Searches for annula data by measurement site.
        Takes in arguments:
        - state: integer id of the state
        - county: integer id of the county
        - site: integer id of the measurement site
        - params: integer id of the desired type of measurement
        - bdate, edate: beginning and end dates of the measurement
        """
        search_params = '&param='
        for p in params:
            search_params += str(p)
            search_params += ','
        search_params = search_params[:-1]
        search_params += (
            f'&state={state}' +
            f'&county={county}' +
            f'&bdate={bdate}' +
            f'&edate={edate}' +
            f'&site={site}')
        url = self.api_url + '/annualData/bySite' + self.stub + search_params

        response = requests.get(url)

        try:
            assert response.status_code == requests.codes.ok
            jsn = json.loads(response.content)
            json_header = jsn['Header']
            json_data = jsn['Data']

            if json_header[0]['rows'] == 0:
                raise ValueError

            df = pd.DataFrame.from_records(json_data)
            return df
        except AssertionError:
            print('Bad URL!')
        except ValueError:
            print('No matching data could be found!')

    def annual_data_by_county(self, state, county, params, bdate, edate):
        """
        Gets the annual data by county. Takes the following parameters:
        - state: integer id code
        - county: integer county code
        - param: integer ids of desired parameters to measure
        - bdate, edate: start and end dates in YYYYMMDD format
        """
        url = self.api_url + '/annualData/byCounty' + self.stub
        search_params = '&param='
        for p in params:
            search_params += str(p)
            search_params += ','
        search_params = search_params[:-1]
        search_params += (
            f'&state={state}' +
            f'&county={county}' +
            f'&bdate={bdate}' +
            f'&edate={edate}')
        url += search_params

        response = requests.get(url)

        try:
            assert response.status_code == requests.codes.ok

            jsn = json.loads(response.content)
            json_header = jsn['Header']
            json_data = jsn['Data']

            if json_header[0]['rows'] == 0:
                raise ValueError

            df = pd.DataFrame.from_records(json_data)
            return df

        except AssertionError:
            print('Bad URL!')
        except ValueError:
            print('No matching data could be found!')

    def annual_data_by_state(self, state, params, bdate, edate):
        """
        Gets the annual data by county. Takes the following parameters:
        - state: integer id code
        - param: integer ids of desired parameters to measure
        - bdate, edate: start and end dates in YYYYMMDD format
        """
        url = self.api_url + '/annualData/byState' + self.stub
        search_params = '&param='
        for p in params:
            search_params += str(p)
            search_params += ','
        search_params = search_params[:-1]
        search_params += (
            f'&state={state}' +
            f'&bdate={bdate}' +
            f'&edate={edate}')
        url += search_params

        response = requests.get(url)

        try:
            assert response.status_code == requests.codes.ok

            jsn = json.loads(response.content)
            json_header = jsn['Header']
            json_data = jsn['Data']

            if json_header[0]['rows'] == 0:
                raise ValueError

            df = pd.DataFrame.from_records(json_data)
            return df

        except AssertionError:
            print('Bad URL!')
        except ValueError:
            print('No matching data could be found!')

    def get_monitors_at_site(self, state, county, site, params, bdate, edate):
        """
        Gets information about the monitoring aparatus at a particular site.
        Takes the following arguments:
        - state: integer id of the state
        - county: integer id of the county
        - site: integer id of the site
        - param: a list of parameters to search for
        - bdate, edate: start and end dates for search
        """
        search_params = '&param='
        for p in params:
            search_params += str(p)
            search_params += ','
        search_params = search_params[:-1]

        search_params += (
            f'&state={state}' +
            f'&county={county}' +
            f'&bdate={bdate}' +
            f'&edate={edate}' +
            f'&site={site}')

        url = self.api_url + '/monitors/bySite' + self.stub + search_params

        response = requests.get(url)

        try:
            assert response.status_code == requests.codes.ok
            jsn = json.loads(response.content)
            json_header = jsn['Header']
            json_data = jsn['Data']

            if json_header[0]['rows'] == 0:
                raise ValueError

            df = pd.DataFrame.from_records(json_data)
            return df

        except AssertionError:
            print('Bad URL!')
        except ValueError:
            print('No matching data could be found!')
