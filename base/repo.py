from github import Github
from github.GithubException import GithubException
import csv
import datetime
import os


class Repositories:
    TOKEN = '88499ecd36055ebd7976f72cc3d6369b6fd49c40'
    SECONDS_ONE_YEAR = 365 * 24 * 3600
    STAR_THRESHOLD = 100    
    NUM_REPOS = 0

    def __init__(self):
        pass

    def sample_repo(self):
        g = Github(self.TOKEN)        
        with open('repositories.csv', 'ab') as f:
            writer = csv.writer(f)
            now = datetime.datetime.now()
            for repo in g.get_repos():
                try:
                    print repo.id, repo.name, repo.stargazers_count, repo.created_at.strftime("%Y-%m-%d %H:%M:%S"), repo.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                    if repo.stargazers_count > self.STAR_THRESHOLD and (now - repo.updated_at).total_seconds > self.SECONDS_ONE_YEAR / 4:
                        writer.writerow([repo.id, repo.name, repo.stargazers_count, repo.created_at, repo.updated_at])                    
                        self.NUM_REPOS = self.NUM_REPOS + 1
                        print self.NUM_REPOS

                    if self.NUM_REPOS > 1000:
                        break

                except GithubException:
                    print "Exception occurred, continuing..."            
                    continue
        


if __name__ == '__main__':    
    Repositories().sample_repo()