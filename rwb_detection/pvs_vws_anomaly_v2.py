{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Python Standard Import Statements\n",
    "# .............................\n",
    "import matplotlib; matplotlib.use('agg')\n",
    "\n",
    "import netCDF4\n",
    "import shapely\n",
    "import numpy as np\n",
    "import pandas as pd\n",
    "import math\n",
    "import matplotlib.pyplot as plt\n",
    "import scipy.stats as stats\n",
    "import scipy.odr as odr\n",
    "import scipy.signal as signal\n",
    "import scipy.integrate as integrate\n",
    "import importlib\n",
    "import datetime as dt\n",
    "\n",
    "# Imports for Polygon Routines\n",
    "# ..................................\n",
    "\n",
    "from netCDF4 import Dataset\n",
    "from shapely import geometry\n",
    "from shapely import ops\n",
    "from decimal import Decimal\n",
    "\n",
    "# Defined Functions to be used in script below\n",
    "# .................................................\n",
    "\n",
    "# Function for grabbing coordinates 2PVU contour path\n",
    "def get_path_coord(contour):\n",
    "    paths = []\n",
    "    paths = contour.collections[0].get_paths()\n",
    "    n = len(paths)\n",
    "    xy = []\n",
    "    length = []\n",
    "    for i in np.arange(0,n,1):\n",
    "        length.append(len(paths[i]))\n",
    "    r = np.argmax(length) # gives index of largest contour path\n",
    "    \n",
    "    paths1 = paths[r]\n",
    "    xy = paths1.vertices\n",
    "\n",
    "    for i in range(len(xy)):\n",
    "        a = xy[:,0]\n",
    "        b = xy[:,1]\n",
    "    return a, b\n",
    "# ..................................\n",
    "# Function for finding the index of the closes value\n",
    "# Input Parameter\n",
    "# ..................\n",
    "# A: Array we want the index from\n",
    "#target: The array we would like to know the indices for\n",
    "\n",
    "def getnearpos(array,value):\n",
    "    idx = (np.abs(array-value)).argmin()\n",
    "    return idx   \n",
    "\n",
    "# ..................................\n",
    "# Python code to find longest running \n",
    "# sequence of positive integers.\n",
    "\n",
    "# Problem with code. Doesn't seem to see last large positive consec\n",
    "# group. Pad data at the end with negative values.\n",
    " \n",
    "def getLongestSeq(a, n):\n",
    "    maxIdx = 0\n",
    "    maxLen = 0\n",
    "    currLen = 0\n",
    "    currIdx = 0\n",
    "    \n",
    "    #check to see if data needs padding at the end\n",
    "    for k in range(n):\n",
    "        if a[k] > 0:\n",
    "            currLen +=1\n",
    " \n",
    "            # New sequence, store\n",
    "            # beginning index.\n",
    "            if currLen == 1:\n",
    "                currIdx = k\n",
    "        else:\n",
    "            if currLen > maxLen:\n",
    "                maxLen = currLen\n",
    "                maxIdx = currIdx\n",
    "            currLen = 0\n",
    "             \n",
    "    if maxLen > 0:\n",
    "        print('Index : ',maxIdx,',Length : ',maxLen,)\n",
    "    else:\n",
    "        print(\"No positive sequence detected.\")\n",
    "    return maxIdx, maxLen\n",
    "\n",
    "# ...............................\n",
    "# Function start_end_contour\n",
    "# Function for collecting start and end points of contour\n",
    "# Input Parameters: fidx (middle index), maxl (maximum length), last (index of last value of array)\n",
    "# ...........................\n",
    "# strt_idx: index of first point of pv gradient reversal\n",
    "# maxl: length of pv gradient reversal\n",
    "# last: index of last value of array\n",
    "\n",
    "def start_end_contour(fidx,maxl,last):    \n",
    "    md_idx = fidx\n",
    "    end_idx = md_idx + maxl\n",
    "    strt_idx = md_idx - maxl\n",
    "    \n",
    "    if end_idx > last:\n",
    "        if strt_idx < 0:\n",
    "            strt_idx1 = 0\n",
    "            return strt_idx1, md_idx,last\n",
    "        else:\n",
    "            return strt_idx, md_idx, last\n",
    "    else:\n",
    "        if strt_idx < 0:\n",
    "            strt_idx1 = 0\n",
    "            return strt_idx1, md_idx, end_idx\n",
    "        else:\n",
    "            return strt_idx, md_idx, end_idx\n",
    "\n",
    "# ......................................        \n",
    "# Function retrieve_path\n",
    "# Function for retrieving path of contour and create Polygon\n",
    "# Algorithm for retrieving 2-PVU contour paths for each \n",
    "# Retrieve 2-PVU contour path.\n",
    "\n",
    "def retrieve_path(contour):\n",
    "    paths = []\n",
    "    paths = contour.collections[0].get_paths()\n",
    "    n = len(paths)\n",
    "    xy = []\n",
    "    length = []\n",
    "    for i in np.arange(0,n,1):\n",
    "        length.append(len(paths[i]))\n",
    "    r = np.argmax(length) # gives index of largest contour path\n",
    "    \n",
    "    paths1 = paths[r]\n",
    "    xy = paths1.vertices\n",
    "\n",
    "    for i in range(len(xy)):\n",
    "        a = xy[:,0]\n",
    "        b = xy[:,1]\n",
    "    poly = geometry.Polygon([(i[0],i[1]) for i in zip(a,b)])\n",
    "    \n",
    "    # find intersection between line and contour segment\n",
    "    \n",
    "    return poly\n",
    "\n",
    "# .............................\n",
    "# Function pvindex_bnds\n",
    "# Function for choosing the start point of the PV streamer segment\n",
    "# Code tests whether p2gradx2 is positive at positive p2grady2\n",
    "# Input Variables:\n",
    "# firstx, firsty: index of first value indicated by getLongSeq\n",
    "# lengthx, lengthy: length of consecutive group of positive values indicated by getLongSeq\n",
    "\n",
    "# Output Variables:\n",
    "# strt_idx, end-idx: start and end index bounds of PV streamer\n",
    "# .........................................\n",
    "\n",
    "def pvindex_bnds(datax,datay,firstx,firsty,lengthx,lengthy):\n",
    "    idx1 = np.min([firstx,firsty])  # Idnetify range over which to search\n",
    "    idx2 = np.max([firstx,firsty])+1\n",
    "    irange = np.arange(idx1,idx2,1)\n",
    "\n",
    "    for i in irange:     # Search along positive p2grady2 for index with positive p2gradx2\n",
    "        if (datay[i]>0 and datax[i]>0):\n",
    "            strt_idx = i\n",
    "            pos_length = np.max([lengthx,lengthy])  # Find index detection length (pos_length x 2) of the PV streamer.\n",
    "            end_idx = strt_idx + (pos_length*2)     # Find end index. \n",
    "            mdl_idx = strt_idx + np.min([lengthx,lengthy]) # Find middle index to be used to define PV streamer region.\n",
    "            \n",
    "            if end_idx >= len(p2grady2):            # Check whether end_idx is greater than length of contour path\n",
    "                end_idx = len(p2grady2)-2\n",
    "            else:\n",
    "                end_idx = end_idx\n",
    "            \n",
    "            if mdl_idx >= len(p2grady2):            # Check whether mdl_idx is greater than length of contour path\n",
    "                mdl_idx = len(p2grady2)-2\n",
    "            else:\n",
    "                mdl_idx = mdl_idx\n",
    "            break\n",
    "        else:\n",
    "            strt_idx = float('NaN')\n",
    "            mdl_idx = float('NaN')\n",
    "            end_idx = float('NaN')\n",
    "            pass\n",
    "            \n",
    "    return strt_idx, mdl_idx, end_idx\n",
    "\n",
    "# ....................................\n",
    "# Function data_pad\n",
    "# Pad data with negatives at the end. Section tests whether or not the very last element is positive or negative,\n",
    "# since getLongSec function doesn't \"see\" positive end values very well unless part of a significantly large\n",
    "# sequence. If end value is positive (i.e. p2grady2[-1]>0), then test is padded with -1's.\n",
    "# ...........................................................\n",
    "# Store size of p2gradx2 and p2grady2\n",
    "\n",
    "def data_pad(datax,datay):\n",
    "    # Tests if padding needed\n",
    "    if (datay[-1]>0 or datax[-1]>0):\n",
    "        testy = np.copy(datay)\n",
    "        testx = np.copy(datax)\n",
    "        pad = np.repeat(-1,5)\n",
    "        testy2 = np.hstack([testy,pad])\n",
    "        testx2 = np.hstack([testx,pad])\n",
    "    else:\n",
    "        testy2 = np.copy(datay)\n",
    "        testx2 = np.copy(datax)\n",
    "    \n",
    "    return testx2, testy2\n",
    "\n",
    "def ncdump(nc_fid, verb=True):\n",
    "    '''\n",
    "    ncdump outputs dimensions, variables and their attribute information.\n",
    "    The information is similar to that of NCAR's ncdump utility.\n",
    "    ncdump requires a valid instance of Dataset.\n",
    "\n",
    "    Parameters\n",
    "    ----------\n",
    "    nc_fid : netCDF4.Dataset\n",
    "        A netCDF4 dateset object\n",
    "    verb : Boolean\n",
    "        whether or not nc_attrs, nc_dims, and nc_vars are printed\n",
    "\n",
    "    Returns\n",
    "    -------\n",
    "    nc_attrs : list\n",
    "        A Python list of the NetCDF file global attributes\n",
    "    nc_dims : list\n",
    "        A Python list of the NetCDF file dimensions\n",
    "    nc_vars : list\n",
    "        A Python list of the NetCDF file variables\n",
    "    '''\n",
    "    def print_ncattr(key):\n",
    "        \"\"\"\n",
    "        Prints the NetCDF file attributes for a given key\n",
    "\n",
    "        Parameters\n",
    "        ----------\n",
    "        key : unicode\n",
    "            a valid netCDF4.Dataset.variables key\n",
    "        \"\"\"\n",
    "        try:\n",
    "            print (\"\\t\\ttype:\", repr(nc_fid.variables[key].dtype))\n",
    "            for ncattr in nc_fid.variables[key].ncattrs():\n",
    "                print ('\\t\\t%s:' % ncattr,\\\n",
    "                      repr(nc_fid.variables[key].getncattr(ncattr)))\n",
    "        except KeyError:\n",
    "            print (\"\\t\\tWARNING: %s does not contain variable attributes\") % key\n",
    "\n",
    "    # NetCDF global attributes\n",
    "    nc_attrs = nc_fid.ncattrs()\n",
    "    if verb:\n",
    "        print (\"NetCDF Global Attributes:\")\n",
    "        for nc_attr in nc_attrs:\n",
    "            print ('\\t%s:' % nc_attr, repr(nc_fid.getncattr(nc_attr)))\n",
    "    nc_dims = [dim for dim in nc_fid.dimensions]  # list of nc dimensions\n",
    "    # Dimension shape information.\n",
    "    if verb:\n",
    "        print (\"NetCDF dimension information:\")\n",
    "        for dim in nc_dims:\n",
    "            print (\"\\tName:\", dim) \n",
    "            print (\"\\t\\tsize:\", len(nc_fid.dimensions[dim]))\n",
    "            print_ncattr(dim)\n",
    "    # Variable information.\n",
    "    nc_vars = [var for var in nc_fid.variables]  # list of nc variables\n",
    "    if verb:\n",
    "        print (\"NetCDF variable information:\")\n",
    "        for var in nc_vars:\n",
    "            if var not in nc_dims:\n",
    "                print ('\\tName:', var)\n",
    "                print (\"\\t\\tdimensions:\", nc_fid.variables[var].dimensions)\n",
    "                print (\"\\t\\tsize:\", nc_fid.variables[var].size)\n",
    "                print_ncattr(var)\n",
    "    return nc_attrs, nc_dims, nc_vars\n",
    "\n",
    "def syn_clim(data):\n",
    "    clim0, clim6, clim12, clim18 = np.empty([73,144]),np.empty([73,144]),np.empty([73,144]),np.empty([73,144])\n",
    "    std0, std6, std12, std18 = np.empty([73,144]),np.empty([73,144]),np.empty([73,144]),np.empty([73,144])\n",
    "\n",
    "    for j in np.arange(0,144,1):\n",
    "        for i in np.arange(0,73,1):\n",
    "            clim_range = data[np.arange(0,58800,1),i,j]\n",
    "            dates = pd.date_range('1979-01-01','2019-04-01',freq='6H')\n",
    "            clim_frame = pd.Series(clim_range,index=dates[0:58800])\n",
    "            clim = clim_frame.groupby(clim_frame.index.hour).mean()\n",
    "            clim2 = np.array(clim.values)\n",
    "            pvstd = clim_frame.groupby(clim_frame.index.hour).std()\n",
    "            pvstd2 = np.array(pvstd.values)\n",
    "        \n",
    "            clim0[i,j], clim6[i,j], clim12[i,j], clim18[i,j] = clim2[0],clim2[1],clim2[2],clim2[3]\n",
    "            std0[i,j], std6[i,j], std12[i,j], std18[i,j] = pvstd2[0],pvstd2[1],pvstd2[2],pvstd2[3]\n",
    "    \n",
    "    return clim0, clim6, clim12, clim18, std0, std6, std12, std18\n",
    "# .......................................\n",
    "# NC file input 1\n",
    "\n",
    "ncfile1='/home/jjpjones/pvs_vws_indices/era5_ucombined_6hrly.nc'\n",
    "ncf1 = Dataset(ncfile1,'r')\n",
    "nc_attrs1, nc_dims1, nc_vars1 = ncdump(ncf1)\n",
    "\n",
    "# Extract data from NetCDF file\n",
    "lat = ncf1.variables['latitude'][:]\n",
    "lon = ncf1.variables['longitude'][:]\n",
    "time = ncf1.variables['time'][:]\n",
    "lev1 = ncf1.variables['level'][:]\n",
    "u = ncf1.variables['u'][:]\n",
    "\n",
    "# List all times in file as datetime objects\n",
    "time2 = [int(i) for i in time]\n",
    "dt_time = [dt.date(1900,1,1) + dt.timedelta(hours=t) for t in time2]\n",
    "\n",
    "# NC file input 2\n",
    "\n",
    "ncfile2='/home/jjpjones/pvs_vws_indices/era5_pv350k_6hrly_v2.nc'\n",
    "ncf2 = Dataset(ncfile2,'r')\n",
    "nc_attrs2, nc_dims2, nc_vars2 = ncdump(ncf2)\n",
    "\n",
    "pv = ncf2.variables['pv'][:]\n",
    "\n",
    "# Identify zonal wind levels\n",
    "u200 = np.copy(u[0:58800,0,0:73,0:144])\n",
    "u850 = np.copy(u[0:58800,1,0:73,0:144])\n",
    "\n",
    "vws = u200 - u850;  # deep-layer shear\n",
    "\n",
    "# Find synoptic climatology\n",
    "uclim0, uclim6, uclim12, uclim18, ustd0, ustd6, ustd12, ustd18 = syn_clim(vws)\n",
    "pclim0, pclim6, pclim12, pclim18, pstd0, pstd6, pstd12, pstd18 = syn_clim(pv)\n",
    "\n",
    "# Define dates dataframe structure\n",
    "dates = pd.date_range('1979-01-01','2019-04-01',freq='6H')\n",
    "\n",
    "# Set up empty arrays\n",
    "vup_full, vdn_full = [], []\n",
    "\n",
    "for q in np.arange(0,58800,1):\n",
    "    # Define field and calculate meridional pv gradient field\n",
    "    pv_field = pv[q,0:73,0:143]\n",
    "    pv_diffx = np.gradient(pv_field, axis=0)\n",
    "    pv_diffy = np.gradient(pv_field, axis =1)\n",
    "    \n",
    "    # Plot 2PVU contour and retrieve coordinates along path\n",
    "    cs1 = []\n",
    "    fig,ax = plt.subplots()\n",
    "    cs1 = ax.contour(lon[104:143],lat[12:34],pv_field[12:34,104:143],levels=[2e-6])\n",
    "    a, b = get_path_coord(cs1)\n",
    "    # ...........................................\n",
    "    \n",
    "    # Retrieve indices for contour coordinates\n",
    "    \n",
    "    idxlt, idxln = [], []\n",
    "    for r in b:\n",
    "        idxlt.append(getnearpos(lat,r))\n",
    "    \n",
    "    for r in a:\n",
    "        idxln.append(getnearpos(lon,r))\n",
    "    \n",
    "    idxlt = np.flipud(np.array(idxlt)) # convert to array. Update v2: position indices flipped to move from \n",
    "    idxln = np.flipud(np.array(idxln)) # left to right  \n",
    "    # ...........................................\n",
    "    \n",
    "    # Retrieve pv gradient values corresponding to 2PVU contour\n",
    "    # Added array for zonal pv gradient field\n",
    "\n",
    "    p2gradx, p2grady = [],[]\n",
    "    p2gradx.append(pv_diffx[idxlt,idxln])\n",
    "    p2grady.append(pv_diffy[idxlt,idxln])\n",
    "    \n",
    "    # Convert lists to arrays\n",
    "    p2gradx = np.array(p2gradx)\n",
    "    p2grady = np.array(p2grady)\n",
    "    \n",
    "    # Change from hstack to vstack\n",
    "    p2gradx2 = p2gradx[0,:]\n",
    "    p2grady2 = p2grady[0,:]\n",
    "    \n",
    "    # ...........................................\n",
    "    # Update v2: Data padding moved to user-defined function data_pad. pvindex_bnds replaces\n",
    "    # start_end_contour.\n",
    "    # Find largest group of consecutive positive values\n",
    "    # Create temporary array (test) and pad data with negatives \n",
    "    # at the end.\n",
    "    \n",
    "    # Section tests whether or not the very last element is positive or negative\n",
    "    # since getLongSec function doesn't \"see\" positive end values very well. If \n",
    "    # end value is positive (i.e. p2grad2[-1]>0), then test is padded with -1's.\n",
    "    testx, testy = data_pad(p2gradx2,p2grady2) \n",
    "    \n",
    "    \n",
    "    # Check for a large group of consecutive positive integers in zonal meridional pv gradient\n",
    "    #test\n",
    "    pidxy1, plenty1 = getLongestSeq(testy,len(testy))\n",
    "    pidxx1, plentx1 = getLongestSeq(testx,len(testx))\n",
    "   \n",
    "    if (plenty1 >1 and plentx1 >1):\n",
    "        strt1, mid1, end1 = pvindex_bnds(testx,testy,pidxx1,pidxy1,plentx1,plenty1)\n",
    "    else:\n",
    "        print('Step pvindex_bnds: No primary PV detected at timestep: '+ str(q))\n",
    "        strt1 = float('NaN')\n",
    "        mid1 = float('NaN')\n",
    "        end1 = float('NaN')\n",
    "\n",
    "    # ...........................................\n",
    "    # After obtaining start, middle and end locations of PV streamer\n",
    "    # Find standardized anomalies along locations upstream and downstream of first PVS\n",
    "    # Upstream defined as strt to mid indices; downstream defined as mid+1 to end indices\n",
    "    \n",
    "    if np.isnan(strt1) == False:\n",
    "        if not mid1 == end1:\n",
    "            mid12 = mid1 + 1\n",
    "            if dates[q].hour == 0:\n",
    "                vup_std1 = np.sum((vws[q,idxlt[strt1:mid1],idxln[strt1:mid1]] - uclim0[idxlt[strt1:mid1],idxln[strt1:mid1]])/ustd0[idxlt[strt1:mid1],idxln[strt1:mid1]])\n",
    "                vdn_std1 = np.sum((vws[q,idxlt[mid12:end1],idxln[mid12:end1]] - uclim0[idxlt[mid12:end1],idxln[mid12:end1]])/ustd0[idxlt[mid12:end1],idxln[mid12:end1]])\n",
    "            elif dates[q].hour == 6:\n",
    "                vup_std1 = np.sum((vws[q,idxlt[strt1:mid1],idxln[strt1:mid1]] - uclim6[idxlt[strt1:mid1],idxln[strt1:mid1]])/ustd6[idxlt[strt1:mid1],idxln[strt1:mid1]])\n",
    "                vdn_std1 = np.sum((vws[q,idxlt[mid12:end1],idxln[mid12:end1]] - uclim6[idxlt[mid12:end1],idxln[mid12:end1]])/ustd6[idxlt[mid12:end1],idxln[mid12:end1]])\n",
    "            elif dates[q].hour == 12:\n",
    "                vup_std1 = np.sum((vws[q,idxlt[strt1:mid1],idxln[strt1:mid1]] - uclim12[idxlt[strt1:mid1],idxln[strt1:mid1]])/ustd12[idxlt[strt1:mid1],idxln[strt1:mid1]])\n",
    "                vdn_std1 = np.sum((vws[q,idxlt[mid12:end1],idxln[mid12:end1]] - uclim12[idxlt[mid12:end1],idxln[mid12:end1]])/ustd12[idxlt[mid12:end1],idxln[mid12:end1]])\n",
    "            elif dates[q].hour == 18:\n",
    "                vup_std1 = np.sum((vws[q,idxlt[strt1:mid1],idxln[strt1:mid1]] - uclim18[idxlt[strt1:mid1],idxln[strt1:mid1]])/ustd18[idxlt[strt1:mid1],idxln[strt1:mid1]])\n",
    "                vdn_std1 = np.sum((vws[q,idxlt[mid12:end1],idxln[mid12:end1]] - uclim18[idxlt[mid12:end1],idxln[mid12:end1]])/ustd18[idxlt[mid12:end1],idxln[mid12:end1]])\n",
    "            else:\n",
    "                vup_std1 = float('NaN')\n",
    "                vdn_std1 = float('NaN')\n",
    "        else:\n",
    "            print('No PV detected.')\n",
    "            vup_std1 = float('NaN')\n",
    "            vdn_std1 = float('NaN') \n",
    "    else:\n",
    "        print('No PV detected.')\n",
    "        vup_std1 = float('NaN')\n",
    "        vdn_std1 = float('NaN') \n",
    "             \n",
    "        \n",
    "    # ....................................................................\n",
    "    # Check for a second major group of consecutive positive integers by\n",
    "    # removing first group (replaced with -1's)\n",
    "    if np.isnan(strt1) == False:\n",
    "        zero_pad1 = np.abs(end1 - strt1)\n",
    "        y_remaining = np.copy(testy)\n",
    "        y_remaining[strt1:end1] = np.repeat(-1,zero_pad1)\n",
    "\n",
    "        x_remaining = np.copy(testx)\n",
    "        x_remaining[strt1:end1] = np.repeat(-1,zero_pad1)\n",
    "\n",
    "        pidxy2, plenty2 = getLongestSeq(y_remaining,len(y_remaining))\n",
    "        pidxx2, plentx2 = getLongestSeq(x_remaining,len(x_remaining))\n",
    "    \n",
    "        # Check to make sure that lengths of group are greater than 0. \n",
    "        if (plenty2 > 1 and plentx2 > 1):\n",
    "            strt2, mid2, end2 = pvindex_bnds(x_remaining,y_remaining,pidxx2,pidxy2,plentx2,plenty2)\n",
    "        else:\n",
    "            print('Step 2nd pvindex_bnds: No primary PV detected at timestep: '+ str(q))\n",
    "            strt2 = float('NaN')\n",
    "            mid2 = float('NaN')\n",
    "            end2 = float('NaN')\n",
    "            \n",
    "        if np.isnan(strt2) == False:\n",
    "            mid22 = mid2 + 1\n",
    "            if not mid2 == end2: \n",
    "                if dates[q].hour == 0:\n",
    "                    vup_std2 = np.sum((vws[q,idxlt[strt2:mid2],idxln[strt2:mid2]] - uclim0[idxlt[strt2:mid2],idxln[strt2:mid2]])/ustd0[idxlt[strt2:mid2],idxln[strt2:mid2]])\n",
    "                    vdn_std2 = np.sum((vws[q,idxlt[mid22:end2],idxln[mid22:end2]] - uclim0[idxlt[mid22:end2],idxln[mid22:end2]])/ustd0[idxlt[mid22:end2],idxln[mid22:end2]])\n",
    "                elif dates[q].hour == 6:\n",
    "                    vup_std2 = np.sum((vws[q,idxlt[strt2:mid2],idxln[strt2:mid2]] - uclim6[idxlt[strt2:mid2],idxln[strt2:mid2]])/ustd6[idxlt[strt2:mid2],idxln[strt2:mid2]])\n",
    "                    vdn_std2 = np.sum((vws[q,idxlt[mid22:end2],idxln[mid22:end2]] - uclim6[idxlt[mid22:end2],idxln[mid22:end2]])/ustd6[idxlt[mid22:end2],idxln[mid22:end2]])\n",
    "                elif dates[q].hour == 12:\n",
    "                    vup_std2 = np.sum((vws[q,idxlt[strt2:mid2],idxln[strt2:mid2]] - uclim12[idxlt[strt2:mid2],idxln[strt2:mid2]])/ustd12[idxlt[strt2:mid2],idxln[strt2:mid2]])\n",
    "                    vdn_std2 = np.sum((vws[q,idxlt[mid22:end2],idxln[mid22:end2]] - uclim12[idxlt[mid22:end2],idxln[mid22:end2]])/ustd12[idxlt[mid22:end2],idxln[mid22:end2]])\n",
    "                elif dates[q].hour == 18:\n",
    "                    vup_std2 = np.sum((vws[q,idxlt[strt2:mid2],idxln[strt2:mid2]] - uclim18[idxlt[strt2:mid2],idxln[strt2:mid2]])/ustd18[idxlt[strt2:mid2],idxln[strt2:mid2]])\n",
    "                    vdn_std2 = np.sum((vws[q,idxlt[mid22:end2],idxln[mid22:end2]] - uclim18[idxlt[mid22:end2],idxln[mid22:end2]])/ustd18[idxlt[mid22:end2],idxln[mid22:end2]])\n",
    "                else:\n",
    "                    vup_std2 = float('NaN')\n",
    "                    vdn_std2 = float('NaN')\n",
    "            else:\n",
    "                print('No PV detected.')\n",
    "                vup_std2 = float('NaN')\n",
    "                vdn_std2 = float('NaN')\n",
    "        else:\n",
    "            print('No PV detected.')\n",
    "            vup_std2 = float('NaN')\n",
    "            vdn_std2 = float('NaN')\n",
    "    else:\n",
    "        print('No 2nd PV detected.')\n",
    "        vup_std2 = float('NaN')\n",
    "        vdn_std2 = float('NaN') \n",
    "        \n",
    "\n",
    "    # Find total standardized VWS anomalies\n",
    "    vup_total = vup_std1 + vup_std2\n",
    "    vdn_total = vdn_std1 + vdn_std2\n",
    "    \n",
    "    # Append to daily index\n",
    "    vup_full.append(vup_total)\n",
    "    vdn_full.append(vdn_total)\n",
    "    \n",
    "    print('Field at ', q, 'is complete.')\n",
    "    \n",
    "subdaily_vdn = np.array(vdn_full); subdaily_vup = np.array(vup_full)\n",
    "np.savetxt('/home/jjpjones/pvs_vws_indices/subdaily_vwsdn_idx.txt',vdn_full,delimiter=' ')\n",
    "np.savetxt('/home/jjpjones/pvs_vws_indices/subdaily_vwsup_idx.txt',vup_full,delimiter=' ')"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.7.1"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}