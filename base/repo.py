from github import Github
from github.GithubException import GithubException, RateLimitExceededException, BadCredentialsException
import csv
import datetime
import os
import time
import logging
import sys


class Repositories:
    USERNAME = ''
    PASSWORD = ''
    SECONDS_ONE_YEAR = 365 * 24 * 3600
    STAR_THRESHOLD = 100    
    NUM_REPOS = 0    

    def __init__(self):
       # logging.basicConfig(filename = self.LOG_FILE, level = logging.DEBUG)
        pass

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
        


if __name__ == '__main__':    
    Repositories().sample_repo()
