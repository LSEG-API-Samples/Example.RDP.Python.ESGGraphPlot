import getpass as gp

username=input('Enter EDP username:')
clientid=input('Enter client id/app id:')
password=gp.getpass('Enter EDP Password:')

from json import dumps, loads, load
from requests import post,get

#Get access token from EDP server 
getTokenEndpoint="https://api.refinitiv.com/auth/v1/beta1/token"
refreshToken=None
accessToken=None
_header= {}
_header['Accept']='application/json'
_params={}

if refreshToken is None:
    _params={
        "username": username,
        "password": password,
        "client_id": clientid,
        "grant_type": "password",
        "scope": "trapi",
        "takeExclusiveSignOnControl": "true"
    }
else:
    _params={
			"refresh_token": refreshToken,
			"username": username,
			"grant_type": "refresh_token"
    }

resp=post(url=getTokenEndpoint,data=_params,headers=_header,auth=(username,""))
if resp.status_code!=200:
    print("Status Code:",resp.status_code," Text:",dumps(loads(resp.text),indent=4))
    exit()
else:
    #print(dumps(loads(resp.text),indent=4))
    from collections import OrderedDict
    auth_object=loads(resp.text,object_pairs_hook=OrderedDict)
    accessToken=auth_object["access_token"]
    refreshToken=auth_object["refresh_token"]

print("Refresh Token:",refreshToken)
print("Access Token:",accessToken)

esgUniverseEndpoint="https://api.refinitiv.com/data/environmental-social-governance/v2/universe"
resp=get(url=esgUniverseEndpoint,headers={"Authorization": "Bearer " + accessToken})
if resp.status_code!=200:
    print("Status Code:",resp.status_code," Text:",dumps(loads(resp.text),indent=4))
    exit()
    
esg_universe = loads(resp.text)

def GetRicName(ricName):
    if 'data' in esg_universe:
        searchItem = list(filter(lambda data: data[1]==ricName, list(esg_universe['data'])))
        if len(searchItem)>0:
            return searchItem[0][2]
    return None


if GetRicName('MSFT.O') is not None:
    print("MSFT.O is \""+ GetRicName("MSFT.O")+"\"")
else:
    print("Unable to find name for MSFT.O")

ricList="MSFT.O"
esgScoreFullEndpoint="https://api.refinitiv.com/data/environmental-social-governance/v2/views/scores-full?universe="
resp=get(url=esgScoreFullEndpoint+ricList,headers={"Authorization": "Bearer " + accessToken})
if resp.status_code!=200:
    print("Status Code:",resp.status_code," Text:",dumps(loads(resp.text),indent=4))
    exit()

esg_object=loads(resp.text)


import pandas as pd
import numpy as np
headers=esg_object['headers']

#Get column headers/titles using lambda
titles=map(lambda header:header['title'], headers)
dataArray=np.array(esg_object['data'])
df=pd.DataFrame(data=dataArray,columns=titles)
print(df)

dataPlot=pd.DataFrame(df,columns=['Instrument','Period End Date','ESG Score','ESG Combined Score','Innovation Score'])
dataPlot['Period End Date']= dataPlot['Period End Date'].str.split('-').str[0]
#By default sorting pandas data frame using sort_values() or sort_index() creates a new data frame. 
#If you don’t want create a new data frame after sorting and just want to do the sort in place, 
#you can use the argument “inplace = True”.
dataPlot.sort_values('Period End Date',ascending=True,inplace=True)
dataPlot

dataPlot.plot(x='Period End Date',y=['ESG Score','ESG Combined Score','Innovation Score'],figsize=(14,7))
dataPlot.plot(x='Period End Date',y=['ESG Score','ESG Combined Score','Innovation Score'],kind='bar',figsize=(14,7))

ricList="IBM,AMZN.O,MSFT.O,GOOGL.O,FB.O,APPL.O"
esgฺBasicEndpoint="https://api.refinitiv.com/data/environmental-social-governance/v2/views/basic?universe="
resp=get(url=esgฺBasicEndpoint+ricList,headers={"Authorization": "Bearer " + accessToken})
if resp.status_code!=200:
    print("Status Code:",resp.status_code," Text:",dumps(loads(resp.text),indent=4))
    exit()

esg_BasicObject=loads(resp.text)

import pandas as pd
import numpy as np
headers=esg_BasicObject['headers']

#Get column headers/titles using lambda
titles=map(lambda header:header['title'], headers)

basicDataArray=np.array(esg_BasicObject['data'])
basicDf=pd.DataFrame(data=basicDataArray,columns=titles)

if basicDf.empty is False:
    print(basicDf)


co2= [val for sublist in np.array(basicDf.iloc[:,5:6]) for val in sublist]
woman=[val for sublist in np.array(basicDf.iloc[:,6:7]) for val in sublist] 
instrument=[val for sublist in np.array(basicDf.iloc[:,0:1]) for val in sublist]  
print(co2)
print(woman)
print(instrument)
instrumentorg=np.array([])

for val in instrument:
    if GetRicName(val) is None:
        instrumentorg=np.append(instrumentorg,val)
    else:
        instrumentorg=np.append(instrumentorg,GetRicName(val))

print(instrumentorg)

#Uncomment below to plotgraph on supported environment.    
#df1 = pd.DataFrame({"Woman Managers":woman}, index=instrumentorg)
#df1.plot.barh(y='Woman Managers')

#df2 = pd.DataFrame({"CO2 Emission Total":co2}, index=instrumentorg)
#df2.plot.barh(y='CO2 Emission Total',color=(0.5, 0.25, 0.15, 1))
