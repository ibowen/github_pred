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
    SECONDS_ONE_YEAR = 365 * 24 * 3600
    STAR_THRESHOLD = 100    
    NUM_REPOS = 0    

    def __init__(self):
       # logging.basicConfig(filename = self.LOG_FILE, level = logging.DEBUG)
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

            filename = '.'.join(params) + '.json'
            self.write_json(filename, response.json())
            total_pages = 1            

            print links
            if next_page and ('next' in links):                
                total_pages = self.process_pages(links, filename)
            
            print "Total pages = %d" % total_pages        

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

    def sample_repo(self):
        g = Github(login_or_token=self.USERNAME, password=self.PASSWORD, per_page=30)        
        with open('repositories.csv', 'ab') as f:
            writer = csv.writer(f)
            now = datetime.datetime.now()
            for repo in g.get_repos():
                try:
                    print repo.id, repo.name, repo.stargazers_count, repo.created_at.strftime("%Y-%m-%d %H:%M:%S"), repo.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                    writer.writerow([repo.id, repo.name, repo.stargazers_count, repo.created_at, repo.updated_at])                    
                    # if repo.stargazers_count > self.STAR_THRESHOLD and (now - repo.updated_at).total_seconds > self.SECONDS_ONE_YEAR / 4:
                    #     writer.writerow([repo.id, repo.name, repo.stargazers_count, repo.created_at, repo.updated_at])                    
                    #     self.NUM_REPOS = self.NUM_REPOS + 1
                    #     # logging.debug(self.NUM_REPOS)
                    #     print self.NUM_REPOS

                    # if self.NUM_REPOS > 1000:
                    #     break

                    time.sleep(1)

                except BadCredentialsException:
                    print "BadCredentialException occurred..."
                    sys.exit(1)

                except RateLimitExceededException:
                    print "RateLimitExceedException occurred..."                    
                    continue                

                except GithubException:
                    print "Unknwon Exception occurred, skip on this one."                    
                    continue

    def get_organizations(self):
        headers = {'Authorization' : 'token {}'.format(self.TOKEN)}
        # GET /organizations
        params = ['organizations']                
        self.github_request(params, headers, per_page=100, show_body=True, show_header=True)        
        


if __name__ == '__main__':    
    Base().get_organizations()
