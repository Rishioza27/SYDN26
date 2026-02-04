import pandas as pd
import os
import math

# map months to Australian seasons
def getSeason(month):
    if month in ["December", "January", "February"]:
        return "Summer"
    elif month in ["March", "April", "May"]:
        return "Autumn"
    elif month in ["June", "July", "August"]:
        return "Winter"
    elif month in ["September", "October", "November"]:
        return "Spring"
    else:
        return None

def analyseTemperatures():

    folderPath = "temperatures"

    # basic folder check
    if not os.path.exists(folderPath):
        print("Temperatures folder not found.")
        return

    dataFrames = []

    # read CSV files
    for fileName in os.listdir(folderPath):
        if fileName.endswith(".csv"):
            filePath = os.path.join(folderPath, fileName)
            try:
                df = pd.read_csv(filePath)
                dataFrames.append(df)
            except:
                print(f"Could not read file: {fileName}")

    if len(dataFrames) == 0:
        print("No temperature data files found.")
        return

    # combine all years
    data = pd.concat(dataFrames, ignore_index=True)

    # expected columns
    monthColumns = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    # simple column check
    if "STATION_NAME" not in data.columns:
        print("STATION_NAME column missing in data.")
        return

    for month in monthColumns:
        if month not in data.columns:
            print(f"Missing month column: {month}")
            return

    # convert wide data to long format
    longData = data.melt(
        id_vars=["STATION_NAME"],
        value_vars=monthColumns,
        var_name="Month",
        value_name="Temperature"
    )

    # remove missing temperature values
    longData = longData.dropna(subset=["Temperature"])

    if longData.empty:
        print("No valid temperature values found.")
        return

    # assign seasons
    longData["Season"] = longData["Month"].apply(getSeason)

    # Seasonal Average
    seasonalAvg = longData.groupby("Season")["Temperature"].mean()

    with open("average_temp.txt", "w") as file:
        for season in ["Summer", "Autumn", "Winter", "Spring"]:
            if season in seasonalAvg:
                file.write(f"{season}: {seasonalAvg[season]:.1f}°C\n")

    # Temperature Range
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

    # Temperature Stability
    stdDevs = longData.groupby("STATION_NAME")["Temperature"].std()

    minStd = stdDevs.min()
    maxStd = stdDevs.max()

    with open("temperature_stability_stations.txt", "w") as file:

        for station, std in stdDevs.items():
            if math.isclose(std, minStd):
                file.write(
                    f"Most Stable: Station {station}: StdDev {std:.1f}°C\n"
                )

        for station, std in stdDevs.items():
            if math.isclose(std, maxStd):
                file.write(
                    f"Most Variable: Station {station}: StdDev {std:.1f}°C\n"
                )

# run program
analyseTemperatures()
