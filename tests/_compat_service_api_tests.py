# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import sys
import json
import unittest
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from neon_utils.service_apis import request_neon_api, NeonAPI
from neon_utils.service_apis.wolfram_alpha import *
from neon_utils.service_apis.alpha_vantage import *
from neon_utils.service_apis.open_weather_map import *

IP_ADDR = "50.47.129.133"
VALID_LAT = "47.4797"
VALID_LNG = "-122.2079"


class ServiceAPITests(unittest.TestCase):
    def test_request_neon_api_valid(self):
        resp = request_neon_api(NeonAPI.TEST_API, {"test": True})
        self.assertIsInstance(resp, dict)
        self.assertEqual(resp['status_code'], 200)

    def test_request_neon_api_not_implemented(self):
        resp = request_neon_api(NeonAPI.NOT_IMPLEMENTED, {"request": "data"})
        self.assertIsInstance(resp, dict)
        self.assertEqual(resp['status_code'], 401)

    def test_request_neon_api_invalid_api(self):
        with self.assertRaises(TypeError):
            request_neon_api("alpha_vantage", {"company": "alphabet"})

    def test_request_neon_api_invalid_null_params(self):
        with self.assertRaises(ValueError):
            request_neon_api(NeonAPI.ALPHA_VANTAGE, {})

    def test_request_neon_api_invalid_type_params(self):
        with self.assertRaises(TypeError):
            request_neon_api(NeonAPI.ALPHA_VANTAGE, ["alphabet"])


class WolframAlphaTests(unittest.TestCase):
    FULL_QUERY = "https://api.wolframalpha.com/v2/query?input=what+time+is+it&format=image,plaintext" \
                 "&output=XML&appid=DEMO"
    SIMPLE_QUERY = "https://api.wolframalpha.com/v1/simple?i=Who+is+the+prime+minister+of+India%3F&appid=DEMO"
    SPOKEN_QUERY = "https://api.wolframalpha.com/v1/spoken?i=Convert+42+mi+to+km&appid=DEMO"
    SHORT_QUERY = "https://api.wolframalpha.com/v1/result?i=How+many+ounces+are+in+a+gallon%3F&appid=DEMO"
    CONVERSE_QUERY = "http://api.wolframalpha.com/v1/conversation.jsp?appid=DEMO&i=How+much+does+the+earth+weigh%3f"
    RECOGNIZE_QUERY = "https://www.wolframalpha.com/queryrecognizer/query.jsp?mode=Default" \
                      "&i=How+far+away+is+the+Moon%3F&appid=DEMO"

    def test_get_geolocation_ip(self):
        location = get_geolocation_params(ip=IP_ADDR)
        self.assertIsInstance(location, dict)
        self.assertEqual(location, {"ip": IP_ADDR})

    def test_get_geolocation_lat_lng(self):
        location = get_geolocation_params(lat=VALID_LAT, lng=VALID_LNG)
        self.assertIsInstance(location, dict)
        self.assertEqual(location, {"latlong": f"{VALID_LAT},{VALID_LNG}"})

    def test_get_geolocation_null(self):
        from neon_utils.net_utils import get_ip_address
        location = get_geolocation_params()
        self.assertIsInstance(location, dict)
        self.assertEqual(location, {"ip": get_ip_address()})

    def test_api_to_url_valid(self):
        self.assertEqual(api_to_url(QueryApi.SIMPLE), "http://api.wolframalpha.com/v2/simple")
        self.assertEqual(api_to_url(QueryApi.SHORT), "http://api.wolframalpha.com/v2/result")
        self.assertEqual(api_to_url(QueryApi.SPOKEN), "http://api.wolframalpha.com/v2/spoken")
        self.assertEqual(api_to_url(QueryApi.FULL), "http://api.wolframalpha.com/v2/query")
        self.assertEqual(api_to_url(QueryApi.RECOGNIZE), "http://www.wolframalpha.com/queryrecognizer/query.jsp")
        self.assertEqual(api_to_url(QueryApi.CONVERSATION), "http://api.wolframalpha.com/v1/conversation.jsp")

    def test_api_to_url_invalid_null_api(self):
        with self.assertRaises(ValueError):
            api_to_url(None)

    def test_api_to_url_invalid_type_api(self):
        with self.assertRaises(TypeError):
            api_to_url("simple")

    def test_query_full_api(self):
        result = query_wolfram_alpha_api(WolframAlphaTests.FULL_QUERY)
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result["content"].decode(result["encoding"]), str)

    def test_query_simple_api(self):
        result = query_wolfram_alpha_api(WolframAlphaTests.SIMPLE_QUERY)
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result["content"], bytes)
        # TODO: This is a Wolfram error that needs to be handled DM
        if result["encoding"]:
            self.assertEqual(result["content"], b'Wolfram|Alpha did not understand your input')
        else:
            self.assertIsNone(result["encoding"], result["content"])
        self.assertIsInstance(result["cached"], bool)

    def test_query_spoken_api(self):
        result = query_wolfram_alpha_api(WolframAlphaTests.SPOKEN_QUERY)
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result["content"].decode(result["encoding"]), str)
        self.assertIsInstance(result["cached"], bool)

    def test_query_short_api(self):
        result = query_wolfram_alpha_api(WolframAlphaTests.SHORT_QUERY)
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result["content"].decode(result["encoding"]), str)
        self.assertIsInstance(result["cached"], bool)

    def test_query_recognize_api(self):
        result = query_wolfram_alpha_api(WolframAlphaTests.RECOGNIZE_QUERY)
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result["content"].decode(result["encoding"]), str)
        self.assertIsInstance(result["cached"], bool)

    def test_get_wolfram_alpha_response_spec_api_key(self):
        resp = get_wolfram_alpha_response("Convert 42 mi to km", QueryApi.SPOKEN, app_id="DEMO")
        self.assertIsInstance(resp, str)
        self.assertEqual(resp, '42 miles is equivalent to about 67.6 kilometers')

    def test_get_wolfram_alpha_response_conf_api_key(self):
        resp = get_wolfram_alpha_response("Convert 42 mi to km", QueryApi.SPOKEN)
        self.assertIsInstance(resp, str)
        self.assertEqual(resp, '42 miles is equivalent to about 67.6 kilometers')

    def test_get_wolfram_alpha_response_invalid_key(self):
        resp = get_wolfram_alpha_response("Convert 42 km to mi", QueryApi.SPOKEN, app_id="DEMO")
        self.assertIsInstance(resp, str)

    def test_get_wolfram_alpha_bytes_response(self):
        resp = get_wolfram_alpha_response("Who is the prime minister of India", QueryApi.SIMPLE)
        if resp != "Wolfram|Alpha did not understand your input":
            self.assertIsInstance(resp, bytes)

    def test_get_wolfram_alpha_response_no_api_key(self):
        resp = get_wolfram_alpha_response("Who is the prime minister of India", QueryApi.SIMPLE, app_id=None)
        if resp == "Wolfram|Alpha did not understand your input":
            LOG.warning("Wolfram Alpha returned an invalid response (known occasional bug)")
        else:
            self.assertIsInstance(resp, bytes)


class AlphaVantageTests(unittest.TestCase):
    SYMBOL_SEARCH = "https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=tencent&apikey=demo"
    GLOBAL_QUOTE = "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=IBM&apikey=demo"

    def test_query_symbol_search(self):
        resp = query_alpha_vantage_api(AlphaVantageTests.SYMBOL_SEARCH)
        self.assertIsInstance(resp, dict)
        data = json.loads(resp["content"])
        self.assertIsInstance(data, dict)
        self.assertEqual(set(data.keys()), {"bestMatches"})
        self.assertIsInstance(data["bestMatches"], list)
        for match in data["bestMatches"]:
            self.assertEqual(set(match.keys()), {'1. symbol', '2. name', '3. type', '4. region', '5. marketOpen',
                                                 '6. marketClose', '7. timezone', '8. currency', '9. matchScore'})

    def test_query_global_quote(self):
        resp = query_alpha_vantage_api(AlphaVantageTests.GLOBAL_QUOTE)
        self.assertIsInstance(resp, dict)
        data = json.loads(resp["content"])
        self.assertIsInstance(data, dict)
        self.assertEqual(set(data.keys()), {"Global Quote"})
        self.assertIsInstance(data["Global Quote"], dict)
        self.assertEqual(set(data["Global Quote"].keys()), {'01. symbol', '02. open', '03. high', '04. low',
                                                            '05. price', '06. volume', '07. latest trading day',
                                                            '08. previous close', '09. change', '10. change percent'})

    def test_get_stock_symbol_spec_key(self):
        matches = search_stock_by_name("tencent", api_key="demo")
        self.assertIsInstance(matches, list)
        for match in matches:
            self.assertIsInstance(match, dict)
            self.assertEqual(match["region"], "United States")
        self.assertEqual(matches[0]["symbol"], "TCEHY")

    def test_get_stock_symbol_conf_key(self):
        matches = search_stock_by_name("alphabet")
        self.assertIsInstance(matches, list)
        for match in matches:
            self.assertIsInstance(match, dict)
            self.assertEqual(match["region"], "United States")
        self.assertEqual(matches[0]["symbol"], "GOOGL")

    @pytest.mark.skip
    def test_get_stock_symbol_invalid_key(self):
        matches = search_stock_by_name("alphabet", api_key="demo")
        self.assertIsInstance(matches, list)
        self.assertEqual(len(matches), 0)

    def test_get_stock_symbol_no_results(self):
        matches = search_stock_by_name("google")
        self.assertIsInstance(matches, list)
        self.assertEqual(len(matches), 0)

    def test_get_stock_quote_spec_key(self):
        quote = get_stock_quote("IBM", api_key="demo")
        self.assertIsInstance(quote, dict)
        self.assertEqual(set(quote.keys()), {"symbol", "price", "close"})
        self.assertEqual(quote["symbol"], "IBM")

    def test_get_stock_quote_conf_key(self):
        quote = get_stock_quote("GOOGL")
        self.assertIsInstance(quote, dict)
        self.assertEqual(set(quote.keys()), {"symbol", "price", "close"}, quote)
        self.assertEqual(quote["symbol"], "GOOGL")

    def test_get_stock_quote_invalid_key(self):
        quote = get_stock_quote("MSFT", api_key="INVALID")
        self.assertIsInstance(quote, dict)
        if "symbol" in quote.keys():
            LOG.warning("Invalid API key produced valid result!")
            self.assertEqual(quote.get("symbol"), "MSFT")
        else:
            self.assertTrue(quote.get("error"), quote)

    def test_get_stock_quote_invalid_symbol(self):
        quote = get_stock_quote("International Business Machines")
        self.assertIsInstance(quote, dict)
        self.assertTrue(quote.get("error"))

    def test_get_stock_quote_no_api_key(self):
        quote = get_stock_quote("IBM", api_key=None)
        self.assertIsInstance(quote, dict)
        self.assertEqual(set(quote.keys()), {"symbol", "price", "close"})
        self.assertEqual(quote["symbol"], "IBM")

    def test_get_stock_symbol_no_api_key(self):
        matches = search_stock_by_name("tencent", api_key=None)
        self.assertIsInstance(matches, list)
        for match in matches:
            self.assertIsInstance(match, dict)
            self.assertEqual(match["region"], "United States")
        self.assertEqual(matches[0]["symbol"], "TCEHY")


class OpenWeatherMapTests(unittest.TestCase):

    def test_get_forecast_valid_str(self):
        data = get_forecast(VALID_LAT, VALID_LNG)
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data["current"], dict)
        self.assertIsInstance(data["minutely"], list)
        self.assertIsInstance(data["hourly"], list)
        self.assertIsInstance(data["daily"], list)

    def test_get_forecast_valid_float(self):
        data = get_forecast(float(VALID_LAT), float(VALID_LNG))
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data["current"], dict)
        self.assertIsInstance(data["minutely"], list)
        self.assertIsInstance(data["hourly"], list)
        self.assertIsInstance(data["daily"], list)

    def test_get_forecast_default_api_key(self):
        data = get_forecast(VALID_LAT, VALID_LNG)
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data["current"], dict)
        self.assertIsInstance(data["minutely"], list)
        self.assertIsInstance(data["hourly"], list)
        self.assertIsInstance(data["daily"], list)

    def test_get_current_weather(self):
        data = get_current_weather(VALID_LAT, VALID_LNG)
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data["weather"], list)
        self.assertIsInstance(data["weather"][0], dict)

        self.assertIsInstance(data["main"], dict)

    @pytest.mark.skip
    def test_get_forecast_invalid_location(self):
        data = get_forecast("lat", "lon")
        self.assertIsInstance(data, dict)
        self.assertEqual(data['cod'], '400')

    @pytest.mark.skip
    def test_get_forecast_invalid_key(self):
        data = get_forecast(VALID_LAT, VALID_LNG, api_key="test")
        self.assertIsInstance(data, dict)
        self.assertEqual(data['cod'], '401')

    def test_get_forecast_no_api_key(self):
        data = get_forecast(VALID_LAT, VALID_LNG, api_key=None)
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data["current"], dict)
        self.assertIsInstance(data["minutely"], list)
        self.assertIsInstance(data["hourly"], list)
        self.assertIsInstance(data["daily"], list)


if __name__ == '__main__':
    unittest.main()
