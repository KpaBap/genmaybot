import mock
import unittest
import requests
import datetime
from copy import deepcopy

error_msg = "Could not retrieve current air quality data."
json_error_msg = "JSON schema in response has changed. Please fix me. Key error: {}"
location_missing_msg = "Use !setlocation <location> to save your location to the bot or use !aqi <zipcode>"

def get_aqi(self, botevent):
    zipcode = ""
    try:
        zipcode = botevent.input if botevent.input else botevent.user_location
    except AttributeError:
        pass

    if not zipcode:
        botevent.output = location_missing_msg
        return botevent

    try:
        api_key = self.botconfig["APIkeys"]["airnow_apikey"]
    except KeyError as error:
        self.logger.error(f"airnow.gov API key not set. Key not found: {error}")
        return botevent

    date_format = "%Y-%m-%d"
    today = datetime.datetime.today().strftime(date_format)
    tomorrow = (datetime.datetime.today() + datetime.timedelta(days=+1)).strftime(date_format)


    forecast_url = f"http://www.airnowapi.org/aq/forecast/zipCode/?format=application/json&zipCode={zipcode}&date={today}&distance=25&API_KEY={api_key}"
    current_url = f"http://www.airnowapi.org/aq/observation/zipCode/current/?format=application/json&zipCode={zipcode}&distance=25&API_KEY={api_key}"

    current_response = []
    forecast_response = []

    try:
        current_response = requests.get(current_url).json()
        forecast_response = requests.get(forecast_url).json()
    except Exception:
        self.logger.exception(error_msg)
        botevent.output = error_msg

    if not current_response:
        botevent.output = error_msg
        return botevent

    current_ozone = ""
    current_pm = ""
    location = ""
    tomorrow_forecast = ""

    try:
        for observation in current_response:
            if observation['ParameterName'] == "O3":
                current_ozone = f"Ozone: {observation['AQI']} ({observation['Category']['Name']})"
            elif 'PM' in observation['ParameterName']:
                current_pm = f"{current_pm}{observation['ParameterName']}: {observation['AQI']} ({observation['Category']['Name']}) "
                location = f"{observation['ReportingArea']}, {observation['StateCode']}"
    except KeyError as error:
        botevent.output = f"{json_error_msg.format(error)}"
        return botevent

    try:
        for forecast in forecast_response:
            if forecast['DateForecast'].strip() == tomorrow and forecast['AQI'] != -1:
                tomorrow_forecast = f" Tomorrow: {forecast['ParameterName']}: {forecast['AQI']} ({forecast['Category']['Name']})"
    except KeyError:
        pass

    botevent.output = f"{location} - Air quality: {current_pm}{current_ozone}{tomorrow_forecast}"
    return botevent

get_aqi.command = "!aqi"
get_aqi.helptext = "Usage: !aqi <zipcode> Retrieves air quality info from airnow.gov"


class TestEvent(object):
    def __init__(self):
        self.input = "90210"
        self.output = ""
        self.user_location = ""

class TestBot(object):
    def __init__(self):
        self.logger = mock.MagicMock()
        self.logger.exception = mock.MagicMock()
        self.botconfig = {"APIkeys": {"airnow_apikey": None}}

class AQITests(unittest.TestCase):
    date_format = "%Y-%m-%d"
    today = datetime.datetime.today().strftime(date_format)
    tomorrow = (datetime.datetime.today() + datetime.timedelta(days=+1)).strftime(date_format)

    current_response = [{'AQI': 4,
                         'Category': {'Name': 'Good', 'Number': 1},
                         'DateObserved': '{} '.format(today),
                         'HourObserved': 7,
                         'Latitude': 37.33,
                         'LocalTimeZone': 'PST',
                         'Longitude': -121.9,
                         'ParameterName': 'O3',
                         'ReportingArea': 'San Jose',
                         'StateCode': 'CA'},
                        {'AQI': 70,
                         'Category': {'Name': 'Moderate', 'Number': 2},
                         'DateObserved': '{} '.format(today),
                         'HourObserved': 7,
                         'Latitude': 37.33,
                         'LocalTimeZone': 'PST',
                         'Longitude': -121.9,
                         'ParameterName': 'PM2.5',
                         'ReportingArea': 'San Jose',
                         'StateCode': 'CA'}]

    forecast_response = [{'AQI': 161,
                          'ActionDay': False,
                          'Category': {'Name': 'Unhealthy', 'Number': 4},
                          'DateForecast': '{} '.format(today),
                          'DateIssue': '2017-10-11 ',
                          'Latitude': 37.33,
                          'Longitude': -121.9,
                          'ParameterName': 'PM2.5',
                          'ReportingArea': 'San Jose',
                          'StateCode': 'CA'},
                         {'AQI': 181,
                          'ActionDay': False,
                          'Category': {'Name': 'Unhealthy for Sensitive Groups', 'Number': 3},
                          'DateForecast': '{} '.format(tomorrow),
                          'DateIssue': '2017-10-11 ',
                          'Latitude': 37.33,
                          'Longitude': -121.9,
                          'ParameterName': 'PM2.5',
                          'ReportingArea': 'San Jose',
                          'StateCode': 'CA'},
                         {'AQI': -1,
                          'ActionDay': False,
                          'Category': {'Name': 'Unhealthy for Sensitive Groups', 'Number': 3},
                          'DateForecast': '2017-10-14 ',
                          'DateIssue': '2017-10-11 ',
                          'Latitude': 37.33,
                          'Longitude': -121.9,
                          'ParameterName': 'PM2.5',
                          'ReportingArea': 'San Jose',
                          'StateCode': 'CA'},
                         {'AQI': -1,
                          'ActionDay': False,
                          'Category': {'Name': 'Unhealthy for Sensitive Groups', 'Number': 3},
                          'DateForecast': '2017-10-15 ',
                          'DateIssue': '2017-10-11 ',
                          'Latitude': 37.33,
                          'Longitude': -121.9,
                          'ParameterName': 'PM2.5',
                          'ReportingArea': 'San Jose',
                          'StateCode': 'CA'},
                         {'AQI': -1,
                          'ActionDay': False,
                          'Category': {'Name': 'Moderate', 'Number': 2},
                          'DateForecast': '2017-10-16 ',
                          'DateIssue': '2017-10-11 ',
                          'Latitude': 37.33,
                          'Longitude': -121.9,
                          'ParameterName': 'PM2.5',
                          'ReportingArea': 'San Jose',
                          'StateCode': 'CA'}]

    desired_output_with_forecast = "San Jose, CA - Air quality: PM2.5: 70 (Moderate) Ozone: 4 (Good) Tomorrow: PM2.5: 181 (Unhealthy for Sensitive Groups)"
    desired_output_without_forecast = "San Jose, CA - Air quality: PM2.5: 70 (Moderate) Ozone: 4 (Good)"

    def setUp(self):
        self.test_bot = TestBot()
        self.test_event = TestEvent()

    @mock.patch("requests.get", autospec=True)
    def test_aqi_with_input(self, mock_get):
        self.test_event.input = "95125"
        self.test_event.user_location = ""

        mock_response = mock.MagicMock()
        mock_response.json.side_effect = [self.current_response, self.forecast_response]
        mock_get.return_value = mock_response
        

        result = get_aqi(self.test_bot, self.test_event)

        self.assertEqual(mock_response.json.call_count, 2)
        self.assertEqual(result.output, self.desired_output_with_forecast)

    def test_aqi_missing_api_key(self):
        # Missing API key
        self.test_bot.botconfig['APIkeys'].pop("airnow_apikey")
        result = get_aqi(self.test_bot, self.test_event)
        self.assertEqual(result.output, "")

    @mock.patch("requests.get")
    def test_aqi_no_input_no_saved_location(self, mock_get):
        self.test_event.input = ""
        self.test_event.user_location = ""

        result = get_aqi(self.test_bot, self.test_event)
        self.assertIsNotNone(result)
        self.assertEqual(result.output, location_missing_msg)
        mock_get.assert_not_called()

    @mock.patch("requests.get")
    def test_aqi_no_input_yes_saved_location(self, mock_get):
        self.test_event.input = ""
        self.test_event.user_location = "95125"

        mock_response = mock.MagicMock()
        mock_response.json.side_effect = [self.current_response, self.forecast_response]
        mock_get.return_value = mock_response

        result = get_aqi(self.test_bot, self.test_event)
        self.assertIsNotNone(result)
        self.assertEqual(mock_response.json.call_count, 2)
        self.assertEqual(result.output, self.desired_output_with_forecast)

    @mock.patch("requests.get")
    def test_aqi_yes_input_yes_saved_location(self, mock_get):
        self.test_event.input = "90210"
        self.test_event.user_location = "95125"

        mock_response = mock.MagicMock()
        mock_response.json.side_effect = [self.current_response, self.forecast_response]
        mock_get.return_value = mock_response

        result = get_aqi(self.test_bot, self.test_event)
        self.assertIsNotNone(result)
        self.assertEqual(mock_response.json.call_count, 2)
        self.assertEqual(result.output, self.desired_output_with_forecast)

        #Check that we're using the input and not saved user location
        for call in mock_get.call_args_list:
            self.assertIn(self.test_event.input, call[0][0])



    @mock.patch("requests.get", autospec=True)
    def test_aqi_negative(self, mock_get):

        # Exception when trying to fetch URL
        desired_output = error_msg
        mock_response = mock.MagicMock()
        mock_response.json.side_effect = Exception
        mock_get.return_value = mock_response
        result = get_aqi(self.test_bot, self.test_event)
        self.assertEqual(result.output, desired_output)
        self.test_bot.logger.exception.assert_called_with(error_msg)

        # Test with empty response
        mock_response.json.side_effect = None
        mock_response.json.return_value = []

        result = get_aqi(self.test_bot, self.test_event)
        self.assertEqual(result.output, desired_output)

        # Missing stuff from the current response
        desired_output = json_error_msg.format("'AQI'")
        mock_response.json.side_effect = None
        broken_response = deepcopy(self.current_response)
        broken_response[0].pop('AQI')

        mock_response.json.return_value = broken_response

        result = get_aqi(self.test_bot, self.test_event)
        self.assertEqual(result.output, desired_output)

        # Missing stuff from the Forecast response
        broken_response = deepcopy(self.forecast_response)
        for response in broken_response:
            response.pop('AQI')
        mock_response.json.side_effect = [self.current_response, broken_response]
        result = get_aqi(self.test_bot, self.test_event)
        self.assertEqual(result.output, self.desired_output_without_forecast)

    @unittest.skip("Enable this yourself to test against the real API")
    def test_aqi_real(self):
        api_key = "CHANGE ME"
        self.test_bot.botconfig = {"APIkeys":
                                        {"airnow_apikey": api_key}}


        result = get_aqi(self.test_bot, self.test_event)
        print(result.output)


if __name__ == "__main__":
    unittest.main()
