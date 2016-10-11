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

class RepositoryManager:
    TOKEN = ''
    SECONDS_ONE_YEAR = 365 * 24 * 3600        

    def __init__(self, token):
        self.TOKEN = token

    def load_organizaitons(self):
        orgs = []
        with open('organizations-list.csv', 'rb') as f:
            reader = csv.reader(f)
            for line in reader:
                orgs.append(line[0])

        return orgs

    def get_org_repos(self):
        orgs = self.load_organizaitons()
        g = Github(login_or_token=self.TOKEN, per_page=100)
        
        with open('repos.csv','wb') as f:
            now = datetime.datetime.now()

            writer = csv.writer(f)
            writer.writerow(['org_id','repo_id','name','full_name','fork','forks_count','size','has_issues','has_wiki', \
                                'language','stargazers_count','watchers_count','created_at','updated_at','homepage'])            
            for org in orgs:
                try:            
                    organization = g.get_organization(org)
                    for repo in organization.get_repos():
                        print repo.id, repo.name, repo.homepage
                        if repo.fork == False and repo.stargazers_count > 100 and (now - repo.updated_at).total_seconds > self.SECONDS_ONE_YEAR / 12:
                                writer.writerow([org, repo.id, repo.name, repo.full_name, repo.fork, repo.forks_count, repo.size, repo.has_issues, repo.has_wiki, \
                                    repo.language, repo.stargazers_count, repo.watchers_count, repo.created_at, repo.updated_at, repo.homepage])

                                # time.sleep(0.5)

                except RateLimitExceededException:
                    print "RateLimitExceedException occurred..."
                    time.sleep(1800)                    
                    continue                

                except BadCredentialsException:
                    print "BadCredentialException occurred..."
                    sys.exit(1)

                except GithubException:
                    print "Unknwon Exception occurred, skip on this one."                    
                    sys.exit(1)              
                            
if __name__ == '__main__':
    access_token = ''
    RepositoryManager(access_token).get_org_repos()