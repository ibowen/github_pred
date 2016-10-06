from pymongo import MongoClient
import pandas as pd
import logging
import os



logging.basicConfig(filename='starrings.log',level=logging.DEBUG)

def starring_etl(mongodb, coll_name):
    """ Description: function to flatten mongodb into dataframe
        @mongodb: mongodb database connection
        @coll_name: collection name
    """
    stars_list = [] # init a list to contain query result
    stars = mongodb[coll_name].find({}, {"_id":0, "starred_at": 1, "user.type": 1, "user.id":1, "user.login":1, "user.site_admin":1})
    for star in stars:
        names = coll_name.split('.')
        stars_list.append([names[1], '.'.join(names[2:-1])] + [star['starred_at']] + star['user'].values()) # append the flattened row
    # construct a dataframe
    stars_df = pd.DataFrame(stars_list, columns=['owner', 'repo', 'starred_at', 'user.login', 'user.site_admin', 'user.type', 'user.id'])
    logging.debug(coll_name)
    logging.debug(stars_df.shape)
    print coll_name, stars_df.shape
    
    return stars_df

def dump_starring(db_url, db_name):
    """ Description: function to dump all collections of mongo database into a csv file
        @db_url: mongodb url
        @db_name: mongodb database name
        @start_day: str, the day that the query starts from, ie. '2015-01-01'
    """
    mongocli = MongoClient(db_url)# init mongodb client
    mongodb = mongocli[db_name] # connect 'github' database
    coll_names = mongodb.collection_names() # get collection names
    
    for coll_name in coll_names: # loop collections
        # construct a dataframe
        stars_df = starring_etl(mongodb=mongodb, coll_name=coll_name)
        
        # write out csv
        file_name = 'data/starring.csv'
        if not os.path.isfile(file_name): # if file not exist, wirte column names
            stars_df.to_csv(file_name, index=False)
        else: # else it exists, not append colnames
            stars_df.to_csv(file_name, mode = 'a', header=False, index=False)
        logging.debug(coll_name + 'is completed...')
        print coll_name + 'is completed...'
        print '-------------------------------------------------'
        break
        
    mongocli.close()

def main():
    # mongodb configuration
    db_url = 'ec2-54-67-97-244.us-west-1.compute.amazonaws.com:27017'
    db_name = 'starrings'
    mongocli = MongoClient(db_url)# init mongodb client
    mongodb = mongocli[db_name] # connect 'github' database
    
    dump_starring(db_url, db_name)


if __name__ == '__main__':
    main()



