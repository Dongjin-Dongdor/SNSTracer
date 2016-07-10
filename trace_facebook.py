#-- coding: utf-8 --
__author__ = 'gimdongjin'


import oauth2 as oauth
import string
import random
from bottle import request, run, route, jinja2_template, post, get, hook
import bottle
from beaker.middleware import  SessionMiddleware
import urlparse
import tweepy
from pymongo import MongoClient
from json import dumps
from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import facebook_compliance_fix
import sys
import urllib2

reload(sys)
sys.setdefaultencoding('utf-8')


session_opts = {
    'session.type': 'memory',
    'session.cookie_expires': 300,
    'session.auto': True
}


app = SessionMiddleware(bottle.app(),session_opts)


AppID = "1719277154971838"
AppSecret = "8bd66003086da2df2a23fbfe378df2cc"

FACEBOOK_ACCESS_TOKEN_URL = 'https://graph.facebook.com/oauth/access_token'
FACEBOOK_REQUEST_TOKEN_URL = 'https://www.facebook.com/dialog/oauth'
FACEBOOK_CHECK_AUTH = 'https://graph.facebook.com/me'

code = request.GET.get('code')

consumer = oauth.Consumer(AppID,AppSecret)
client = oauth.Client(consumer)
redirect_uri = 'http://localhost:8081/get_auth'
request_url = FACEBOOK_REQUEST_TOKEN_URL + '?client_id=%s&redirect_uri=%s&client_secret=%s&response_type=%s' %(AppID,redirect_uri,AppSecret,'code')
access_token_regular = ''

print request_url


@route('/get_auth')
def get_oauth():
    code = request.query['code']
    redirect = "http://localhost:8081/get_auth"
    access_request = FACEBOOK_ACCESS_TOKEN_URL+"?client_id=%s&redirect_uri=%s&client_secret=%s&code=%s" %(AppID,redirect,AppSecret,code)
    client = oauth.Client(consumer)
    resp,content = client.request(access_request,"POST")

    access_token = dict(urlparse.parse_qsl(content))
    access_token_regular = access_token['access_token']

    # req = urllib2.Request(access_request)
    # response = urllib2.urlopen(req)
    # str = response.read()
    # print str




@route('/get_access_detail')
def get_access_detail():
    print 'good!!!'




def main():
    run(app=app,host='0',port=8081,server='tornado')


if __name__ == "__main__":

    main()


