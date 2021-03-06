from __future__ import print_function
from HTMLParser import HTMLParser
import requests
from boto3 import Session
from boto3.dynamodb.conditions import Key, Attr
import uuid,time


session = Session(region_name='eu-west-1')
dynamodb = session.resource('dynamodb')
table = dynamodb.Table('GameMetrics')

def lambda_handler(event, context):

    class reviews(HTMLParser):

        def __init__(self):
            HTMLParser.__init__(self)
            self.inLink = False
            self.dataArray = []
            self.countLanguages = 0
            self.lasttag = None
            self.lastname = None
            self.lastvalue = None

        def handle_starttag(self, tag, attrs):
            self.inLink = False
            if tag == 'span':
                for name, value in attrs:
                    if name == 'class' and value =='user_reviews_count':
                        self.countLanguages += 1
                        self.inLink = True
                        self.lasttag = tag

        def handle_endtag(self, tag):
            if tag == "span":
                self.inlink = False

        def handle_data(self, data):
            if self.lasttag == 'span' and self.inLink and data.strip():
                values=data.replace('(', '').replace(')', '').replace(',','')
                if values:
                    namestemp.append(int(values))
    for appid in event["key"]:
        appid=appid.split(",")[0]
        namestemp=[]
        url="http://store.steampowered.com/app/"+appid
        cookie = dict(birthtime='-189395999')
        r_new=requests.get(url,cookies=cookie)
        data=r_new.text
        parser = reviews()
        parser.feed(data)
        parser.close()

        #News count
        url='http://api.steampowered.com' \
            '/ISteamNews/GetNewsForApp/v2' \
            '?appid='+appid+ \
            '&maxlength=1' \
            '&count=1000'

        r_new=requests.get(url)
        news=len(r_new.json()['appnews']['newsitems'])

        #Players Count
        url='http://api.steampowered.com' \
        '/ISteamUserStats/GetNumberOfCurrentPlayers/v1' \
        '?appid='+appid

        r_new=requests.get(url)
        players=r_new.json()['response']['player_count']
        if len(namestemp)>0:
                positive=int(namestemp[0])
                negative=int(namestemp[1])
        else:
            positive=0
            negative=0


        try:
                table.put_item(
                   Item={
                        'Id' : str(uuid.uuid4()),
                        'AppId': appid,
                        'Positive': positive,
                        'Negative': negative,
                        'News':news,
                        'Players':players,
                        'Date':int(time.time()*1000)
                         }
                )
        except Exception as e:
            print(e)

if __name__ == "__main__":
    try:
        lambda_handler("event","asd")
    except Exception as err:
        print(err)
