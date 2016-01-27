from __future__ import print_function
import json
from HTMLParser import HTMLParser
import requests
from boto3 import Session

s=Session(region_name='eu-west-1')
awslambda = s.client('lambda')
idlist=[]

def crawl():
    print("crawl started")
    class MyHTMLParser(HTMLParser):
        def handle_starttag(self, tag, attrs):
            for attr in attrs:
                if "data-ds-appid" in attr:
                    game_id=attr[1]
                    if game_id not in idlist:
                        idlist.append(game_id)
                        return(idlist)

    #Find the early access game pagination count
    url='http://store.steampowered.com/search/tabpaginated/render/?query=&start=10&count=1&genre=70&tab=NewReleases&cc=TR&l=english'
    r=requests.get(url)
    data = json.loads(r.text)
    total_count=data['total_count']
    pagination=total_count/10+1

    #Create the list
    i=0
    while(i<pagination*10):
        url='http://store.steampowered.com/search/tabpaginated/render/?query=&start='+str(i)+'&count=10+&genre=70&tab=NewReleases&cc=TR&l=english'
        r_new=requests.get(url)
        data = json.loads(r_new.text)
        parser = MyHTMLParser()
        parser.feed(data['results_html'])
        i=i+10
    #print(len(idlist))
    list_dic= {}
    dicid=0
    while len(idlist)>0:
        templist=[]
        for y in range(0,100):
            if len(idlist)>0:
                templist.append(idlist.pop())
        list_dic[dicid] = templist
        dicid+=1
    #print(list_dic)


    for key,value in list_dic.items():
        FunctionName='Crawler'+str(key)
        response = awslambda.list_functions(
        MaxItems=1230
        )
        current_funcs=[]
        for func in response['Functions']:
            current_funcs.append(func['FunctionName'])
        if FunctionName not in current_funcs:
            response = awslambda.create_function(
                FunctionName=FunctionName,
                Runtime='python2.7',
                Role='arn:aws:iam::130575395405:role/lambda_basic_execution',
                Handler='lambda_function.lambda_handler',
                Code={
                    'S3Bucket': 'early-lambda-codes',
                    'S3Key': 'reviewcrawler.zip'
                },
                Description='Review Crawler',
                Timeout=120,
                MemorySize=128,
                Publish=True
            )
        print("Invoking function ",FunctionName)
        response = awslambda.invoke(
        FunctionName=FunctionName,
        InvocationType='RequestResponse',
        Payload= '{"key":'+json.dumps(value)+'}')
        print({"key":json.dumps(value)})


    print("Lambda functions created and invoked")



def lambda_handler(event, context):
    crawl()

if __name__ == "__main__":
    try:
        lambda_handler("event","asd")
    except Exception as err:
        print(err)
