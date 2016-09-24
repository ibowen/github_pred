import requests
import json
import time
from pymongo import MongoClient
import random
import pandas as pd
import logging

# configure log files
logging.basicConfig(filename='starring_retrieval_full.log',level=logging.DEBUG)

def github_request(params, headers, per_page=30, page=1, show_head=False, show_body=False, is_write=False):
    """ Description: function to perform a github api request
        - params: a list of request parameters
        - headers: a dict of request headers
        - per_page: defalt 30 records per page, can go up to 100
        - page: default starts from page 1
        - show_head: default False, not show the response head
        - show_body: default False, not show the response body
        - is_write: default False, if write out to json file, default in current directory
        - return: a string of status code, and a json object of response
    """
    url = "https://api.github.com/" + '/'.join(params) + '?per_page={}&page={}'.format(per_page, page)
    logging.debug('requesting: ' + url)
    print 'requesting: ' + url

    try:
        response = requests.get(url, headers=headers) # get response
    except:
        logging.exception('Got exception on requesting' + url)
        raise
    if show_body:
        # body
        logging.debug(json.dumps(response.json(), indent=1))

    if show_head:
        # header
        for (k,v) in response.headers.items():
            logging.debug(str(k) + " => " + str(v))

    file_name = '.'.join(params) + '.json'
    if is_write:
        with open(file_name, 'w') as jsonfile:
            json.dump(response.json(), jsonfile)

    logging.debug('total records of this request: {}'.format(len(response.json())))
    print 'total records of this request: {}'.format(len(response.json()))
    return response.headers['Status'], response.json()

def dump_mongo(db_url, db_name, params, headers):
    """ Description: function to dump github api into mongodb
        - db_url: mongodb url
        - db_name: mongodb database name
        - params: github api params
        - headers: github api headers
    """
    mongocli = MongoClient(db_url)# init mongodb client
    mongodb = mongocli[db_name] # connect 'github' database
    
    page = 1
    collection_name = '.'.join(params)
    start_time = time.time()
    while True:
        status, json_body = github_request(params, headers,per_page=100,page=page)
        logging.debug('page {} : '.format(page) + 'status: ' + status + '\n')

        if status == '422 Unprocessable Entity' or len(json_body) == 0:
            break
        try:
            mongodb[collection_name].insert(json_body)
        except:
            logging.exception('Got exception on inserting mongodb')
            raise
        page += 1
        time.sleep(1)
    mongocli.close() # close connection
    elapsed_time = time.time() - start_time
    logging.debug('completed: {}'.format(elapsed_time))
    print 'completed: {}'.format(elapsed_time)

def main():

    # configure api, mongodb
    ACCESS_TOKEN = '219c8c8184c45933dd259f21eaf5ff726387e7ed'
    db_url = 'ec2-54-67-97-244.us-west-1.compute.amazonaws.com:27017'
    db_name = 'starrings'
    headers = {'Authorization' : 'token {}'.format(ACCESS_TOKEN),'Accept' : 'application/vnd.github.v3.star+json'}

    # construct repo params for api
    repos = pd.read_csv('./data/repos-with-homepage.csv')
    repo_portfolio = repos[['org_id', 'name']]
    starring_list = []
    for _, row in repo_portfolio.iterrows():
        starring_list.append(['repos', row['org_id'], row['name'], 'stargazers'])
    # start retrieving
    for starring in starring_list:
        print 'start requesting: {}/{}'.format(starring[1], starring[2])
        logging.debug(starring)
        dump_mongo(db_url,db_name,starring,headers)

if __name__ == '__main__':
    main()




