import pandas as pd

def dataLoad(filepath,element,sheetname=None,stations_col=None,station_name=None,headerrow=0):
    '''
    Load the data from common Ethiopian Meteorology Institute station file formats (csv or excel).

    Parameters
    ----------
    filepath : STR
        Path to datafile.
    element : STR
        Name of element. If there are multiple elements in the data, specify which one to use by supplying that exact name.
    sheetname : None or INT or STR, optional
        If the datafile is an excel file with multiple sheets, specify the sheet number (starting from 0) or name as STR. The default is None.
    stations_col : None or STR, optional
        If there is a column in the datafile that specifies the different stations, supply the name of that column. The default is None (no column with station names).
    station_name : None or STR, optional
        Only used if stations_col=None. If there is data for only one station in the file, you can supply the station's name as string.
    headerrow : INT, optional
        The row number for the row that contains column headers (starting from 0). The default is 0 (headers on the first row).

    Returns
    -------
    datanew : DataFrame
        Data for the requested element, indexed by date, with a column per station.
        The requested element name can be found under datanew.element
    '''
    import warnings
    warnings.simplefilter(action='ignore', category=UserWarning)
    
    # Load data
    if filepath.endswith('.xlsx'):    
        data = pd.read_excel(filepath,sheetname,header=headerrow)
    else:
        data = pd.read_csv(filepath,header=headerrow)
    
    # Select element
    if len(data.columns)>34:
        el_col = data.columns[(data==element).sum()>0]
        if not list(el_col):
            print('Error: Element not found. Please give a name that is present inside the column with elements.')
            return
        else:
            data = data[data[el_col[0]]==element]
    
    # Check for stations_col validity
    if stations_col!=None:
        if stations_col not in data.columns:
            print(f'Error: The column name {stations_col} is given by the user, but not found in the column names. Make sure you specified the correct header-row number.')
            return
    
    # Check for year/day or year/month format
    cols_found = False
    for i,name in zip(range(len(data.columns)-1,-1,-1),data.columns[::-1]):
        value_cols = None
        if type(name) == str:
            if 'de' in name.lower() or '12' in name:
                value_cols = data.columns[i-11:i+1]
            elif '31' in name:
                value_cols = data.columns[i-30:i+1]
        else:
            if name == 31:
                value_cols = data.columns[i-30:i+1]
            elif name == 12:
                value_cols = data.columns[i-11:i+1]
        if type(value_cols)!=type(None):
            cols_found = True
            break
    if not cols_found:
        print('Eror: Day or month columns could not be found. Make sure you specified the correct header-row number, that column names have a number in them (1-12 for months, 1-31 for days), or month names.')
        return
    
    # Get year column number, and fill missing data forward if needed
    year_found = False
    for i,name in enumerate(data.columns):
        if 'y' in name.lower():
            yearcol = name
            year_found = True
            break
    if not year_found:
            print('Error: No columnname "year" found. Make sure you specified the correct header-row number, and that one of the column names is "year".')
            return        
    datecol = data.columns[i+1]
    
    cols = [yearcol,datecol]+list(value_cols)
    datename = 'day' if len(value_cols) == 12 else 'month'
    newcols = ['year',datename] + list(range(1,len(value_cols)+1))
    if stations_col!=None:
        cols.insert(0,stations_col)
        newcols.insert(0,'station')
    data = data.get(cols)
    data = data.set_axis(newcols,axis=1)
    
    # Clean up year and date column
    data.year.fillna(method='ffill',inplace=True)
    data[datename].fillna(value=0,inplace=True)
    data = data.astype({'year':'int32',newcols[1]:'int32'})
    
    # Melt
    var_name = 'month' if len(value_cols) == 12 else 'day'
    id_vars = newcols[:2] if stations_col==None else newcols[:3]    
    
    datamelt = data.melt(id_vars = id_vars, var_name = var_name)
    
    # Create datetime
    dt = pd.to_datetime(datamelt.get(['year','month','day']),errors='coerce')
    datamelt['datetime'] = dt
    datamelt.dropna(subset='datetime',inplace=True)
    
    # Select only datetime and data
    datacols = ['datetime','value']
    if stations_col != None: datacols = ['station'] + datacols
    dataout = datamelt.get(datacols)
    dataout.loc[:,'value'] = pd.to_numeric(dataout.value,errors='coerce')
    
    # Get one value per day  
    groupby = [dataout.dropna().datetime.dt.date]
    if stations_col != None:
        groupby += [dataout.dropna()['station']]
    
    coldata = dataout.value
    if 'rain' in element.lower() or 'rf' in element.lower() or 'prec' in element.lower():
        datanew = coldata.dropna().groupby(by=groupby).sum().reset_index()
    else:
        datanew = coldata.dropna().groupby(by=groupby).mean().reset_index()
     
    # Pivot stations
    if stations_col != None:
        datanew = datanew.pivot(columns = 'station',index='datetime',values='value')
    else:
        datanew = datanew.set_index('datetime')
        if len(datanew.columns) == 1 and 'value' in datanew.columns:
            if station_name == None: 
                print('WARNING: Station name unknown. You can supply a stationname by including "station_name=STATIONNAME".\n')
                station_name = 'UnknownStation'
            datanew = datanew.set_axis([station_name],axis=1)
    
    # Set index to full years
    datanew = datanew.set_index(pd.to_datetime(datanew.index))
    i_start = pd.to_datetime(str(datanew.index.year.min()))
    i_end = pd.to_datetime(str(datanew.index.year.max()+1))-pd.to_timedelta(1,'D')
    
    datanew = datanew.reindex(pd.date_range(i_start,i_end))
    datanew.element = element
    
    # Prepare information print
    nstations = len(datanew.columns)
    station_info = f'for station {station_name}' if nstations==1 else f'for {nstations} stations'
    year_info = f'years {i_start.year}-{i_end.year}'
    print(f'Data loaded for element {element}, {year_info}, {station_info}.')
    
    return datanew

def coordDataLoad(filepath,station_col = 'station', lat_col = 'latitude', lon_col = 'longitude'):
    '''
    This function assumes you are loading a file with three columns, named 'station', 'latitude' and 'longitude'. 
    
    You can simply supply filepath, and make sure that; your data have correctily spelled the 'station', 'latitude', and 'longitude'
    
    It returns a dataframe that can be used for the inverse distance weighting function, as 'coord_data'.
    '''
    try:
        coord_data = pd.read_csv(filepath)[[station_col,lat_col,lon_col]].set_axis(['station','latitude','longitude'],axis=1)
        coord_data = coord_data.drop_duplicates(subset=['station']).set_index('station')
        print(f"Coordinates loaded for {len(coord_data)} stations.")
        return coord_data      
    except Exception as e:
        print(f"An error occurred: {e}")
