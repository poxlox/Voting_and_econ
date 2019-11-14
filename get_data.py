import requests
import pandas as pd

def get_fips():
    resp=requests.get('https://www.nrcs.usda.gov/wps/portal/nrcs/detail/?cid=nrcs143_013697')
    df=pd.read_html(resp.text)[0]
    df=df.iloc[0:-1]
    return df

def BEA(method, **kwargs):
    '''
    methods: getdata, getdatasetlist, getparameterlist,
        getparametervalues, getparametervaluesfiltered
    params: datasetname, parametername, targetparameter, 
        tablename, linecode, year, geoflips
    '''
    target = 'https://apps.bea.gov/api/data'
    payload = {'UserID': os.environ['BEA_API_KEY'], 'method':method}
    payload.update(kwargs)
    return requests.get(target, params=payload)

def clean_BEA(df,labelname):
    df=df[df['NoteRef'] != '(NA)']
    df=df[df['NoteRef'] != '*']
    df=df.drop(labels=['Code','CL_UNIT','NoteRef','UNIT_MULT',
                       'TimePeriod','GeoName'],axis=1)
    if ',' in df['DataValue'].iloc[0]:
        df['DataValue']=df['DataValue'].str.replace(',', '').astype(float)
    df=df.astype({'GeoFips':'float64','DataValue':'float64'})
    df=df.rename(columns={'DataValue':labelname})
    return df

if __name__=='__main__':
    print('please have folder named "files" in directory')
    print('please have downloaded "countypres_2000-2016.csv" and stored this in files directory, see my /files folder')
    print(f'please have downloaded "files/laucnty{yr[2:]}.xlsx" and stored this in files directory, see my /files folder')

    print('please have a BEA API Key stored in your os environment as "BEA_API_KEY"')
    d=0
    while d=0:
        yr = input('input 4 digit election year (2000 or later) here: ')
        print(f'getting data for {}...')
        vote=pd.read_csv('files/countypres_2000-2016.csv')
        vote.rename(columns = {'FIPS':'GeoFips'}, inplace = True)
        vote=vote[vote['year']==int(yr)]
        vote=vote.dropna(axis=0,how='any')
        vote=vote.drop(labels=['state_po','office','version'],axis=1)
        resp=requests.get('https://www.nrcs.usda.gov/wps/portal/nrcs/detail/?cid=nrcs143_013697')
        #GeoFips data
        df=pd.read_html(resp.text)[0]
        df.drop(3232,inplace=True)
        df.rename(columns={'FIPS':'GeoFips'}, inplace=True)
        df=df.astype({'GeoFips':'float64'})
        df=df.drop(labels=['Name','State'],axis=1)
        merged=pd.merge(vote,df,how='inner',on='GeoFips')
        if yr=='2000':
            yr='2001'
        resp=BEA('getdata', datasetname='regional',geofips='County',tablename='CAEMP25N',year=yr,linecode=10)
        #num jobs
        df=pd.DataFrame.from_records(resp.json()['BEAAPI']['Results']['Data'])
        df=clean_BEA(df,'num_jobs')
        merged=pd.merge(merged,df,how='inner',on='GeoFips')
        yr='2000'
        resp=BEA('getdata', datasetname='regional',geofips='County',tablename='CAINC45',year=yr,linecode=370)
        #farm income thousands
        df=pd.DataFrame.from_dict(resp.json()['BEAAPI']['Results']['Data'])
        df=clean_BEA(df,'Farm_income_thousands')
        merged=pd.merge(merged,df,how='inner',on='GeoFips')
        resp=BEA('getdata', datasetname='regional',geofips='County',tablename='CAINC30',year=yr,linecode=110)
        #income/capita
        df=pd.DataFrame.from_dict(resp.json()['BEAAPI']['Results']['Data'])
        df=clean_BEA(df,'Income/Capita')
        merged=pd.merge(merged,df,how='inner',on='GeoFips')
        resp=BEA('getdata', datasetname='regional',geofips='County',tablename='CAINC30',year=yr,linecode=100)
        #population
        df=pd.DataFrame.from_dict(resp.json()['BEAAPI']['Results']['Data'])
        df=clean_BEA(df,'population')
        merged=pd.merge(merged,df,how='inner',on='GeoFips')
        resp=BEA('getdata', datasetname='regional',geofips='County',tablename='CAINC30',year=yr,linecode=290)
        #average salary
        df=pd.DataFrame.from_dict(resp.json()['BEAAPI']['Results']['Data'])
        df=clean_BEA(df,'avg_sal')
        merged=pd.merge(merged,df,how='inner',on='GeoFips')
        df=pd.read_excel(f'files/laucnty{yr[2:]}.xlsx', converters={'state_fips_Code':str, 'county_fips_code':str})
        #unemployment file
        df['GeoFips']=df['state_fips_Code']+df['county_fips_code']
        df=df.astype({'GeoFips':'float64'})
        df=df.drop(labels=['LAUS_Code','state_fips_Code','county_fips_code','Unnamed: 5', 'Year','County Name/State Abbreviation'], axis=1)
        merged=pd.merge(merged,df,how='inner',on='GeoFips')
        print(f'storing as /files/table{yr}.pkl...')
        merged.to_pickle(f'./files/table{yr}.pkl')
        qq=input('done? y/n: ')
        if qq=='y':
            d=1
        