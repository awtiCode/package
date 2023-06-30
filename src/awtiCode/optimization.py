# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

# Import packages
from ortools.sat.python import cp_model
import pandas as pd
import numpy as np

def cropSchedule(waterAvailable=100000,landAvailable=2000,noCrops=4,
                 cropCycle=[3,4,5,4],waterUse=[300,200,350,400],
                 cropProfit=[75000,60000,100000,150000],**moreOptions):
    """
    This function calculates the yearly crop schedule that gives the most profit, given certain conditions (constraints). The constraints can be set through the parameters.

    Parameters
    ----------
    waterAvailable : int or list of ints
        The available water per month. If not specified, this is set to 100000.
        If an integer is provided, this value is used for all months.
        A list can be used to specify 12 (different) values, representing availability per month.
    landAvailable : int
        The available area of land. If not specified, this is set to 2000.
    noCrops : int
        Number of crops. If not specified, 4 crops are assumed.
    cropCycle : list of ints, length of list should be equal to noCrops
        Per crop, the number of months from sowing to harvest. If not specified, as example the list [3,4,5,4] is used, which will only work if noCrops = 4.
        If for a crop the time from sowing to harvest is a year or longer, the cropcycle should be set to 12, and you probably will need to use the arguments noYrs and yrsToProfit (see below under **moreOptions).
    waterUse : list of ints, length of list should be equal to noCrops
        Per crop the water use per unit of land area per month. The sum of all total crop areas times this water use will be <= waterAvailable. If not specified, as example the list [300,200,350,400] is used, which will only work if noCrops = 4.
    cropProfit : list of ints, length of list should be equal to noCrops
        Per crop, the profit per unit of land area per harvest. If not specified, as example the list [75000,60000,100000,150000] is used, which will only work if noCrops = 4.
        If a crop has a time from sowing to first harvest longer than a year, but then can be harvested for example every month, the cropCycle should be set to 12, but the profit should be set to profit per harvest * (12 / months between each harvest).
    
    **moreOptions : Other options that can be set, are the following (ALL optional):
        
        cropNames : list of names for the crops.
            The lenght of the list should equal the number of crops (noCrops).
            If used, the provided names will be used in the output.
            If not used, names will be 'c1' to 'cx' (x = noCrops)
        cropOffSeason : dict with key:value being integer:list of integers
            x:[1,2,3] represents the xth crop not growing during months 1, 2 and 3.
            To set that the 2nd and 3rd crop cannot grow during months 2 and 3, use 'cropOffSeason = {2:[2,3],3:[2,3]}'
            If not used, all crops can grow all months.
        noYrs : integer
            The number of years this schedule represents. Total profit is maximized as landArea * profit. The schedule represents one year, but if noYrs>1 the profit for 1 year is multiplied with the given number of years.
            If unused, noYrs = 1.
        yrsToProfit : list of integers with length equal to noCrops.
            Per crop, the number of whole years between sowing and harvest. If a cropcycle is less than a year, the value should be set to 0. If the cropcycle is for example 1 years, value should be set to 1.
            If unused, a list of zeros is used.
        maxTime : integer
            The maximum calculation time of the solver, in seconds.
            If unused, this is set to 10 seconds.

    Returns
    -------
    cropsDf : Pandas DataFrame
        A summary of settings and results for all month/crop combinations.

    """
    
    
    ############################## SETTINGS ########################################
    if type(waterAvailable) == int:    
        waterAvailable = [waterAvailable]
    if len(waterAvailable) == 1:
        waterAvailable=list(waterAvailable)*12
    available_water_per_month = np.array(waterAvailable)
    if _lenCheck(available_water_per_month,'waterAvailable'):
        return
    
    available_land = landAvailable
    
    # Crop settings
    crops = np.array(['c'+str(i) for i in range(1,noCrops+1)])

    if 'cropNames' not in moreOptions.keys():
        cropNames = crops
    else:
        cropNames = moreOptions['cropNames']
        if _lenCheck(cropNames,'cropNames','perCrop',noCrops):
            return
        else:
            cropNames = cropNames
    
    cropNdict = dict(zip(crops,cropNames))
    
    cropCycle = np.array(cropCycle)
    if _lenCheck(cropCycle,'cropCycle','perCrop',noCrops):
        return
    
    waterconstraint = np.array(waterUse)
    if _lenCheck(waterconstraint,'waterUse','perCrop',noCrops):
        return
    
    profit = np.array(cropProfit)
    if _lenCheck(profit,'cropProfit','perCrop',noCrops):
        return
    
    moreOptions_options = ['cropNames','cropOffSeason','noYrs','yrsToProfit','maxTime']
    for key in moreOptions.keys():
        if key not in moreOptions_options:
            print(f'WARNING: The argument {key} is not recognized. The only additional arguments are {str(moreOptions_options)}.')
    
    if 'cropOffSeason' not in moreOptions.keys():
        cropOffSeason = {}
    else:
        cropOffSeason = moreOptions['cropOffSeason']
        newDict = {}
        for key in cropOffSeason.keys():
            newkey = str(key)
            if newkey.isdecimal():
                newkey = 'c'+newkey
            if newkey in crops:
                monthsOff = cropOffSeason[key]
                newDict[newkey] = monthsOff
                print(f'Crop {cropNdict[newkey]} will not be grown in months {",".join(str(i) for i in monthsOff)}.')
            else:
                print(f'ERROR: Given cropOffSeason key \'{key}\' not correct. Please give a number representing the crop you want to exclude for certain months.')
                return
        cropOffSeason = newDict
    
    # Settings for crops that take more than a year
    if 'noYrs' not in moreOptions.keys():
        noYrs = 1
    else:
        
        noYrs = moreOptions['noYrs']
    
    if 'yrsToProfit' not in moreOptions.keys():
        yrsToProfit = [0]*noCrops
    else:
        yrsToProfit = np.array(moreOptions['yrsToProfit'])
        if _lenCheck(yrsToProfit,'yrsToProfit','perCrop',noCrops):
            return
    
    # Solver settings
    if 'maxTime' not in moreOptions.keys():
        maxTime = 10
    else:
        maxTime = moreOptions['maxTime']
       
    ######################### FROM HERE: DO NOT CHANGE ############################
    
    # from ortools.sat.python import cp_model
    model = cp_model.CpModel()
    
    # Create the variables
    no_months = 12
    
    var_upper_bound = 100000
    months = str(list(range(1,no_months+1)))[1:-1].split(', ')
    cropvars = {}
    sowvars = {}
    croplist = []
    monthlist = []
    for crop in crops:
        for month in months:
            cropvar = crop+'m'+month
            sowvar = crop+'m'+month+'sow'
            cropvars[cropvar] = model.NewIntVar(0, var_upper_bound ,cropvar)
            sowvars[cropvar] = model.NewBoolVar(sowvar)
            croplist.append(crop)
            monthlist.append('m'+month)
    
    cropsDf = pd.DataFrame({'names':cropvars.keys(),'variables':cropvars.values()}).set_index('names')
    
    cropsDf['crop'] = croplist
    cropsDf['cropname'] = cropsDf.crop.replace(crops,cropNames)
    cropsDf['month'] = monthlist
    cropsDf['waterconstraint'] = cropsDf.crop.replace(crops,waterconstraint)
    cropsDf['profit'] = cropsDf.crop.replace(crops,profit)
    cropsDf['cropcycle'] = cropsDf.crop.replace(crops,cropCycle)
    cropsDf['monthInt'] = cropsDf.month.str.slice(1).astype(int)
    cropsDf['yrsNoProfit'] = cropsDf.crop.replace(crops,yrsToProfit)
    
    # Create water constraints
    for i, month in enumerate(months):
        monthname = 'm'+month
        multiply = cropsDf.variables*cropsDf.waterconstraint
        monthmultiply = multiply[cropsDf.index.str.slice(2)==monthname]
        model.Add(sum(monthmultiply)<= available_water_per_month[i])
    
    # Create land constraints
    for month in months:
        monthname = 'm'+month
        monthvars = cropsDf.variables[cropsDf.month==monthname]
        model.Add(monthvars.sum() <= available_land)    
    
    # Certain crops cannot grow during certain months (cropOffSeason)
    if len(cropOffSeason)>0:
        for crop in cropOffSeason.keys():
            yrmonths = np.array(cropOffSeason[crop])
            monthsOff = yrmonths.astype(int)
            for month in monthsOff:
                variable = cropsDf.variables[(cropsDf.monthInt==month)&(cropsDf.crop==crop)][0]
                model.Add(variable==0)
    
    # Sowing constraints
    #### Depending on cropcycle: if crop is sown (sowvar[crop]==True), the following cropvars should be equal
    #### Also, then all next sowvar[crop] should be false
    for cropvar,sowvar in sowvars.items():          # Take all cropvars and sowvars one by one
        crop = cropvar[:cropvar.find('m')]                          # Take cropname
        cycle = cropCycle[list(crops).index(crop)]                     # Take cycle that matches cropname
        month = cropvar[cropvar.find('m'):]                         # Take month from cropvar
        monthno = int(month[1:])                    # Take month as integer
        for i in range(monthno+1,monthno+cycle):    # Go over all months succeeding the cropvar month 
            if i > no_months:                             # Break if outside of 12 month range
                i -= 12
            varname = crop+'m'+str(i)               # Create cropvar names succeeding the cropvar 
            model.Add(cropvars[cropvar]==cropvars[varname]).OnlyEnforceIf(sowvar)   # Succeeding months must be                                                                     
                                                                                    # equal to cropvar month when
                                                                                    # sowvar of original month 
                                                                                    # is true.
            model.Add(sowvars[varname]==0).OnlyEnforceIf(sowvar)    # Succeeding sowvars must be False because 
                                                                    # you cannot sow again on same ground until
                                                                    # cropcycle is finished.
    
    #### A month must be zero, if within it's preceding cropcycle all sowvariables are zero or own sowvar is zero
    for cropvar, sowvar in sowvars.items():         # Go over all cropvars
        crop = cropvar[:cropvar.find('m')]                           # Take cropname
        cycle = cropCycle[list(crops).index(crop)]                      # Take cycle that matches cropname
        month = cropvar[cropvar.find('m'):]                         # Take month from cropvar
        monthno = int(month[1:])                    # Take month as integer
        
        constraint = f'model.Add(cropvars[\'{cropvar}\']==0)'       # Start basic constraint string
    
        for i in list(range(monthno-cycle+1, monthno+1))[::-1]:   # For the length of cropcycle, go over all preceding cropvars (limited by size of year) 
            if i <= 0: 
                i += 12
            varname = crop + 'm' + str(i)
            constraint = constraint + f'.OnlyEnforceIf(sowvars[\'{varname}\'].Not())'   
                    # Add OnlyEnforceIf(sowvars[preceding_cropvar].Not()) to constraint string
        exec(constraint)    # Execute constraint string
    
    #### A month cannot be zero, if the corresponding sowvariable is one
    for cropvar, sowvar in sowvars.items():
        model.Add(cropvars[cropvar]>0).OnlyEnforceIf(sowvar)
    
    # solve it
    ### to take crop cycles into account (per cycle, only one yield), //cropcycle
    profitweight = cropsDf.profit*(noYrs-cropsDf.yrsNoProfit)//cropsDf.cropcycle
    model.Maximize(sum(cropsDf.variables*profitweight))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = maxTime

    status = solver.Solve(model)
    
    for name,variable in zip(cropsDf.index,cropsDf.variables):
        cropsDf.loc[name,'hectare'] = solver.Value(variable)
        cropsDf.loc[name,'result'] = str((solver.Value(sowvars[name]),solver.Value(variable)))
    
    cropsResult = cropsDf.pivot(index='monthInt',columns='cropname',values='result').get(cropNames)
    objVal = solver.ObjectiveValue()/1000000
    print('\nTotal profit: '+str(int(objVal))+' million.')
    print('Monthly per crop: (sowing,hectare), with sowing 0 (no) or 1 (yes).\n',cropsResult)
    
    return cropsDf

def _lenCheck(collection,name,colType = 'monthly',noCrops=None):
    if colType == 'monthly':
        if len(collection)!=12:
            print(f'ERROR: {name} did not get a collection of 12 values. Please provide 12 values, representing the monthly value.')
            return True
        else:
            return False
    if colType == 'perCrop':
        if len(collection)!=noCrops:
            print(f'ERROR: {name} did not get a collection of with the same number of values as the number of crops. Please provide '+str(noCrops)+' values, representing the different crops.')
            return True
        else:
            return False