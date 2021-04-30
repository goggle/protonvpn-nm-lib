import time
import json


class Streaming:
    def __init__(self):
        self.__data = None

    def __getitem__(self, country_code):
        if not isinstance(country_code, str):
            raise TypeError("Expected type str (provided {})".format(type(country_code)))
        elif country_code.upper() not in self.__data["StreamingServices"]:
            raise KeyError("\"{}\" not found".format(country_code))

        return self.__data["StreamingServices"][country_code.upper()].get("2", {})

    def json_dumps(self):
        return json.dumps(self.__data)

    def json_loads(self, data):
        self.__data = json.loads(data)

    def update_streaming_services_data(self, data):
        assert "Code" in data
        assert "ResourceBaseURL" in data
        assert "StreamingServices" in data

        if data["Code"] != 1000:
            raise ValueError("Invalid data with code != 1000")

        data["StreamingServicesUpdateTimestamp"] = time.time()
        self.__data = data

    @property
    def streaming_services_timestamp(self):
        try:
            return self.__data.get("StreamingServicesUpdateTimestamp", 0.0)
        except AttributeError:
            return 0.0
