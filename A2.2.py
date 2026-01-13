import pandas as pd
import os
import math


# map month names to Australian seasons
def getSeason(month):
    if month in ["December", "January", "February"]:
        return "Summer"
    elif month in ["March", "April", "May"]:
        return "Autumn"
    elif month in ["June", "July", "August"]:
        return "Winter"
    else:
        return "Spring"


def analyseTemperatures():

    folderPath = "temperatures"
    dataFrames = []

    # read all csv files
    for fileName in os.listdir(folderPath):
        if fileName.endswith(".csv"):
            filePath = os.path.join(folderPath, fileName)
            df = pd.read_csv(filePath)
            dataFrames.append(df)

    # combine all files
    data = pd.concat(dataFrames, ignore_index=True)

    # list of month columns
    monthColumns = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    # convert wide format to long format
    longData = data.melt(
        id_vars=["STATION_NAME"],
        value_vars=monthColumns,
        var_name="Month",
        value_name="Temperature"
    )

    # remove missing values
    longData = longData.dropna(subset=["Temperature"])

    # assign season
    longData["Season"] = longData["Month"].apply(getSeason)

    #  Seasonal Average 
    seasonalAvg = longData.groupby("Season")["Temperature"].mean()

    with open("average_temp.txt", "w") as file:
        for season, avg in seasonalAvg.items():
            file.write(f"{season}: {avg:.1f}°C\n")

    #  Temperature Range 
    stationStats = longData.groupby("STATION_NAME")["Temperature"].agg(["max", "min"])
    stationStats["range"] = stationStats["max"] - stationStats["min"]

    maxRange = stationStats["range"].max()
    rangeStations = stationStats[stationStats["range"] == maxRange]

    with open("largest_temp_range_station.txt", "w") as file:
        for station, row in rangeStations.iterrows():
            file.write(
                f"Station {station}: Range {row['range']:.1f}°C "
                f"(Max: {row['max']:.1f}°C, Min: {row['min']:.1f}°C)\n"
            )

    #  Temperature Stability 
    stdDevs = longData.groupby("STATION_NAME")["Temperature"].std()

    minStd = stdDevs.min()
    maxStd = stdDevs.max()

    with open("temperature_stability_stations.txt", "w") as file:
        file.write("Most Stable:\n")
        for station, std in stdDevs.items():
            if math.isclose(std, minStd):
                file.write(f"Station {station}: StdDev {std:.1f}°C\n")

        file.write("\nMost Variable:\n")
        for station, std in stdDevs.items():
            if math.isclose(std, maxStd):
                file.write(f"Station {station}: StdDev {std:.1f}°C\n")


# run program
analyseTemperatures()