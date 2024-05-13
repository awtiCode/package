import numpy as np
# Function to fill missing values using Arithmetic Mean
def fill_missing_data_arithmetic(data):
    """
    Fills missing numerical values using the Arithmetic Mean method.
    """
    row_wise_means = data.mean(axis=1)
    fill_dict = {column: row_wise_means for column in data.columns}
    filled_data = data.fillna(fill_dict)
    filled_data.element = data.element
    return filled_data


# Function to fill missing values using Normal Ratio method
def fill_missing_data_normal_ratio(data):
    """
    Fill missing rainfall values in a DataFrame using the normal ratio.
    """
    data = data.copy()
    # Trying to fill all station by going through a data
    for station_name in data.columns:
        try:
            Ni = data.resample(rule='Y').sum().mean()
            Pi_Ni = data / Ni
            Pi_Ni_Sum = Pi_Ni.drop(station_name, axis=1).sum(axis=1)
            Na = Ni[station_name]
            n = data.drop(station_name, axis=1).notna().sum(axis=1)
            fill_data = (Na / n) * Pi_Ni_Sum
            data[station_name] = data[station_name].fillna(fill_data)
        except Exception as e:
            print(f"Error for {station_name}: {e}")

    return data

def fill_missing_data_inverse_distance(data, coord_data, power = 2):

    filled_data = data.copy()

    # Combine latitude and longitude into a DataFrame 'coordinates'
    for missing_station in filled_data.columns:      
        station_coords = coord_data.loc[missing_station, ['latitude', 'longitude']].values 
        distances = np.sqrt((station_coords[0] - coord_data.loc[coord_data.index!=missing_station,'latitude'])**2 + (station_coords[1] - coord_data.loc[coord_data.index!=missing_station,'longitude'])**2)
        weights = 1 / (distances ** power)
        other_station_data = data.loc[:,data.columns!=missing_station]
        weighted_station_data = other_station_data*weights
        weightsdf = weighted_station_data.copy()
        for col in weightsdf:
            weightsdf.loc[:,col] = weights[col]
        weightsdf[weighted_station_data.isna()] = np.nan
        fill_with = weighted_station_data.sum(axis=1) / weightsdf.sum(axis=1)
        filled_data.loc[:,missing_station] = data.loc[:,missing_station].fillna(fill_with)

    return filled_data
