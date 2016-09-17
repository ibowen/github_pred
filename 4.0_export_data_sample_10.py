# -*- coding: utf-8 -*-
"""
Created on Thu Sep 15 22:50:45 2016

@author: Wan
"""
import os
import datetime
import csv
from pymongo import MongoClient
import pandas as pd

###   convert unix time stamp to readable dates
###   convert a column of unix timestamp into readable dates
def convertDate(df,time_stamp_col):
    new_df = df
    date = list()                          # new date list
    #   convert unix timestamp
    for i in df[time_stamp_col]:
        nextDate = CvtUnixTime(i)
        date.append(nextDate)

    new_df['date'] = date
    new_df = new_df.drop(time_stamp_col,axis=1)    # time_stamp_col = 'week' or 'w'
    return new_df

###   in this py, five functions that convert Json style data into dataframe format
###   will be defined in Development Environment

#   db.Stats_w_all_commits        <== Table 1
    #   output 1:   ===>     df_stat_repo_main
    #   output 2:   ===>     df_contribution_his
    #   output 3:   ===>     df_contributors
#   db.Stats_w_commit_act         <== Table 2
    #   output 1:   ===>     df_weekly_commits
#   db.Stats_w_freq               <== Table 3
    #   output 1:   ===>     df_Stats_w_freq
#   db.Stats_52w_cmmt             <== Table 4
    #   output 1:   ===>     df_Stats_52w_cmmt
#   db.Stats_day_hr_com           <== Table 5
    #   output 1:   ===>     df_Stats_day_hr_comt


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

conn = MongoClient(db_url)                #   init mongodb client
db = conn[db_name]                        #   build conn to local database 'sample_data'

#   test connection with MongoDB
try:
    conn = pymongo.MongoClient(db_url)
    print ("MongoDb is Connected: Good to go!")

except pymongo.errors.ConnectionFailure, e:
    print "error: %s" %e



###        connection is ready
##########################################################################

#   convert unix time to
def CvtUnixTime(u):
    date = datetime.datetime.utcfromtimestamp(u).strftime('%Y-%m-%d %H:%M:%S')
    return date

#   ddl    for     db.Stats_w_all_commits
###   1: df_contribution_his
###   a history table cumulate all contribution details
###       a, c, d,          w, contributorName,               repoIndex
###   eg: 0  0  0  1473552000           jreese     ['lebinh', 'ngxtop']
###   a - # of additions
###   d - # of deletions
###   c - # of commits
###   w - Start of the week, given as a Unix timestamp.

#   ddl
###   2: df_contributors
###   a static table stores info of contributors
###       a, c, d,          w, contributorName,               repoIndex
###   eg: 0  0  0  1473552000           jreese     ['lebinh', 'ngxtop']
###   a - # of additions
###   d - # of deletions
###   c - # of commits
###   w - Start of the week, given as a Unix timestamp.



#   define function getContribution_His: History of Contributor's commits
#   input table name: Stats_w_all_commits
#   output table: df_repo_main, df_contribution_his, df_contributors

###   parameters: db   <== the database from which your data get extracted
#    TABLE 1
def convert_Stats_w_all_commits(db_url, db_name):
    conn = MongoClient(db_url)                #   init mongodb client
    db = conn[db_name]                        #   build conn to local database 'sample_data'
    collection = db.Stats_w_all_commits

    #   get all records in table_1  Stats_w_all_commits
    #   for sample data, returns 10 records, each for a particular repositary labeled as owner, repoName
    records = collection.find()
    #   generate output tables: df_stat_repo_main, df_contribution_his,df_contributors
    df_stat_repo_main = pd.DataFrame()
    df_contribution_his = pd.DataFrame()
    df_contributors = pd.DataFrame()

    # position in loop
    position = 0

    #   content, index
    for items in records:
        #   initialize total number of contributions for this repo
        ttl_repo_contributions = 0

        #   capture total number of contributors for each repository
        ttl_contributors = len(items['content'])

        #   indicate which repo it is
        thisOwner = items['owner']
        thisRepo = items['repo']

        #   each record contains commits from multiple contributors
        #   Contributors:   info and commits stat measures for a particular contributors
        #   remember to close your cursor after u finish processing the data

        for contributors in items['content']:
            #   remember to close your cursor after u finish processing the data

            #   get name of contributor
            contriName = contributors['author']['login']
            #   get type of contributor
            userType = contributors['author']['type']

            #   get The Total number of commits authored by the contributor.
            ttl_user_commits = contributors['total']

            #   increment contribution
            ttl_repo_contributions += ttl_user_commits

            #   show number of contributions
            print( contriName + "'s number of contributions:  " + str(ttl_user_commits))

            ###################################################################
            ###                   insert data into tables                   ###
            ###         df_contribution_his and df_contributors
            ###################################################################

            #   capture contribution history of this contributor
            df = pd.DataFrame(list(contributors['weeks']))

            col_list = list(df)
            df['owner'] = thisOwner
            df['repo'] = thisRepo
            df['contributorName'] = contriName

            print("converted")
            #   insert into Table df_contribution_his
            df_contribution_his = df_contribution_his.append(df)

            #   insert into Table df_contributors
            #   prepare data into subtotal
            col_list.remove('w')
            df_subtotal = df[col_list].sum()
            df_subtotal = pd.DataFrame(df_subtotal)
            df_subtotal = df_subtotal.T

            df_subtotal['contributorName'] = contriName
            df_subtotal['owner'] = thisOwner
            df_subtotal['repo'] = thisRepo
            df_subtotal['userType'] = userType

            #   insert into Table df_contributors
            df_contributors = df_contributors.append(df_subtotal)

            #   insert into Table df_stat_repo_main
            df_stat_repo_main = df_contribution_his[['a','c','d','w','owner','repo']]
            df_stat_repo_main = df_stat_repo_main.groupby(['w','owner','repo'])[['a','c','d']].sum()

        #   position forward
        print(str(position))
        position += 1

        ###   loop ended
    conn.close()                               # close connection with MongoDB
    #    return tables
    return df_stat_repo_main,df_contributors, df_contribution_his

    ###   function convert_Stats_w_all_commits has been defined
    ########################################################################



#   ddl    for     db.Stats_w_commit_act       <== Table 2
###   Get the last year of commit activity data

def convert_Stats_w_commit_act(db_url, db_name):
    conn = MongoClient(db_url)                #   init mongodb client
    db = conn[db_name]                        #   build conn to local database 'sample_data'
    #   identify the table you in database
    collection = db.Stats_w_commit_act


    #   get all records in table_2  Stats_w_commit_act
    #   for sample data, returns 10 records, each for a particular repositary labeled as owner, repoName
    records = collection.find()

    #   generate output tables:
    day_list = ['Sun','Mon','Tue','Wed','Thur','Fri','Sat']

    #   output table df_weekly_commits
    df_weekly_commits = pd.DataFrame()

    #   position in the loop
    position = 0

    #   content, index
    #   go through records in Stats_w_commit_act, each giving back the history of commit_act
    for items in records:
        #   indicate which repo it is
        thisOwner = items['owner']
        thisRepo = items['repo']

        #   capture commits history of a particular repo
        #   days value represents the number of commits in order
        #   Starting on Sunday

        df_2 = pd.DataFrame(list(items['content']))

        #   extract commits value into columns with a particular day header assotiated

        df_days = pd.DataFrame(list(df_2['days']))
        df_days.columns = day_list
        df_days

        df_days = pd.concat([df_2, df_days], axis=1)
        df_days = df_days.drop('days', axis=1)
        #   combine index to df_days
        df_days['owner'] = thisOwner
        df_days['repo'] = thisRepo

        #   insert into Table df_weekly_commits
        df_weekly_commits = df_weekly_commits.append(df_days)

        print(str(position))
        position += position

    #   loop ended

    #   return Table df_weekly_commits
    ###   total        week  Sun  Mon  Tue  Wed  Thur  Fri  Sat     owner       repo
    ###      14  1442707200    0   11    1    1     0    1    0    jquery  jquery-ui

    #   print out nrow and ncol
    number_of_row = len(df_weekly_commits)
    number_of_col = len(list(df_weekly_commits))

    print("df_weekly_commits:\nNumber of rows : " + str(number_of_row) + "\nNumber of cols: " + str(number_of_col))

    conn.close()                               # close connection with MongoDB
    return df_weekly_commits

    ###   function convert_Stats_w_commit_act has been defined
    ########################################################################





#   ddl    for     db.Stats_w_freq               <==     Table 3
###   Get the number of additions and deletions per week
###   week, # of additions, # of deletions

def convert_Stats_w_freq(db_url, db_name):
    conn = MongoClient(db_url)                #   init mongodb client
    db = conn[db_name]                        #   build conn to local database 'sample_data'
    #   identify the table you in database: Stats_w_freq
    collection = db.Stats_w_freq

    #   get all records in table_3  Stats_w_freq
    #   for sample data, returns 10 records, each for a particular repositary labeled as owner, repoName
    records = collection.find()


    #   generate output tables:
    col_list = ['week','num_of_additions','num_of_deletions']

    #   output table df_Stats_w_freq
    df_Stats_w_freq = pd.DataFrame()

    #   position in the loop
    position = 0

    #   content, index
    #   go through records in df_Stats_w_freq, each giving back the history of weekly additions and deletions
    for items in records:
        #   indicate which repo it is
        thisOwner = items['owner']
        thisRepo = items['repo']

        #   capture commits history of a particular repo
        #   days value represents the number of commits in order
        #   Starting on Sunday

        df = pd.DataFrame(list(items['content']))

        df.columns = col_list
        df['owner'] = thisOwner
        df['repo'] = thisRepo

        df_Stats_w_freq = df_Stats_w_freq.append(df)


        print(str(position))
        position += 1

    #   loop ended

    #   return Table df_Stats_w_freq
    ###         week     num_of_additions    num_of_deletions   owner       repo
    ###   1211068800                19107               -4351  lebinh     ngxtop

    #   print out nrow and ncol
    number_of_row = len(df_Stats_w_freq)
    number_of_col = len(list(df_Stats_w_freq))

    print("df_Stats_w_freq:\nNumber of rows : " + str(number_of_row) + "\nNumber of cols: " + str(number_of_col))

    conn.close()                               # close connection with MongoDB
    return df_Stats_w_freq

    ###   function convert_Stats_w_commit_act has been defined
    ########################################################################




#   ddl    for     db.Stats_52w_cmmt               <==   Table 4
###   Get the weekly commit count for the repository owner and everyone else
###   all, owner

def convert_Stats_52w_cmmt(db_url, db_name):
    conn = MongoClient(db_url)                #   init mongodb client
    db = conn[db_name]                        #   build conn to local database 'sample_data'
    #   identify the table you in database: Stats_52w_cmmt
    collection = db.Stats_52w_cmmt

    #   get all records in table_4  Stats_52w_cmmt
    #   for sample data, returns 10 records, each for a particular repositary labeled as owner, repoName
    records = collection.find()

    #   generate output tables:
    df = pd.DataFrame()

    #   output table df_Stats_w_freq
    df_Stats_52w_cmmt = pd.DataFrame()

    #   position in the loop
    position = 0

    #   content, index
    #   go through records in df_Stats_w_freq, each giving back the history of weekly additions and deletions
    for items in records:
        #   indicate which repo it is
        thisOwner = items['owner']
        thisRepo = items['repo']

        #   capture commits history of a particular repo
        #   history # of commits in last 52 weeks
        #   the order of records should be ascending sequece, which can't be promised due to lack of info

        df['all_commits'] = items['content']['all']
        df['owner_commits'] = items['content']['owner']
        df['owner'] = thisOwner
        df['repo'] = thisRepo

        df_Stats_52w_cmmt = df_Stats_52w_cmmt.append(df)

        print(str(position))
        position += 1

    #   loop ended

    #   return Table df_Stats_52w_cmmt
    ###       all_commits  owner_commits       owner       repo
    ###                 0              0      lebinh     ngxtop

    #   print out nrow and ncol
    number_of_row = len(df_Stats_52w_cmmt)
    number_of_col = len(list(df_Stats_52w_cmmt))

    print("df_Stats_52w_cmmt:\nNumber of rows : " + str(number_of_row) + "\nNumber of cols: " + str(number_of_col))

    conn.close()                               # close connection with MongoDB
    return df_Stats_52w_cmmt

    ###   function convert_Stats_52w_cmmt has been defined
    ########################################################################





#   ddl    for     db.Stats_day_hr_com               <==   Table 5
###   Get the number of commits per hour in each day
###   0-6: Sunday - Saturday
###   0-23: Hour of day
###   Number of commits

def convert_Stats_day_hr_com(db_url, db_name):
    conn = MongoClient(db_url)                #   init mongodb client
    db = conn[db_name]                        #   build conn to local database 'sample_data'
    #   identify the table you in database: Stats_52w_cmmt
    collection = db.Stats_day_hr_com

    #   get all records in table_5  Stats_day_hr_com
    #   for sample data, returns 10 records, each for a particular repositary labeled as owner, repoName
    records = collection.find()

    #   generate output tables:
    df = pd.DataFrame()
    col_list = ['day_of_week','hour_of_day', 'num_of_commits']

    #   output table df_Stats_w_freq
    df_Stats_day_hr_comt = pd.DataFrame()

    #   position in the loop
    position = 0

    #   content, index
    #   go through records in df_Stats_w_freq, each giving back the history of weekly additions and deletions
    for items in records:
        #   indicate which repo it is
        thisOwner = items['owner']
        thisRepo = items['repo']

        #   capture commits history of a particular repo
        #   history # of commits in each hour buckets

        df = pd.DataFrame(list(items['content']))
        df.columns = col_list
        df['owner'] = thisOwner
        df['repo'] = thisRepo

        df_Stats_day_hr_comt = df_Stats_day_hr_comt.append(df)

        print(str(position))
        position += 1

    #   loop ended

    #   return Table df_Stats_day_hr_comt
    ###    day_of_week  hour_of_day  num_of_commits     owner       repo
    ###              5           18              48    lebinh     ngxtop

    #   print out nrow and ncol
    number_of_row = len(df_Stats_day_hr_comt)
    number_of_col = len(list(df_Stats_day_hr_comt))

    print("df_Stats_day_hr_comt:\nNumber of rows : " + str(number_of_row) + "\nNumber of cols: " + str(number_of_col))

    conn.close()                               # close connection with MongoDB
    return df_Stats_day_hr_comt

    ###   function convert_Stats_w_commit_act has been defined
    ########################################################################


##########################################################################
###                   convert unix times to dates                      ###
##########################################################################
###   Table 1:   df_stat_repo_main
###   convert_Stats_w_all_commits(db_url, db_name)
x,y,z = convert_Stats_w_all_commits(db_url, db_name)

#   transform a hierarchical index into data frame
# df = x.add_suffix('_Count').reset_index()
df = x.reset_index()
time_stamp_col = 'w'

#   convert unix timestamp
df_stat_repo_main = convertDate(df,time_stamp_col)

###   write into csv files
df_stat_repo_main.to_csv('df_stat_repo_main.csv', sep=',')



###   df_stat_repo_main  finished
###############################################################




#############################################
#   df_contibution_his
time_stamp_col = 'w'

df_contibution_his = convertDate(z,time_stamp_col)

###   write into csv files
df_contibution_his.to_csv('df_contibution_his.csv', sep=',')

############################################

#   df_contibution_his
df_contributor_main = y


###   write into csv files
df_contibution_his.to_csv('df_contibution_his.csv', sep=',')









#####################################################################
###   Table 2:   df_weekly_commits
###   convert_Stats_w_commit_act(db_url, db_name)
x = convert_Stats_w_commit_act(db_url, db_name)
time_stamp_col = 'week'

#   convert unix timestamp
df_weekly_commits = convertDate(x,time_stamp_col)

###   write into csv files
df_weekly_commits.to_csv('df_weekly_commits.csv', sep=',')




###   df_weekly_commits  finished
###############################################################



#####################################################################
###   Table 3:   df_Stats_w_freq
###   convert_Stats_w_freq(db_url, db_name)
df_Stats_w_freq = convert_Stats_w_freq(db_url, db_name)


###   write into csv files
df_Stats_w_freq.to_csv('df_Stats_w_freq.csv', sep=',')


###   df_Stats_w_freq  finished
###############################################################




#####################################################################
###   Table 4:   df_Stats_52w_cmmt
###   convert_Stats_52w_cmmt(db_url, db_name)
df_Stats_52w_cmmt = convert_Stats_52w_cmmt(db_url, db_name)


###   write into csv files
df_Stats_52w_cmmt.to_csv('df_Stats_52w_cmmt.csv', sep=',')

###   df_Stats_52w_cmmt  finished
###############################################################



#####################################################################
###   Table 5:   df_Stats_day_hr_comt
###   convert_Stats_day_hr_com(db_url, db_name)
df_Stats_day_hr_comt = convert_Stats_day_hr_com(db_url, db_name)


###   write into csv files
df_Stats_day_hr_comt.to_csv('df_Stats_day_hr_comt.csv', sep=',')
###   df_Stats_day_hr_comt  finished
###############################################################







