from datetime import datetime, date, timedelta
import http.client
import logging
import json
import os.path

timeFormat = "%Y-%m-%d %H:%M:%S"

# Fetch data from open API


def getCurrentRecord(key):
    conn = http.client.HTTPSConnection("opendata.cwb.gov.tw")
    url = "/api/v1/rest/datastore/O-A0003-001?format=JSON&StationId=466920&WeatherElement=AirTemperature"
    conn.request("GET", url, headers={
        "accept": "application/json",
        "authorization": key
    })
    response = conn.getresponse()

    if response.status != 200:
        logging.error("HTTP status " + response.status +
                      ": " + response.reason)
        exit(1)

    result = json.loads(response.read())

    temp = float(result["records"]["Station"][0]["WeatherElement"]["AirTemperature"])

    if temp < -20.0:
        logging.warning("Temperature is too low.\nResponse:\n" + str(result))
        exit(0)

    return {
        "time": datetime.fromisoformat(result["records"]["Station"][0]["ObsTime"]["DateTime"]).strftime(timeFormat),
        "temp": temp
    }

# Load json files


def getJson(path, exitIfNotFound=True):
    if not os.path.isfile(path):
        if exitIfNotFound:
            logging.error("{0} not found".format(path))
            exit(1)
        else:
            return False

    with open(path, "r") as file:
        result = json.loads(file.read())

    return result


def coldness(temp):
    if temp > 19.0:
        return "無"
    elif temp <= 19.0 and temp > 14.0:
        return "東北季風"
    elif temp <= 14.0 and temp > 12.0:
        return "大陸冷氣團"
    elif temp <= 12.0 and temp > 10.0:
        return "強烈大陸冷氣團"
    else:
        return "寒流"


def main():
    configPath = os.path.join(os.path.dirname(__file__), "config.json")
    dataPath = os.path.join(os.path.dirname(__file__), "data.json")
    logPath = os.path.join(os.path.dirname(__file__), "exec.log")

    FORMAT = '%(asctime)s %(levelname)s: %(message)s'
    logging.basicConfig(format=FORMAT, filename=logPath)

    config = getJson(configPath)

    if "dataPath" in config.keys() and config["dataPath"] != "":
        dataPath = config["dataPath"]

    currentRecord = getCurrentRecord(config["key"])

    data = getJson(dataPath, False)

    lowestRecord = currentRecord

    if data != False:
        # Don't update if the upstream doesn't update
        if currentRecord["time"] == data["time"]:
            exit(0)

        lowestRecord = {
            "time": data["minTempTime"],
            "temp": data["minTemp"]
        }

        recordTime = datetime.strptime(currentRecord["time"], timeFormat)
        dataTime = datetime.strptime(data["time"], timeFormat)

        # check the time interval between two records
        delta = recordTime - dataTime
        if delta > timedelta(minutes=10):
            logging.warning(
                "Interval between two records is too long: {0}".format(delta))

        # reset lowestRecord if crossing days
        if (recordTime.date() - dataTime.date()).days > 0:
            lowestRecord = currentRecord

    if lowestRecord["temp"] > currentRecord["temp"]:
        lowestRecord = currentRecord

    newData = {
        "time": currentRecord["time"],
        "temp": currentRecord["temp"],
        "minTempTime": lowestRecord["time"],
        "minTemp": lowestRecord["temp"],
        "coldness": coldness(lowestRecord["temp"])
    }

    with open(dataPath, "w") as file:
        file.write(json.dumps(newData))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(type(e).__name__ + ": " + str(e), exc_info=True)
        exit(1)
