import csv
import os
from os.path import dirname, abspath


def loadUserWeights():
    ROOT_DIR = dirname((dirname(abspath(__file__))))
    file = os.path.join(ROOT_DIR, 'data/user_weights.csv')
    header = True
    row_num = 1

    weights = {}

    with open(file, 'rb') as f:
        reader = csv.reader(f)
        if header:
            next(reader)

        for row in reader:
            user_id = int(row[0])
            weight_by_follower = float(row[-2])
            weight_by_repo = float(row[-1])
            weight_combine = (weight_by_follower + weight_by_repo) / 2

            weights[user_id] = (weight_by_follower, weight_by_repo, weight_combine)            
            row_num = row_num + 1            
            
    return weights
            
def calRepoWeights():
    ROOT_DIR = dirname((dirname(abspath(__file__))))
    file = os.path.join(ROOT_DIR, 'data/starrings_full.csv')
    header = True
    row_num = 1

    user_weights = loadUserWeights()
    repo_weights = {}
    
    with open(file, 'rb') as f:
        reader = csv.reader(f)
        if header:
            next(reader)

        for row in reader:
            repo_login = row[1]
            user_id = row[6]

            if user_id in user_weights:
                weight_by_follower = user_weights[user_id][0]
                weight_by_repo = user_weights[user_id][1]
                weight_combine = user_weights[user_id][2]
            else:
                continue

            if repo_login in repo_weights:
                repo_weights[repo_login][0] = repo_weights[repo_login][0] + weight_by_follower
                repo_weights[repo_login][1] = repo_weights[repo_login][1] + weight_by_repo
                repo_weights[repo_login][2] = repo_weights[repo_login][2] + weight_combine
                repo_weights[repo_login][3] = repo_weights[repo_login][3] + 1

            else:
                repo_weights[repo_login] = [weight_by_follower,weight_by_repo,weight_combine,1]

            print repo_login, repo_weights[repo_login]

            row_num = row_num + 1
            

    output_file = os.path.join(ROOT_DIR, 'data/repo_weights.csv')
    with open(output_file, 'ab') as f:
        writer = csv.writer(f)

        for repo in repo_weights:
            writer.writerow([repo, repo_weights[repo][0], repo_weights[repo][1], repo_weights[repo][2], repo_weights[repo][3]])

def calRepo2RepoWeights():
    ROOT_DIR = dirname((dirname(abspath(__file__))))
    input_file = os.path.join(ROOT_DIR, 'data/repo_repo_users.csv')    
    row_num = 1

    user_weights = loadUserWeights()    

    edges = []

    with open(input_file,'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            from_repo = row[0]
            to_repo = row[1]

            # no common user
            if row[2][1:-1] == '':
                total_weight_by_follower = 0                
                total_weight_by_repo = 0
                total_weight_combine = 0
                num_common_users = 0

            else:
                user_list = row[2][1:-1].split(',')            
                total_weight_by_follower = 0
                total_weight_by_repo = 0
                total_weight_combine = 0
                num_common_users = len(user_list)

                for user_id in user_list:                    
                    user_id = int(user_id)
                    if user_id in user_weights:
                        weight_by_follower = user_weights[user_id][0]
                        weight_by_repo = user_weights[user_id][1]
                        weight_combine = user_weights[user_id][2]
                        
                        total_weight_by_follower = total_weight_by_follower + weight_by_follower
                        total_weight_by_repo = total_weight_by_repo + weight_by_repo
                        total_weight_combine = total_weight_combine + weight_combine


            edge = [from_repo, to_repo, total_weight_by_follower, total_weight_by_repo, total_weight_combine, num_common_users]
            edges.append(edge)
            print edge
            
            row_num = row_num + 1
            # if row_num > 100:
            #     break

    output_file = os.path.join(ROOT_DIR, 'data/repo_repo_weights.csv')
    with open(output_file, 'ab') as f:
        writer = csv.writer(f)
        for edge in edges:
            writer.writerow(edge)

    return row_num
            

if __name__ == "__main__":
    # loadUserWeights()
    # calRepoWeights()
    calRepo2RepoWeights()
