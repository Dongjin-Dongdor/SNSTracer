#-- coding: utf-8 --
__author__ = 'gimdongjin'



import pyoauth2 as oauth
import urllib2
import string
import random
from bottle import request, run, route, jinja2_template, post, get, hook, redirect,static_file
import bottle

from beaker.middleware import  SessionMiddleware
import urlparse
import tweepy

import requests
from pymongo import MongoClient
from json import dumps
import time
from time import strftime
import sys
import datetime
import twitter

reload(sys)
sys.setdefaultencoding('utf-8')

session_opts = {
    'session.type': 'memory',
    'session.cookie_expires': 300000,
    'session.auto': True,
    'session.key':'palette_uid'
}


app = SessionMiddleware(bottle.app(), session_opts)

##########################twitter##################################

twitter_consumer_key="F6Dr6dubbLsXupN3hWEub4Flz"
twitter_consumer_secret="8YyrnG0MbBl4x0r37AVuV9oUu4jpAwLfzChq3jgjF1CjGC0ZjJ"
twitter_request_token_url = 'https://api.twitter.com/oauth/request_token'
twitter_access_token_url = 'https://api.twitter.com/oauth/access_token'
twitter_authorize_url = 'https://api.twitter.com/oauth/authorize'
consumer_twitter = oauth.Consumer(twitter_consumer_key, twitter_consumer_secret)
client_twitter = oauth.Client(consumer_twitter)



###########################facebook##################################

facebook_access_token_url = 'https://graph.facebook.com/oauth/access_token'
facebook_request_token_url = 'https://www.facebook.com/dialog/oauth'
facebook_check_auth = 'https://graph.facebook.com/v2.2/me?access_token='
facebook_consumer_key='971864392875082'
facebook_consumer_secret ='8bf0c21f5620c8fdcfa293bbb10abd88'
facebook_graph_url = 'https://graph.facebook.com/me?access_token='
consumer_facebook = oauth.Consumer(facebook_consumer_key,facebook_consumer_secret)
client_facebook = oauth.Client(consumer_facebook)



##############################kakao####################################

kakao_request_token_url = 'https://kauth.kakao.com/oauth/authorize?'
kakao_access_token_url = 'https://kauth.kakao.com/oauth/token?'
kakao_consumer_key= 'f8a99718997aac1411eada0fb20884a0'
kakao_upload_url = 'https://kapi.kakao.com/v1/api/story/post/note?access_token='


########################################################################
########################################################################




@hook('before_request')
def setup_request():
    request.session = request.environ['beaker.session']



c = string.letters + string.digits
parent = "root"


#palette를 통해 들어온 노드들의 parent 가 누군이지 확인하는 함수
@route('/start/<url_address:path>')
def index(url_address):
    created_at = datetime.datetime.now()
    str_created_at = str(created_at)
    global url_v1
    global parent
    global session_id
    global referer
    global flag
    url_v1 = ''.join(random.sample(c,7))
    v1 = url_v1
    flag = 1
    p_referer = request.environ.get('HTTP_REFERER')

    if 'kakao' in p_referer :
        referer = 'kakao'
    elif 'facebook' in p_referer :
        referer = 'facebook'
    elif 'twitter' in p_referer :
        referer = 'twitter'

    parent = url_address
    request.session = request.environ['beaker.session']
    session_id = request.get_cookie('palette_uid')
    if session_id is None:
        request.session.save()
        session_id = request.session.id
    s = bottle.request.environ.get('beaker.session')
    s['test'] = 'this string came from the session'
    s.save()
    access_collection.insert({'session_id':session_id,'access_token_twitter':'','access_token_secret_twitter':'','access_token_facebook':'',
                              'access_token_kakao':'','screen_name_twitter':'','screen_name_facebook':'','screen_name_kakao':'','created_at':created_at})


    if t_collection.find({'beaker_session':session_id}).count() >0:
        twitter_list = t_collection.find_one({'beaker_session':session_id})
        twitter_token = twitter_list['access_token']
        twitter_token_secret = twitter_list['access_token_secret']
    else :
        twitter_token = ''
        twitter_token_secret = ''

    if f_collection.find({'beaker_session':session_id}).count()>0:
        facebook_list = f_collection.find_one({'beaker_session':session_id})
        facebook_token = facebook_list['access_token']
    else :
        facebook_token = ''

    if k_collection.find({'beaker_session':session_id}).count()>0:
        kakao_list = k_collection.find_one({'beaker_session':session_id})
        kakao_token = kakao_list['access_token']
    else:
        kakao_token = ''
    if favorite_collection.find({'beaker_session':session_id}).count()>0:
        screen_name = favorite_collection.find_one({'beaker_session':session_id})
        name = screen_name['favorite']
    else :
        name = ''
    if share_collection.find({"my_randomkey":parent}).count()>0:
        i = share_collection.find_one({"my_randomkey":parent})
        visitor_count = i["count_visitor"] + 1
        share_collection.update_one({"my_randomkey":parent},{'$set':{"count_visitor":visitor_count}})
    #parent_children_collection.insert({'parent':parent,'children':v1,'sns':referer,'session_id':session_id,'created_at':created_at})
    share_collection.insert({"my_randomkey":v1,"sns":"","session_id":session_id,"created_at":created_at,"count_visitor":0,'str_created_at':str_created_at})
    print parent,'!!!!!!!!!!!!this!!!!!'
    i = parent_children_collection.find_one({"children":parent})
    print i,'@@@@@@@@@@@@@@'
    print i['url_random'],'~~!!~~~~~~~'
    url_parent_collection.insert({"session_id":session_id,"parent_random":v1,
                                  "created_at":created_at,
                                  "grand_parent_url":i["url_random"],
                                  "sns":referer
                                  })
    return jinja2_template('twitter.html',session_id=session_id,screen_name=name,access_token_regular_facebook=facebook_token,
                           access_token_regular_twitter=twitter_token,
                           access_token_secret_twitter= twitter_token_secret,
                           random_character=v1,
                           access_token_regular_kakao=kakao_token)

#####################################go to sns oaut#############################


#처음 실행시 시작되는 함수
@route("/")
def start():
    global flag
    global session_id
    global sns_v1
    created_at = datetime.datetime.now()
    str_created_at = strftime("%y-%m-%d %H:%M:%S")
    #flag를 통해 url로 들어온 노드인지 palette로 들어온 노드인지 확인한다.
    flag = 2
    #랜덤 숫자(노드 고유번호)를 발급한다.
    sns_v1 = ''.join(random.sample(c,7))
    v1 = sns_v1
    #sns
    p_referer = request.forms.get('sns')
    #refer를 sns에 맞게 바꿔준다.
    try:
        if 'kakao' in p_referer :
            referer = 'kakao'
        elif 'facebook' in p_referer :
            referer = 'facebook'
        elif 'twitter' in p_referer :
            referer = 'twitter'
    except:
        referer = ''
    #위에 session_opts설정에 key값인 palette_uid를 통해 session_id를 받는다.
    session_id = request.get_cookie('palette_uid')

    if session_id is None:
        request.session.save()
        session_id = request.session.id
    share_collection.insert({"my_randomkey":v1,"sns":"","session_id":session_id,"created_at":created_at,"count_visitor":0,'str_created_at':str_created_at})
    access_collection.insert({'session_id':session_id,'access_token_twitter':'','access_token_secret_twitter':'','access_token_facebook':'',
                              'access_token_kakao':'','screen_name_twitter':'','screen_name_facebook':'','screen_name_kakao':'','created_at':created_at})


    url_parent_collection.insert({"session_id":session_id,"parent_random":v1,"created_at":created_at,"grand_parent_url":'',"sns":referer})
    return jinja2_template('twitter.html',session_id = session_id,random_character=v1)


#url을 공유한 노드를 통해 들어올시 이 함수 실행
@post('/url_sharer_children')
def url_sharer_children():

    #########url을 통해 공유한 노드의 정보를 입력하기 위해선, 자식노드가 부모노드를 통해 들어왔을때 부모노드를 parent_children_collection에
    ########다시 저장하는 방법을 사용한다. 왜? url을 긁어간 후 어디에 공유했는지 알수없기 때문이다.

    created_at = datetime.datetime.now()
    str_created_at = strftime("%y-%m-%d %H:%M:%S")
    global parent
    #parent_random은 부모노드가 누구인지 표시한다.
    parent_random = request.forms.get('parent')
    parent = parent_random
    #children_random은 현재 노드가 누군인지 표시한다.
    children_random = request.forms.get('children')
    #부모노드의 sns가 어디인지 표시한다
    parent_sns = request.forms.get('sns')
    if 'facebook' in parent_sns:
        parent_sns = "facebook"
    if 'twitter' in parent_sns:
        parent_sns = "twitter"
    if 'kakao' in parent_sns:
        parent_sns = "kakao"
    #부모노드의 정보를 가져온다.
    i = url_parent_collection.find_one({"parent_random":parent_random})
    #부모노드의 세션ID와 만들어진 일시를 가져온다.
    parent_session_id = i['session_id']
    parent_created_at = i['created_at']
    if share_collection.find({"my_randomkey":parent}).count()>0:
        i = share_collection.find_one({"my_randomkey":parent})
        visitor_count = i["count_visitor"] + 1
        share_collection.update_one({"my_randomkey":parent},{'$set':{"count_visitor":visitor_count}})

    ## 저장되어진 노드가 있을경우
    if url_parent_collection.find({"parent_random":parent_random}).count()>0:
        ##url로 공유한 사용자들의 정보를 업데이트한다. 업데이트전에 ' '으로 되어있다.
        url_parent_collection.update({"parent_random":children_random},{'$set':{'sns':parent_sns,'grand_parent_url':parent_random}})
        print 'updating....!!'

        jin = url_parent_collection.find_one({"parent_random":parent_random})
        print jin['sns'],'jin-s sns'
        print jin['grand_parent_url'],'grand_parent_url!!!'
        ## 현재 노드가 root에서 나온건지 확인한다.
        parent_url_pp = parent_children_collection.find_one({"sns":jin["sns"],"url_random":jin["grand_parent_url"]})
        ## 부모노드가 없다는 말은 parent 가 루트라는것을 의미한다.
        if jin["grand_parent_url"] == "":
            print 'check here 111'
            parent_children_collection.insert({"parent":"root",
                                               "created_at":parent_created_at,
                                               "article_key":1,
                                               "session_id":parent_session_id,
                                               "parent_sns":"none",
                                                "url_random":parent_random,
                                               "children":parent_random,
                                               "sns":parent_sns})
        ## 부모노드가 있으므로 자식을 찾고 share_url  DB에 입력한다. (url로 들어온 노드는 역으로 넣어주기에 grand_parent를 찾는다
        else :
            try:
                print 'check here 222'
                parent_children_collection.insert({"parent":parent_url_pp["children"],
                                               "created_at":parent_created_at,
                                               "article_key":1,
                                               "session_id":parent_session_id,
                                               "parent_sns":"" ,
                                                "url_random":parent_random,
                                                "children":parent_random,
                                                "sns":parent_sns})
            except Exception:
                print "duplicate!!"




    else :
        print 'check here!!!'



@route('/twitter')
def twitter():
    global  twitter_request_token
    resp, content = client_twitter.request(twitter_request_token_url, "GET")
    twitter_request_token = dict(urlparse.parse_qsl(content))
    twitterURL = twitter_authorize_url+"?oauth_token="+twitter_request_token['oauth_token']
    redirect(twitterURL)

@route('/facebook')
def facebook():
    redirect_uri = 'http://localhost:8011/get_oauth_facebook'
    facebookURL = facebook_request_token_url+ '?client_id=%s&redirect_uri=%s&scope=publish_stream,read_stream,offline_access,email&client_secret=%s&response_type=%s'%(facebook_consumer_key,redirect_uri,facebook_consumer_secret,'code')

    redirect(facebookURL)


@route('/kakao')
def kakao():
    redirect_uri = 'http://localhost:8011/get_oauth_kakao'
    kakaoURL = kakao_request_token_url+'client_id=%s&redirect_uri=%s&response_type=%s'%(kakao_consumer_key,redirect_uri,'code')
    redirect(kakaoURL)



##################oauth for twitter###################

@route('/get_oauth_twitter')
def get_oauth_twitter():
    created_at = datetime.datetime.now()
    str_created_at = strftime("%y-%m-%d %H:%M:%S")
    global twitter_access_token_regular
    global twitter_access_token_secret
    if flag == 2 :
        v1 = sns_v1
    if flag == 1 :
        v1 = url_v1
    session_id


    oauth_token = request.query['oauth_token']
    oauth_verifier = request.query['oauth_verifier']
    beaker_session = request.environ['beaker.session']

    token = oauth.Token(twitter_request_token['oauth_token'],twitter_request_token['oauth_token_secret'])

    token.set_verifier(oauth_verifier)
    twitter_client = oauth.Client(consumer_twitter,token)
    resp, content = twitter_client.request(twitter_access_token_url, "POST")
    access_token = dict(urlparse.parse_qsl(content))
    access_token_regular = access_token['oauth_token']
    access_token_secret = access_token['oauth_token_secret']


    auth = tweepy.OAuthHandler(twitter_consumer_key,twitter_consumer_secret)
    auth.set_access_token(access_token_regular,access_token_secret)
    api = tweepy.API(auth)
    user = api.verify_credentials()
    screen_name = user.screen_name
    try:
        id = user.id
        print id
    except:
        print "pass!!!"
    t_collection.insert({'beaker_session':session_id,'access_token':access_token_regular,'access_token_secret':access_token_secret,'screen_name_twitter':screen_name,'created_at':created_at})
    favorite_twitter_collection.insert({'access_token':access_token_regular,'screen_name_twitter':screen_name})

    if(access_collection.find({'screen_name_twitter':screen_name}).count()>0):
        access_collection.update({'screen_name_twitter':screen_name},{'$set':{'access_token_twitter':access_token_regular,'access_token_secret_twitter':access_token_secret,'created_at':created_at}})
        i = access_collection.find_one({'screen_name_twitter':screen_name})
        facebook_access_token_regular = i['access_token_facebook']
        kakao_access_token_regular = i['access_token_kakao']
    else :
        access_collection.update({},{'$set':{'access_token_twitter':access_token_regular,'access_token_secret_twitter':access_token_secret,'screen_name_twitter':screen_name,'created_at':created_at}})
        i = access_collection.find_one({'screen_name_twitter':screen_name})
        facebook_access_token_regular = i['access_token_facebook']
        kakao_access_token_regular = i['access_token_kakao']


    return jinja2_template('twitter.html',screen_name_twitter = screen_name,
                           random_character = v1,
                           access_token_regular_twitter=access_token_regular,
                           access_token_secret_twitter=access_token_secret,
                           access_token_regular_facebook = facebook_access_token_regular,
                           checker = 1,
                           access_token_regular_kakao = kakao_access_token_regular)




############################oauth for facebook##########################

import facebook
@get('/get_oauth_facebook')
def get_oauth_facebook():
    created_at = datetime.datetime.now()
    str_created_at = strftime("%y-%m-%d %H:%M:%S")
    global facebook_access_token_regular
    if flag == 2 :
        v1 = sns_v1
    if flag == 1 :
        v1 = url_v1
    code = request.query['code']
    session_id


    redirect = "http://localhost:8011/get_oauth_facebook"
    accessURL = facebook_access_token_url+"?client_id=%s&redirect_uri=%s&client_secret=%s&code=%s" %(facebook_consumer_key,redirect,facebook_consumer_secret,code)
    facebook_client = oauth.Client(consumer_facebook)
    resp,content = facebook_client.request(accessURL,"POST")
    facebook_access_token = dict(urlparse.parse_qsl(content))
    print facebook_access_token
    facebook_access_token_regular = facebook_access_token['access_token']
    get_facebook_id_url = facebook_graph_url+facebook_access_token_regular
    r = requests.get(get_facebook_id_url)
    list_info = r.json()
    print list_info,' list info!!!'
    f_collection.insert({'beaker_session':session_id,'access_token':facebook_access_token_regular,'screen_name_facebook':list_info['name'],'created_at':created_at})
    favorite_facebook_collection.insert({'access_token':facebook_access_token_regular,'screen_name_facebook':list_info['name']})

    if(access_collection.find({'screen_name_facebook':list_info['name']}).count()>0):
        access_collection.update({'screen_name_facebook':list_info['name']},{'$set':{'access_token_facebook':facebook_access_token_regular,'created_at':created_at}})
        i = access_collection.find_one({'screen_name_facebook':list_info['name']})
        kakao_access_token_regular = i['access_token_kakao']
        twitter_access_token_regular = i['access_token_twitter']
        twitter_access_token_secret = i['access_token_secret_twitter']
    else :
        access_collection.update({},{'$set':{'access_token_facebook':facebook_access_token_regular,'screen_name_facebook':list_info['name'],'created_at':created_at}})
        i = access_collection.find_one({'screen_name_facebook':list_info['name']})
        kakao_access_token_regular = i['access_token_kakao']
        twitter_access_token_regular = i['access_token_twitter']
        twitter_access_token_secret = i['access_token_secret_twitter']



    return jinja2_template('twitter.html',screen_name_facebook = list_info['name'],
                           access_token_regular_facebook=facebook_access_token_regular,
                           access_token_regular_twitter=twitter_access_token_regular,
                           access_token_secret_twitter=twitter_access_token_secret,
                           random_character=v1,
                           checker = 2,
                           access_token_regular_kakao = kakao_access_token_regular)



#################################oauth for kakao##########################

@get('/get_oauth_kakao')
def get_oauth_kakao():
    created_at = datetime.datetime.now()
    str_created_at = strftime("%y-%m-%d %H:%M:%S")
    global kakao_access_token_regular
    if flag == 2 :
        v1 = sns_v1
    if flag == 1 :
        v1 = url_v1

    redirect_uri = "http://localhost:8011/get_oauth_kakao"
    code = request.query['code']
    accessURL = kakao_access_token_url+"grant_type=authorization_code&client_id=%s&redirect_uri=%s&code=%s"%(kakao_consumer_key,redirect_uri,code)
    print accessURL,'accessURL!!!'
    r = requests.post(accessURL)

    access_info = r.json()
    kakao_access_token_regular = access_info['access_token']
    info_url = 'https://kapi.kakao.com/v1/api/talk/profile?access_token='
    request_info = info_url+kakao_access_token_regular

    r = requests.get(request_info)
    print r,'!!~~~!!!!'

    list_info = r.json()
    print list_info,'!!!!!!!'
    session_id


    k_collection.insert({'beaker_session':session_id,'access_token':kakao_access_token_regular,'screen_name_kakao':list_info['nickName'],'created_at':created_at})
    favorite_kakao_collection.insert({'access_token':kakao_access_token_regular,'screen_name_kakao':list_info['nickName']})

    if(access_collection.find({'screen_name_kakao':list_info['nickName']}).count()>0):
        access_collection.update({'screen_name_kakao':list_info['nickName']},{'$set':{'access_token_kakao':kakao_access_token_regular,'created_at':created_at}})
        i = access_collection.find_one({'screen_name_kakao':list_info['nickName']})
        facebook_access_token_regular = i['access_token_facebook']
        twitter_access_token_regular = i['access_token_twitter']
        twitter_access_token_secret = i['access_token_secret_twitter']
    else :
        access_collection.update({},{'$set':{'access_token_kakao':kakao_access_token_regular,'screen_name_kakao':list_info['nickName'],'created_at':created_at}})
        i = access_collection.find_one({'screen_name_kakao':list_info['nickName']})
        facebook_access_token_regular = i['access_token_facebook']
        twitter_access_token_regular = i['access_token_twitter']
        twitter_access_token_secret = i['access_token_secret_twitter']


    return jinja2_template('twitter.html',screen_name_kakao = list_info['nickName'],
                           access_token_regular_facebook=facebook_access_token_regular,
                           access_token_regular_twitter=twitter_access_token_regular,
                           access_token_secret_twitter=twitter_access_token_secret,
                           random_character=v1,
                           checker = 3,
                           access_token_regular_kakao = kakao_access_token_regular)




#####################upload for twitter###########################

@get('/upload_opinion_twitter')
def upload_opinion_twitter():
    created_at = datetime.datetime.now()
    str_created_at = strftime("%y-%m-%d %H:%M:%S")
    if flag == 2 :
        v1 = sns_v1
    if flag == 1 :
        v1 = url_v1
    twitter_randomkey = ''.join(random.sample(c,7))
    link = request.query['real_url_twitter']
    beaker = request.query['beaker_twitter']
    opinion = request.query['opinion_twitter']
    session_id
    access = request.query['access_token_twitter']
    alter_refer = request.query['referer']


    referer = alter_refer
    access_secret = request.query['access_token_secret_twitter']
    opinion_with_palette = opinion+'  '+'http://127.0.0.1:8011/start/'+twitter_randomkey
    share_collection.insert({"my_randomkey":twitter_randomkey,"sns":"twitter","session_id":session_id,"created_at":created_at,"count_visitor":0,'str_created_at':str_created_at})
    parent_children_collection.insert({'parent':parent,'children':twitter_randomkey,'sns':'twitter','parent_sns':referer,'session_id':session_id,'created_at':created_at,'article_key':1,"url_random":v1})
    auth = tweepy.OAuthHandler(twitter_consumer_key,twitter_consumer_secret)
    auth.set_access_token(access,access_secret)
    api = tweepy.API(auth)
    api.update_status(opinion_with_palette)
    list = {"random_children":v1}
    return list
##########################upload for facebook##########################

@get('/upload_opinion_facebook')
def upload_opinion_facebook():
    created_at = datetime.datetime.now()
    str_created_at = strftime("%y-%m-%d %H:%M:%S")
    if flag == 2 :
        v1 = sns_v1
    if flag == 1 :
        v1 = url_v1
    facebook_randomkey = ''.join(random.sample(c,7))
    link = request.query['real_url_facebook']
    beaker = request.query['beaker_facebook']
    opinion = request.query['opinion_facebook']
    session_id
    opinion_with_palette = opinion+'  '+'http://127.0.0.1:8011/start/'+facebook_randomkey
    facebook_access_token_regular = request.query['access_token_facebook']
    get_facebook_id_url = facebook_graph_url+facebook_access_token_regular
    r = requests.get(get_facebook_id_url)
    list_info = r.json()
    graph = facebook.GraphAPI(access_token=facebook_access_token_regular,version='2.5')
    id  = list_info['id']
    name = list_info['name']
    alter_refer = request.query['referer']

    #if flag == 2 :
    referer = alter_refer
    share_collection.insert({"my_randomkey":facebook_randomkey,"sns":"facebook","session_id":session_id,"created_at":created_at,"count_visitor":0,'str_created_at':str_created_at})
    parent_children_collection.insert({'parent':parent,'children':facebook_randomkey,'sns':'facebook','parent_sns':referer,'session_id':session_id,'created_at':created_at,'article_key':1,"url_random":v1})
    graph.put_object(id, "feed", message=opinion_with_palette)
    list = {"random_children":v1}
    return list

#########################upload for kakao#################################

@get('/upload_opinion_kakao')
def upload_opinion_kakao():
    created_at = datetime.datetime.now()
    str_created_at = strftime("%y-%m-%d %H:%M:%S")
    if flag == 2 :
        v1 = sns_v1
    if flag == 1 :
        v1 = url_v1
    kakao_randomkey = ''.join(random.sample(c,7))
    opinion = request.query['opinion_kakao']
    opinion_with_palette = opinion+'  '+'http://127.0.0.1:8011/start/'+kakao_randomkey
    session_id
    alter_refer = request.query['referer']

    #if flag == 2 :
    referer = alter_refer
    kakao_access_token_regular = request.query['access_token_kakao']
    get_kakao_url = kakao_upload_url+kakao_access_token_regular+'&content='+opinion_with_palette
    share_collection.insert({"my_randomkey":kakao_randomkey,"sns":"kakao","session_id":session_id,"created_at":created_at,"count_visitor":0,'str_created_at':str_created_at})

    parent_children_collection.insert({'parent':parent,'children':kakao_randomkey,'sns':'kakao','parent_sns':referer,'session_id':session_id,'created_at':created_at,'article_key':1,"url_random":v1})
    requests.post(get_kakao_url)
    list = {"random_children":v1}
    return list




@post('/favorite_twitter')
def favorite_twitter():
    created_at = datetime.datetime.now()
    str_created_at = strftime("%y-%m-%d %H:%M:%S")
    if flag == 2 :
        v1 = sns_v1
    if flag == 1 :
        v1 = url_v1
    session_id = request.forms.get('session_id')
    access_token = request.forms.get('access_token_twitter')
    i = favorite_twitter_collection.find_one({'access_token':access_token})
    favorite = i['screen_name_twitter']
    if favorite_collection.find({'beaker_session':session_id}).count()>0:
        favorite_collection.update_one({'beaker_session':session_id},{'$set':{'favorite':favorite}})
    else:
        favorite_collection.insert({'beaker_session':session_id,'favorite':favorite,'created_at':created_at})

    list = {"screen_name":favorite,"random_children":v1}
    return list

@post('/favorite_facebook')
def favorite_facebook():
    created_at = datetime.datetime.now()
    str_created_at = strftime("%y-%m-%d %H:%M:%S")
    if flag == 2 :
        v1 = sns_v1
    if flag == 1 :
        v1 = url_v1
    session_id = request.forms.get('session_id')
    access_token = request.forms.get('access_token_facebook')
    i = favorite_facebook_collection.find_one({'access_token':access_token})
    favorite =  i['screen_name_facebook']
    if favorite_collection.find({'beaker_session':session_id}).count()>0:
        favorite_collection.update_one({'beaker_session':session_id},{'$set':{'favorite':favorite}})
    else:
        favorite_collection.insert({'beaker_session':session_id,'favorite':favorite,'created_at':created_at})

    list = {"screen_name":favorite,"random_children":v1}
    return list



@post('/favorite_kakao')
def favorite_kakao():
    created_at = datetime.datetime.now()
    str_created_at = strftime("%y-%m-%d %H:%M:%S")
    if flag == 2 :
        v1 = sns_v1
    if flag == 1 :
        v1 = url_v1
    session_id = request.forms.get('session_id')
    access_token = request.forms.get('access_token_kakao')
    i = favorite_kakao_collection.find_one({'access_token':access_token})
    favorite = i['screen_name_kakao']
    if favorite_collection.find({'beaker_session':session_id}).count()>0:
        favorite_collection.update_one({'beaker_session':session_id},{'$set':{'favorite':favorite}})
    else:
        favorite_collection.insert({'beaker_session':session_id,'favorite':favorite,'created_at':created_at})

    list = {"screen_name":favorite,"random_children":v1}
    return list

@route('/draw_json')
def draw_json():
    return jinja2_template('draw_json.html')


@route('/static/<path:path>')
def callback(path):
    return static_file(path, root='./static')


def main():

    run(app=app,host='0',port=8011,server='tornado')




if __name__ == "__main__":
    client = MongoClient('localhost')
    #트위터의 엑세스 토큰을 저장 DB.
    t_collection = client['trace_project']['twitter']
    #페이스북의 엑세스 토큰을 저장 DB.
    f_collection = client['trace_project']['facebook']
    #카카오의 엑세스 토큰을 저장 DB.
    k_collection = client['trace_project']['kakao']
    #마지막으로 클릭한 SNS를 저장하는 DB
    favorite_collection = client['trace_project']['favorite']
    #연결된 모든 엑세스토큰을 저장하는 DB
    access_collection = client['trace_project']['access_token']
    #트위터 엑세스토큰의 정보를 저장하는 DB
    favorite_twitter_collection = client['trace_project']['favorite_twitter']
    #페이스북 엑세스토큰의 정보를 저장하는 DB
    favorite_facebook_collection = client['trace_project']['favorite_facebook']
    #카카 엑세스토큰의 정보를 저장하는 DB
    favorite_kakao_collection = client['trace_project']['favorite_kakao']
    #핵심 DB / 각노드의 자신과 자신의 부모를 보여주는 DB
    parent_children_collection = client['trace_project']['share_url']
    #위의 DB에 중복을 허용하지 않게 만드는 명령
    parent_children_collection.ensure_index('children',unique =True)
    #해당 노드를 통해 몇명이 들어왔는지를 보여준다.
    share_collection = client['trace_project']['sharer_url']
    #url로 공유하는 사용자를 track한다.
    url_parent_collection = client['trace_project']['url_parent']


    main()








