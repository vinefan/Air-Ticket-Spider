# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 11:14:12 2019

@author: 1
"""
import requests
import datetime
import random
import pymysql

url='https://flights.ctrip.com/itinerary/api/12808/products'
##已改
data={"flightWay":"Oneway","classType":"ALL","hasChild":"false","hasBaby":"false","searchIndex":1,
      "airportParams":[{"dcity":"CTU","acity":"SHA","dcityname":"成都","acityname":"上海","date":"2019-07-22",
      "dcityid":28,"acityid":2,"dport":"CTU","dportname":"双流国际机场","aport":"PVG","aportname":"浦东国际机场"}]}

UserAgent = ["Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
             "Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0) Gecko/16.0 Firefox/16.0",\
             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/534.55.3 (KHTML, like Gecko) Version/5.1.3 Safari/534.53.10", 
             "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)", 
             "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
             "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1500.55 Safari/537.36",
             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17",
             "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
             "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
             "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
             "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7"
          ]
#已改
headers={#Host,Content-type,User-Agent,Referer
        'Host':'flights.ctrip.com',        
        'Content-Type':'application/json'
        }
#yigai      
airport=[{"port":"CTU","portname":"双流国际机场","city":"ctu","cityname":"成都","cityid":28},
         {"port":"SHA","portname":"虹桥国际机场","city":"sha","cityname":"上海","cityid":2},
         {"port":"PVG","portname":"浦东国际机场","city":"sha","cityname":"上海","cityid":2},
         {"port":"PEK","portname":"首都国际机场","city":"bjs","cityname":"北京","cityid":1},
         {"port":"NAY","portname":"南苑机场","city":"bjs","cityname":"北京","cityid":1}]

source="携程"

def set_date(i):
    today=datetime.datetime.today()
    offset=datetime.timedelta(days=i)
    date=(today+offset).strftime('%Y-%m-%d')
    return date
#yigai      
def get_headers(date,dairport,aairport):
    Referer="https://flights.ctrip.com/itinerary/oneway/"+dairport.get('city')+","+dairport.get('port')+"-"+aairport.get('city')+","+aairport.get('port')+"?date="+date
    headers['Referer']=Referer
    headers['User-Agent']=random.choice(UserAgent)
#yigai    
def get_data(date,depCity,arrCity):
    data['airportParams'][0]['date']=date
    data['airportParams'][0]['dcity']=depCity.get('city')
    data['airportParams'][0]['dcityname']=depCity.get('cityname')
    data['airportParams'][0]['dcityid']=depCity.get('cityid')
    data['airportParams'][0]['dport']=depCity.get('port')
    data['airportParams'][0]['dportname']=depCity.get('portname')
    data['airportParams'][0]['acity']=arrCity.get('city')
    data['airportParams'][0]['acityname']=arrCity.get('cityname')
    data['airportParams'][0]['acityid']=arrCity.get('cityid')
    data['airportParams'][0]['aport']=arrCity.get('port')
    data['airportParams'][0]['aportname']=arrCity.get('portname')
  
def get_proxy():
    return requests.get(" http://118.24.52.95:5010/get/").text
  
def sort_flights(depCity,arrCity,flightList):
    
    response=requests.post(url,headers=headers,json=data, proxies={"http": "http://{}".format(proxy)})
    response.raise_for_status()
    routeList=response.json().get('data').get('routeList')
    
    if routeList:
        for i in range(len(routeList)):        
            flight={}
            route=routeList[i]
            #isThrough
            if route.get('routeType')=="Flight":                    
                legs=route.get('legs')
                if legs:
                    for j in range(len(legs)):
                        leg = legs[j]
                        if leg.get('flight'): 
                            dport=leg.get('flight').get('departureAirportInfo').get('airportTlc')
                            aport=leg.get('flight').get('arrivalAirportInfo').get('airportTlc')
                            if dport==depCity.get('port') and aport==arrCity.get('port'):
                                #source,flightId,airlineName,flightNumber,depTime,arrTime,isThrough
                                get_flightInfo(leg.get('flight'),flight)
                                if leg.get('cabins'):
                                    #lowestPrice,childPrice,babyPrice,cabin
                                    get_price(leg.get('cabins'),flight)
                                    flightList.append(flight)
            
    else:
        print("empty page")
        return;
#gai??weiwan
def get_flightInfo(pageData,flightInfo):
    if pageData:
        flightNumber=pageData.get('flightNumber')
        dDate=pageData.get('departureDate')
        flightInfo['source']=source
        flightInfo['flightId']=get_flightId(flightNumber,dDate)     
        flightInfo['airlineName']=pageData.get('airlineName')
        flightInfo['flightNumber']=flightNumber
        flightInfo['depTime']=dDate
        flightInfo['arrTime']=pageData.get('arrivalDate')
        #gai
        if pageData.get('stopTimes')==0:
            flightInfo['isThrough']=1
        else:
            flightInfo['isThrough']=0
    else:
        return;
    
def get_price(pageData,flightInfo):
    if pageData:
        lowestPrice=100000
        for i in range(len(pageData)):
            cabin=pageData[i]
            if cabin:
                tmp=cabin.get('price').get('price')
                if tmp<lowestPrice:
                    lowestPrice=tmp
                    flightInfo['lowestPrice']=tmp
                    if cabin.get('childPolicy'):
                        flightInfo['childPrice']=cabin.get('childPolicy').get('price')
                    else:
                        flightInfo['childPrice']=None
                    if cabin.get('babyPolicy'):
                        flightInfo['babyPirce']=cabin.get('babyPolicy').get('price')
                    else:
                        flightInfo['babyPirce']=None
                    flightInfo['cabin']=cabin.get('cabinClass')
            else:
                return;
    else:
        return;

def get_flightId(flightNumber,depDatetime):
    return "XC"+flightNumber+datetime.datetime.strptime(depDatetime,"%Y-%m-%d %H:%M:%S").strftime("%m%d%H%M")


def sendmeg(flights, depCity, arrCity):

    # mysql里的表名都带了单引号 ，可能存在bug
    table = '{}_to_{}'.format(depCity,arrCity)
    table = table.lower()
    
    # 创建sql语句
    # select = 'SELECT * FROM {} WHERE flight_id = %s '.format(table)
    select = 'SELECT * FROM {} WHERE flight_id = "{}"'
    insert = 'INSERT INTO {}(flight_id,  \
                             source,     \
                             airline_name, \
                             flight_number, \
                             lowest_price, \
                             child_price,  \
                             baby_price,   \
                             dep_time,     \
                             arr_time,     \
                             cabin,        \
                             is_through)  \
              VALUES(%s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s)'.format(table)
    
    update = 'UPDATE {}           \
              SET lowest_price = %s ,    \
                  child_ price = %s ,    \
                  baby_price = %s ,      \
                  cabin = %s ,           \
                  is_through = %s ,      \
              WHERE id=%s'.format(table)

    # 连接数据库
    database = pymysql.connect(host='localhost', user='root', password='123456', port=3306, db='creeper')
    cursor = database.cursor()

    # 遍历数据，如果数据存在，则update ，否则insert
    for flight in flights:
        try:
            print(flight['flightId'])
            cursor.execute(select.format(table,flight['flightId']))
            subsistent = cursor.rowcount
            print(subsistent)
            #存在，更新该数据
            if subsistent:
                flightpast = cursor.fetchone()
                try:
                    cursor.execute(update,(flight['lowestPrice'], \
                                           flight['childPrice'],  \
                                           flight['babyPrice'],   \
                                           flight['cabin'],       \
                                           flight['isThrough'],  \
                                           flightpast['id']) )
                    database.commit()
                except Exception as e:
                    print(e)
                    database.rollback()
                
            # 不存在，则插入一条数据
            else:
                try:
                    cursor.execute(insert,(flight['flightId'], \
                                           flight['source'],    \
                                           flight['airlineName'], \
                                           flight['flightNumber'], \
                                           flight['lowestPrice'],  \
                                           flight['childPrice'],  \
                                           flight['babyPrice'],  \
                                           flight['depTime'],  \
                                           flight['arrTime'],  \
                                           flight['cabin'],  \
                                           flight['isThrough'],  ))
                    database.commit()
                except:
                    database.rollback()
                    print(e)
        except Exception as e:
            print(e)
    
    database.close()
    print(table+": 已全部存入")



def main():
    
    # 航线循环
    for i in range(len(airport)):
        depCity=airport[i]
        for j in range(len(airport)):
            arrCity=airport[j]
            if depCity.get('cityname')!=arrCity.get('cityname'): 
                
                flightList=[]
                # 循环日期
                for k in range(1):
                    date=set_date(k)
                    get_headers(date,depCity,arrCity)
                    get_data(date,depCity,arrCity)  
                    print(date+" "+depCity.get('port')+"-"+arrCity.get('port'))
                    sort_flights(depCity,arrCity,flightList)
                # 存入数据库    
                depPort = depCity['port']
                arrPort = arrCity['port']
                sendmeg(flightList, depPort, arrPort)
                    
                
    
                    
main()   
    

    
    
    
    
