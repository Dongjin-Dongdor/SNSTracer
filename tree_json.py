__author__ = 'gimdongjin'




from pymongo import MongoClient
import json


client = MongoClient('localhost')
parent_children_collection = client['trace_project']['share_url']
sharer_collection = client['trace_project']['sharer_url']

trace_list = []
i = parent_children_collection.find({'article_key':1})

for get in i :
    parent = get['parent']
    print parent,'!!!'
    children = get['children']
    print children,'@@@'
    sns = get['sns']
    trace_tuple = (parent,children,sns)
    trace_list.append(trace_tuple)

trace_list_real = []
print trace_list,'trace_list!!!'

for x in trace_list:
    if x[2] != 'not yet':
        trace_list_real.append(x)
print trace_list_real


parent, children, sns = zip(*trace_list_real)


global d
def get_nodes(name,sns):

    d ={}
    d["name"] = name
    kkk = parent_children_collection.find_one({"children":name})

    d["sns"] = kkk["sns"]
    d["size"] = 3000
    d["share_count_direct"] =  get_children_direct_number(name)
    d["share_count_all"] =  count_children(name) -1
    d["share_twitter"] = count_twitter(name,0)

    print d["share_twitter"],"twitter",d["name"]
    d["share_facebook"] = count_facebook(name,0)
    print d["share_facebook"],"facebook",d["name"]
    d["share_kakao"] = count_kakao(name,0)
    print d["share_kakao"],"kakao",d["name"]

    if sharer_collection.find({"my_randomkey":name}).count()>0:
        sharer = sharer_collection.find_one({"my_randomkey":name})
        d["count"] = sharer['count_visitor']
        d["share_time"] = sharer['str_created_at']
    children = get_children(name)
    k = []

    if children:

            d["children"] = [get_nodes(child,1) for child in children]
        #print d
    return d

# def get_children_number(name):
#     count = 0
#     children = get_children(name)
#     if  children:
#
#     else:

def count_twitter(name, num):
    global twitter_count
    twitter_count = num
    for x in trace_list_real:
        if x[0] == name :
            if x[2] == 'twitter':
                twitter_count = twitter_count + 1
            count_twitter(x[1],twitter_count)
    return twitter_count

def count_facebook(name, num):
    global facebook_count
    facebook_count = num
    for x in trace_list_real:
        if x[0] == name:
            if x[2] == "facebook":
                facebook_count = facebook_count +1
            count_facebook(x[1],facebook_count)
    return facebook_count


def count_kakao(name, num):
    global kakao_count
    kakao_count = num
    for x in trace_list_real:
        if x[0] == name:
            if x[2] == "kakao":
                kakao_count = kakao_count + 1
            count_kakao(x[1], kakao_count)
    return kakao_count

def count_children(name):
    global count
    count  = 1

    for x in trace_list_real:
        if x[0] ==  name:
            count  = count + count_children(x[1])
    return count


def get_children_direct_number(name):
    count = 0
    for x in trace_list_real:
        if x[0] == name:
            count += 1
    return count


def get_children(name):
    children_list = []
    for x in trace_list_real:
        if x[0]==name:
            children_list.append(x[1])
    return children_list



root_nodes = dict()
def main():
    global root_nodes
    root_nodes['name'] = 'root'
    json_list = []
    for x in trace_list_real:
        if x[0]=='root' :
            json_list.append(get_nodes(x[1],x[2]))
    root_nodes['children'] = json_list
    write_tree =  json.dumps(root_nodes, indent=4)
    write_json = open('graph_test.json','wb')
    write_json.write(write_tree)
    write_json.close

main()
