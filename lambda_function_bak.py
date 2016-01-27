from __future__ import print_function
import boto3
import json
from HTMLParser import HTMLParser
import requests
import threading
from boto3.session import Session
session = Session(region_name='eu-west-1')


idlist=[]
def crawl():

    class MyHTMLParser(HTMLParser):
        def handle_starttag(self, tag, attrs):
            for attr in attrs:
                if "data-ds-appid" in attr:
                    game_id=attr[1]
                    if game_id not in idlist:
                        idlist.append(game_id)
                        return(idlist)
    


    #Find the early access game count
    url='http://store.steampowered.com/search/tabpaginated/render/?query=&start=10&count=1&genre=70&tab=NewReleases&cc=TR&l=english'
    r=requests.get(url)
    data = json.loads(r.text)
    new_html=data['results_html']
    total_count=data['total_count']
    pagination=total_count/10+2
    #print(total_count,pagination)
    

    #Create the list

    
    applist={}
    i=0
    while(i<pagination*10):
        url='http://store.steampowered.com/search/tabpaginated/render/?query=&start='+str(i)+'&count=10+&genre=70&tab=NewReleases&cc=TR&l=english'
        r_new=requests.get(url)
        data = json.loads(r_new.text)
        parser = MyHTMLParser()
        parser.feed(data['results_html'])
        i=i+10
        #print(idlist)
    

    return(idlist)



def reviews(sess,table):

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
    namestemp=[]
    print(len(idlist))
    while len(idlist)>0:
        new_appid=idlist.pop()
        url="http://store.steampowered.com/app/"+new_appid
        cookie = dict(birthtime='-189395999')
        r_new=requests.get(url,cookies=cookie)
        data=r_new.text
        parser = reviews()
        parser.feed(data)
        if len(namestemp)>0:
            positive=int(namestemp[0])
            negative=int(namestemp[1])
        else:
            positive=0
            negative=0
        print(table,url)
        try:
            print(sess,table,new_appid,positive,negative)
            table.put_item(
               Item={
                    'AppId': new_appid,
                    'Positive': positive,
                    'Negative': negative,
                     }
            )
        except:
            print("break")


def lambda_handler(event, context):
    NUM_THREADS = 2
    crawl()
    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table('GameReviews')
    try:
        while NUM_THREADS>0:
            NUM_THREADS=NUM_THREADS-1
            t1=threading.Thread(target=reviews, args=(dynamodb,table))
            t1.start()

    except:
        print("Error: unable to start thread")

