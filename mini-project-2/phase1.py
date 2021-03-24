import pandas as pd
import time
import json
from pymongo import MongoClient
import sys
import re

def get_terms(body, title, tag):
    #post = posts.find() # the whole post collection    
    new_arr = []

    #Break down the list and remove the punctuation
    if body != "There is nothing":
        new_arr.extend(re.findall(r"[\w']+", body))
 
    if title != "There is nothing":
        new_arr.extend(re.findall(r"[\w']+", title))

    if tag != "There is nothing":
        new_arr.extend(re.findall(r"[\w']+", tag))
    
    #Remove the words with length less than 3 and lower the words
    new_arr = [keyword.lower() for keyword in new_arr if len(keyword) >= 3]
    
    #Remove the duplicates
    new_arr = list(set(new_arr))
    
    return new_arr


def main(): 
    
    #Preprocess the json file
    with open('Tags.json', 'r') as f:
        tag_data = json.load(f)
        tag_data = tag_data['tags']['row']

    with open('Votes.json', 'r') as f:
        vote_data = json.load(f)
        vote_data = vote_data['votes']['row']

    with open('Posts.json', 'r') as f:
        post_data = json.load(f)
        post_data = post_data['posts']['row']
    
    #Create the tag, vote and post dataframe
    tag_df = pd.DataFrame(tag_data)
    vote_df = pd.DataFrame(vote_data)
    post_df = pd.DataFrame(post_data)

    #Create the terms
    post_df.fillna("There is nothing", inplace = True)
    df = post_df.apply(lambda x: get_terms(x['Body'], x['Tags'], x['Title']),axis=1)
    post_df['Terms'] = df

    tag_df.reset_index(inplace=True)
    tag_dict = tag_df.to_dict("records")

    vote_df.reset_index(inplace=True)
    vote_dict = vote_df.to_dict("records")

    post_df.reset_index(inplace=True)
    post_dict = post_df.to_dict("records")
    
    #Create the client and access the database
    port_number = sys.argv[1]
    port_number = port_number.lower()  # prevent case sensitivity

    #Establish the connection
    try:
        client = MongoClient('mongodb://localhost:{}'.format(port_number))
    except:
        print("The connection is busy")

    #Create or open the database
    mydb = client["291db"]  

    collist = mydb.list_collection_names()  # list all the collection inside the database

    if "Posts" in collist:  # check if the Posts collection inside
        mydb["Posts"].drop()  # drop if have

    if "Tags" in collist:  # check if the Tags collection inside
        mydb["Tags"].drop()  # drop if have

    if "Votes" in collist:  # check if the Votes collection inside
        mydb["Votes"].drop()  # drop if have

    # create new colelctions for the database
    myposts = mydb["Posts"]
    mytags = mydb["Tags"]
    myvotes = mydb["Votes"]

    #insert to the database
    myvotes.insert_many(vote_dict)
    mytags.insert_many(tag_dict)
    myposts.insert_many(post_dict)

    #Create index for term array 
    myposts.create_index("Terms")   
    

if __name__ == "__main__":
    main()
