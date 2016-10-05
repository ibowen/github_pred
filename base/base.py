from github import Github
from github.GithubException import GithubException, RateLimitExceededException, BadCredentialsException
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


class Base:    
    TOKEN = ''
    
    def __init__(self, token):
        self.TOKEN = token       
        pass

    def github_request(self, params, headers, per_page=30, page=1, show_header=False, show_body=False, next_page=True):
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
        response = requests.get(url, headers=headers) # get response
        links = []

        if response.headers['Status'] == '200 OK':                        
            if show_body:            
                print json.dumps(response.json(), indent=2)
                print '------------------------------------'

            if show_header:            
                for (k,v) in response.headers.items():
                    print k, "=>", v
                    if k == 'Link':
                        links = self.parse_link(v)                    
                print '------------------------------------'

            # filename = '.'.join(params) + '.json'
            # self.write_json(filename, response.json())
            total_pages = 1            
            
            if next_page and ('next' in links):                
                total_pages = self.process_pages(links, filename)
            
            # print "Total pages = %d" % total_pages
            return response.json()

        else:
            return None

    def parse_link(self, link_str):
        links = {}
        link_list = link_str.split(',')           

        for item in link_list:
            matchObj = re.match(r'<(.*)>.*rel="(.*)"', item.strip(), re.I|re.M)            
            if matchObj:
                url = matchObj.group(1)
                rel = matchObj.group(2)
                
            links[rel] = url

        return links            

    def write_json(self, filename, data):
        with open(filename, 'ab') as f:
            f.write(json.dumps(data, indent = 2))

    def navigateTo(self, link):
        if link != None:
            response = requests.get(link)
        return response
                    
    def process_pages(self, links, filename):
        total_pages = 1        
        
        while links != None and ('next' in links):                        
            response = self.navigateTo(links['next'])            
            print response.headers['Status']

            if response.headers['Status'] == '200 OK':
                self.write_json(filename, response.json())
                for (k,v) in response.headers.items():                    
                    if k == 'Link':
                        links = self.parse_link(v)
                        break

                total_pages = total_pages + 1
                
                print total_pages
                print links

            elif response.headers['Status'] == '403 Forbidden':
                break;

        return total_pages

    # GET /organizations
    def get_public_organizations(self):
        headers = {'Authorization' : 'token {}'.format(self.TOKEN)}
        
        params = ['organizations']                
        self.github_request(params, headers, per_page=100, show_body=True, show_header=True)

    # GET /users/:username
    def get_user(self, username):
        headers = {'Authorization' : 'token {}'.format(self.TOKEN)}
        params = ['users', username]
        response = self.github_request(params, headers, per_page=30, show_body=False, show_header=False)
        return response

        