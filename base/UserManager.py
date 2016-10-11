from github import Github
from github.GithubException import GithubException, RateLimitExceededException, BadCredentialsException
from os.path import dirname, abspath
import csv
import datetime
import os
import time
import logging
import sys
import json
import simplejson
import requests
import re
import pprint

from base import Base


class UserManager:
    TOKEN = ''
    ROOT_DIR = dirname((dirname(abspath(__file__))))
    LOG_FILE = ''

    def __init__(self, token, log_file):
        self.TOKEN = token
        self.LOG_FILE = os.path.join(self.ROOT_DIR, 'log/' + log_file)        
        logging.basicConfig(filename = self.LOG_FILE, level = logging.DEBUG)    
        
    # divide user list to 10 pieces
    def divide(self):
        num_chunks = 10
        user_list = []
        filepath = os.path.join(self.ROOT_DIR, 'data/unique_users.csv')
        print filepath
        header = True
        with open(filepath, 'rb') as f:
            reader = csv.reader(f)
            if header:
                next(reader)

            for line in reader:                
                user_list.append((line[0], line[1]))

        total_number = len(user_list)
        chunk_size = total_number / num_chunks        

        print total_number
        print chunk_size

        for i in range(num_chunks):
            filepath = os.path.join(self.ROOT_DIR, ('data/unique_users-%d' % i) + '.csv')
            with open(filepath, 'wb') as f:
                writer = csv.writer(f)
                start = i * chunk_size
                end = total_number if i * chunk_size + chunk_size - 1 > total_number else i * chunk_size + chunk_size - 1
                
                print start, end
                while start <= end:
                    writer.writerow(user_list[start])
                    start = start + 1
        
    def load_user_list(self, chunk_num):
        user_list = []
        filepath = os.path.join(self.ROOT_DIR, ('data/unique_users-%d' % chunk_num) + '.csv')
        with open(filepath, 'rb') as f:
            reader = csv.reader(f)
            for line in reader:
                user_list.append(line)

        return user_list


    def get_user_by_login(self, chunk_num, last_user_id):
        user_list = self.load_user_list(chunk_num)
        outputFile = os.path.join(self.ROOT_DIR, ('data/user_output-%d' % chunk_num) + '.csv')
        g = Github(login_or_token=self.TOKEN, per_page=100)

        logging.debug("%s: Starting program..." % datetime.datetime.now())
        row_num = 0

        skip = False

        with open(outputFile, 'ab') as f:
            writer = csv.writer(f)
            writer.writerow(['id','login','company','type','followers','following','location','public_repos','public_gists','created_at'])
            
            for user_info in user_list:
                try:
                    user_login = user_info[0]
                    user_id = user_info[1]                    
                    row_num = row_num + 1

                    print row_num, user_id, user_login                

                    # if int(user_id) == int(last_user_id):
                    #     skip = False

                    if not skip:
                        # user = g.get_user(user_login)                        
                        # writer.writerow([user_id, user_login, unicode(user.company).encode("utf-8"), user.type, \
                        #     user.followers, user.following, unicode(user.location).encode("utf-8"), user.public_repos, user.public_gists, user.created_at])
                        
                        user = Base(self.TOKEN).get_user(user_login)
                        if user != None:
                            writer.writerow([user_id, user_login, unicode(user['company']).encode("utf-8"), user['type'], \
                                user['followers'], user['following'], unicode(user['location']).encode("utf-8"), user['public_repos'], user['public_gists'], \
                                user['created_at']])

                            logging.debug("id: %s, %s" % (user_id, user_login))                                                
                            time.sleep(0.5)                        
                
                except Exception as e:
                    print "Unknwon Exception occurred, skip on this one."                    
                    logging.debug("Unknwon Exception occurred, user id = %s, user login = %s." % (user_info[1], user_info[0]))
                    continue

if __name__ == '__main__':
    token = '822f67e75e3b8986c463365320b7d4482850aef6'
    chunk_num = 9
    last_user_id = 5578201
    log_file = ('userlog-%d' % chunk_num) + '.log'
    UserManager(token, log_file).get_user_by_login(chunk_num, last_user_id)


