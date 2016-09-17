# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 18:35:53 2016

@author: Wan
"""

#   60a5c1170d61dde715b1f429fea73ad22ce6402b
###   https://developer.github.com/v3/repos/statistics/#get-the-weekly-commit-count-for-the-repository-owner-and-everyone-else
import time
import json
import requests
import urllib2

from pymongo import MongoClient
import pandas as pd


###   check status
def checkResponse(x):
    if x.headers['Status'] <> '200 OK':
        print(x.headers['Status'])

    else:
        print('Status: 200 OK')


def getGitStat(thisUrl,passCode,countFailure):
    while(passCode == '0'):
        thisResponse = requests.request('GET',thisUrl, headers= headers)
        request_Status = thisResponse.headers['Status']

        #   status = 202 accepted
        if request_Status == '202 Accepted':
            countFailure += 1
            time.sleep(3)
            getGitStat(thisUrl, passCode, countFailure)

        #   other issues
        elif request_Status <> '200 OK':
            print(thisResponse.headers['Status'])
            countFailure += 1

        #   status = 200: ok
        else :
            passCode = '1'      # 0: not pass, 1: pass
            return request_Status,thisResponse.json()

        if countFailure >=9:
            print(request_Status + " happend " + str(countFailure) + " times.")
            break

#####################################################################
###                Test Connection with MongoDB                   ###
#####################################################################

import pymongo
################################################
###           Configure MongoDB              ###
################################################
#   location where to store sample data
db_url = '127.0.0.1:27017'                #   local
db_name = 'sample_data'                   #   sample data for mis-586 project

conn = MongoClient(db_url)        #   init mongodb client
db = conn[db_name]                #   connect local database 'sample_data'

#   test connection with MongoDB
try:
    conn = pymongo.MongoClient(db_url)
    print ("MongoDb is Connected: Good to go!")

except pymongo.errors.ConnectionFailure, e:
    print "error: %s" %e

###   drop target tables
db.Stats_w_all_commits.drop()
db.Stats_w_commit_act.drop()
db.Stats_w_freq.drop()
db.Stats_52w_cmmt.drop()
db.Stats_day_hr_com.drop()


###                 db is ready                  ###
####################################################

###############################################################
###            check connection with github                 ###
###############################################################
headers = {'Authorization': 'token 60a5c1170d61dde715b1f429fea73ad22ce6402b'}
connurl = 'https://api.github.com/user'
payload = {}
r = requests.post(connurl, data = json.dumps(payload), headers = headers)
r
checkResponse(r)
###   request should be successfully collected

#############################################################
###        setup extension for different projects         ###
#############################################################
#
repo_url = 'https://api.github.com/repos'

#   setup sample repository
#   Owner, RepoName
repo_portfolio = [['lebinh', 'ngxtop'],
                  ['IanLunn', 'Hover'],
                  ['eczarny', 'spectacle'],
                  ['JakeWharton', 'ViewPagerIndicator'],
                  ['rendrjs', 'rendr'],
                  ['inconshreveable', 'ngrok'],
                  ['madebymany', 'sir-trevor-js'],
                  ['jschr', 'bootstrap-modal'],
                  ['carrierwaveuploader', 'carrierwave'],
                  ['jquery', 'jquery-ui']]

#   declear extension of each stat measures
contributors = '/stats/contributors'        ##  Get contributors list with additions, deletions, and commit counts
commit_activity = '/stats/commit_activity'  ##  Get the last year of commit activity data
code_frequency = '/stats/code_frequency'    ##  Get the number of additions and deletions per week
participation = '/stats/participation'      ##  Get the weekly commit count for the repository owner and everyone else
punch_card = '/stats/punch_card'            ##  Get the number of commits per hour in each day

#   take the start time
start_time = time.time()

#   loop position
position = 0
####################################################################
###             scratch data from github one by one              ###
####################################################################

for i in repo_portfolio:
    #   define url for the current repo: owner, repoName, url that shared with all stat measures
    thisOwner = i[0]                                      #   get owner name of the ith repo
    thisRepoName = i[1]                                   #   get repoName of the ith repo

    #   compile the full url for this repo
    thisUrl = repo_url + '/' + thisOwner + '/' + thisRepoName

    #   1
    ############################################################################
    ###   Test contributors list with additions, deletions, and commit counts
    ###                     key word  ==>  contributors                      ###
    ############################################################################
    # contributors list with additions, deletions, and commit counts
    #   compile the full url for this repo
    statUrl = thisUrl + contributors

    #   initialize parameters
    countFailure = 0
    passCode = '0'                                             # not pass

    #   capture the i th  json object, which is a list in python represented by json_body
    request_Status,json_body = getGitStat(statUrl,passCode,countFailure)

    print(str(position) + " contributors:   "  + request_Status)      #   print out status and number of repo

    # index, json_body
    indexed_body = {"owner":thisOwner, "repo":thisRepoName,   "content":json_body}

    #   create table Stats_w_all_commits
    collection = db.Stats_w_all_commits               # table Stats_w_all_commits
    collection.insert(indexed_body)                   # insert into "Stats_w_all_commits"
    print(str(position) + ' contributors' + ' inserted 200: OK')
    time.sleep(1)
    ##################################################################

    ###    2
    ######################################################################
    ###      test Get the number of additions and deletions per week
    ###                key word  ==>  commit_activit                   ###
    ######################################################################
    ###   Get the last year of commit activity data
    passCode = '0'                         # not passed
    statUrl = thisUrl + commit_activity
    countFailure = 0

    #  capture the i th  json object, which is a list in python represented by json_body
    request_Status,json_body = getGitStat(statUrl,passCode,countFailure)
    print(str(position) + " commit_activity:   "  + request_Status)      #   print out status and number of repo

    # index, json_body
    indexed_body = {"owner":thisOwner, "repo":thisRepoName,   "content":json_body}

    #   Create table Stats_w_commit_act
    collection = db.Stats_w_commit_act     # table Stats_w_commit_act
    collection.insert(indexed_body)           # insert into "Stats_w_commit_act"

    print(str(position) + " commit_activity" + " inserted 200: OK")

    time.sleep(1)
    ##################################################################


    ###    3
    ######################################################################
    ###      test Get the number of additions and deletions per week
    ###                key word  ==>  code_frequency                   ###
    ######################################################################
    ###   Get the number of additions and deletions per week
    passCode = '0'
    statUrl = thisUrl + code_frequency
    countFailure = 0                          # refresh failure counter

    #  capture the i th  json object, which is a list in python represented by json_body
    request_Status,json_body = getGitStat(statUrl,passCode,countFailure)
    print(str(position) + " code_frequency:   "  + request_Status)      #   print out status and number of repo

    # index, json_body
    indexed_body = {"owner":thisOwner, "repo":thisRepoName,   "content":json_body}

    #   Create table Stats_w_freq
    collection = db.Stats_w_freq              # table Stats_w_freq
    collection.insert(indexed_body)           # insert into "Stats_w_freq"

    print(str(position) + ' code_frequency' + ' inserted 200: OK')

    time.sleep(1)
    ##################################################################


    ###    4
    #########################################################################
    ###      Test Get the weekly commit count for the repository owner    ###
    ###      and everyone else                                            ###
    ###                    key word  ==>  participation                   ###
    ###      from oldeest [0] to most current in the last 52 weeks        ###
    ###      contains "all" and "owner"                                   ###
    #########################################################################
    ###   Get the weekly commit count for the repository owner
    passCode = '0'
    statUrl = thisUrl + participation
    countFailure = 0                          # refresh failure counter

    #  capture the i th  json object, which is a list in python represented by json_body
    request_Status,json_body = getGitStat(statUrl,passCode,countFailure)
    print(str(position) + " participation:   "  + request_Status)      #   print out status and number of repo

    # index, json_body
    indexed_body = {"owner":thisOwner, "repo":thisRepoName,   "content":json_body}

    #   Create table Stats_52w_cmmt
    collection = db.Stats_52w_cmmt            # table Stats_52w_cmmt
    collection.insert(indexed_body)           # insert into "Stats_52w_cmmt"

    print(str(position) + ' participation' + ' inserted 200: OK')
    time.sleep(1)
    ##################################################################

    ###    5
    ##############################################################################
    ###      Test Get the number of commits per hour in each day               ###
    ###                    key word  ==>  punch_card                           ###
    ##            attr_1: 0-6: Sunday - Saturday                               ###
    ##            attr_2: 0-23: Hour of day                                    ###
    ##            attr_3: Number of commits                                    ###
    ###      For example:   [2, 14, 25] indicates that                         ###
    ###      there were 25 total commits, during the 2:00pm hour on Tuesdays.  ###
    ###      All times are based on the time zone of individual commits.       ###
    ##############################################################################
    ###   Get the number of commits per hour in each day
    passCode = '0'
    statUrl = thisUrl + punch_card
    countFailure = 0                          # refresh failure counter

    #   capture the i th  json object, which is a list in python represented by json_body
    request_Status,json_body = getGitStat(statUrl,passCode,countFailure)
    print(str(position) + " punch_card:   "  + request_Status)      #   print out status and number of repo

    # index, json_body
    indexed_body = {"owner":thisOwner, "repo":thisRepoName,   "content":json_body}

    #   Create table Stats_day_hr_com
    collection = db.Stats_day_hr_com          # table Stats_day_hr_com
    collection.insert(indexed_body)           # insert into "Stats_day_hr_com"

    print(str(position) + ' punch_card' + ' inserted 200: OK')
    time.sleep(1)

    ##################################################################
    #   move forward
    position += 1



conn.close()             # close connection with MongoDB
end_time = time.time()
print(end_time - start_time)




