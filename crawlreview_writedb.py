from __future__ import print_function
from HTMLParser import HTMLParser
import requests
from boto3 import Session

session = Session(region_name='eu-west-1')
dynamodb = session.resource('dynamodb')
table = dynamodb.Table('GameReviews')

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
        namestemp=[]
        url="http://store.steampowered.com/app/"+appid
        cookie = dict(birthtime='-189395999')
        r_new=requests.get(url,cookies=cookie)
        data=r_new.text
        parser = reviews()
        parser.feed(data)
        parser.close()
        if len(namestemp)>0:
                positive=int(namestemp[0])
                negative=int(namestemp[1])
        else:
            positive=0
            negative=0

        #Query old data
        results = table.query(
            KeyConditionExpression=Key('AppId').eq(appid)
        )
        newnegative=0
        newpositive=0
        for i in results['Items']:
            oldpositive=i['Positive']
            oldnegative=i['Negative']
            if positive!=oldpositive:
                print(positive,oldpositive)
                newpositive=positive
                print("changed positive,old was:",oldpositive,"new is:",newpositive)
            else:
                newpositive=positive

            if negative!=oldnegative:
                print(negative,oldnegative)
                newnegative=negative
                print("changed negative,old was:",oldnegative,"new is:",newnegative)

            else:
                newnegative=negative

        try:
                table.put_item(
                   Item={
                        'AppId': appid,
                        'Positive': newpositive,
                        'Negative': newnegative,
                         }
                )
                print("Updated :",appid,newpositive,newnegative)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    try:
        lambda_handler("event","asd")
    except Exception as err:
        print(err)
