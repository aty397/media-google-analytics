# coding: UTF-8
"""A simple example of how to access the Google Analytics API."""

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import datetime

def get_service(api_name, api_version, scopes, key_file_location):
    """Get a service that communicates to a Google API.

    Args:
        api_name: The name of the api to connect to.
        api_version: The api version to connect to.
        scopes: A list auth scopes to authorize for the application.
        key_file_location: The path to a valid service account JSON key file.

    Returns:
        A service that is connected to the specified API.
    """

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
            key_file_location, scopes=scopes)

    # Build the service object.
    service = build(api_name, api_version, credentials=credentials)

    return service

def get_first_profile_id(service):
    # Use the Analytics service object to get the first profile id.

    # Get a list of all Google Analytics accounts for this user
    accounts = service.management().accounts().list().execute()

    if accounts.get('items'):
        # Get the first Google Analytics account.
        account = accounts.get('items')[0].get('id')

        # Get a list of all the properties for the first account.
        properties = service.management().webproperties().list(
                accountId=account).execute()

        if properties.get('items'):
            # Get the first property id.
            property = properties.get('items')[0].get('id')

            # Get a list of all views (profiles) for the first property.
            profiles = service.management().profiles().list(
                    accountId=account,
                    webPropertyId=property).execute()

            if profiles.get('items'):
                # return the first view (profile) id.
                return profiles.get('items')[0].get('id')

    return None

def get_results(service, profile_id):
    # Use the Analytics Service Object to query the Core Reporting API
    # for the number of sessions within the past seven days.
    return service.data().ga().get(
            ids='ga:' + profile_id,
            start_date='30daysAgo',
            end_date='today',
            metrics='ga:pageviews',
            dimensions='ga:pagePath',
            filters='ga:pagePath==/'
            ).execute()

def get_results_pv(service, profile_id,post_path,pubdate,enddate):
    # Use the Analytics Service Object to query the Core Reporting API
    # 確認
    # print '<--------------------------------------------------------'
    # print 'start_date=',pubdate
    # print 'end_date=',enddate
    # print 'path=',post_path
    input_filter = 'ga:pagePath=='+post_path
    result = service.data().ga().get(
            ids='ga:' + profile_id,
            start_date=pubdate,
            end_date=enddate,
            metrics='ga:pageviews',
            dimensions='ga:pagePath',
            filters=input_filter
            ).execute()
    return result.get('rows')[0][1]

def get_results_pv_hour(pubdate):
    #時間ごとのPVを取得する
    #pubdate=日付型：%Y-%m-%d-%H
    return 0

def print_results(results):
    # Print data nicely for the user.
    # if results.get('rows') is None:
    #     print "None"
    # print "type=",type(results)
    # print "len=",len(results)
    # print ".get=",results.get('rows')
    # return
    if results:
        # print 'View (Profile):', results.get('profileInfo').get('profileName')
        # print 'len=',results.get('rows')
        #postが存在したかチェック
        if results.get('rows') is None:
            print 'Post does not exist.'
        else:        
            # print 'page', results.get('rows')[0][0]
            print 'pv:', results.get('rows')[0][1]
    else:
        print 'No results found'

def main():
    # Define the auth scopes to request.
    scope = 'https://www.googleapis.com/auth/analytics.readonly'
    key_file_location = '/Users/daichi/py/client_secrets.json'

    # Authenticate and construct service.
    service = get_service(
            api_name='analytics',
            api_version='v3',
            scopes=[scope],
            key_file_location=key_file_location)

    profile_id = get_first_profile_id(service)

    #出力用ファイル
    fout = open('output/bijin.csv',mode='w')
    #記事パス,1日PV、1週PV、1月PV、公開日、記事タイトル
    fout.write('記事パス'+',')
    fout.write('PV(1日)'+',')
    fout.write('PV(７日)'+',')
    fout.write('PV(30日)'+',')
    fout.write('公開日'+',')
    fout.write('記事タイトル'+',')
    fout.write('\n')

    #CSVからpostidと公開日時を取得する
    f = open('input/bijin.txt')
    line = f.readline()

    count = 1
    while line:
        print '<--------------------------------------------------------',count
        count+=1
        input = line.split()
        #input format
        # [0]=パス
        # [1]=公開日
        # [2]=記事タイトル
       
        #計測記事のpath
        path = input[0]

        #計測記事公開日時を文字列で取得
        pubdate = input[1]
        # publish_hour = pubdate[11:12]
        # print 'hour=',publish_hour
        
        #日付型に変換
        pubdate = datetime.datetime.strptime(pubdate, "%Y-%m-%d-%H")

        #公開２時間
        pv_2hour = get_results_pv_hour(pubdate)

        #1日後
        #未来日付指定をしていない確認
        pubdate_d = pubdate + datetime.timedelta(days=1) 
        pubdate_d = pubdate_d.strftime("%Y-%m-%d") #文字列に戻す
        # print 'pubdate_d = ',pubdate_d

        #1週間後
        #未来日付指定をしていない確認
        pubdate_w = pubdate + datetime.timedelta(days=7) 
        pubdate_w = pubdate_w.strftime("%Y-%m-%d") #文字列に戻す
        # print 'pubdate_w = ',pubdate_w

        #１月後
        #未来日付指定をしていない確認
        pubdate_m = pubdate + datetime.timedelta(days=30) 
        pubdate_m = pubdate_m.strftime("%Y-%m-%d") #文字列に戻す
        # print 'pubdate_m = ',pubdate_m

        pubdate = pubdate.strftime("%Y-%m-%d") #pubdateを文字列に戻す  
        
        #PV取得
        pv_day = get_results_pv(service, profile_id,path,pubdate,pubdate_d)#公開後1日のPV
        pv_week = get_results_pv(service, profile_id,path,pubdate,pubdate_w)#公開後1週間のPV
        pv_month = get_results_pv(service, profile_id,path,pubdate,pubdate_m)#公開後1月のPV
        
        post_title = input[2]
        #想定出力
        #記事パス,1日PV、1週PV、1月PV、公開日、記事タイトル 
        fout.write(path+',')
        fout.write(pv_day+',')
        fout.write(pv_week+',')
        fout.write(pv_month+',')
        fout.write(pubdate+',')
        fout.write(input[2])
        fout.write('\n')

        break
        line = f.readline()#次の行を読み込む
    #サイクルここまで <-
    f.close()
    fout.close()

if __name__ == '__main__':
    main()