from pymongo import MongoClient
import time
import random
import re
import sys
from datetime import datetime

def report(user_id, posts, votes):
    """If a user id is provided, the user will be shown a report that includes
    (1) the number of questions owned and the average score for those questions,
    (2) the number of answers owned and the average score for those answers, and
    (3) the number of votes registered for the user.
    Input: user_id: - Determine if the user_id is provide the report is shown
            posts - posts collection to access the data
            votes - votes collection to access the data
    Output: None"""

    # Find all the posts that are questions
    questions = posts.find({"$and": [{"PostTypeId": "1"}, {"OwnerUserId": user_id}]})
    # Find all the posts that are answers
    answers = posts.find({"$and": [{"PostTypeId": "2"}, {"OwnerUserId": user_id}]})
    # Find all the votes with user_id
    vote = votes.find({"UserId": user_id})

    # Count the number of questions owned and the average score for those questions
    num_questions = 0
    total_score_questions = 0
    for ques in questions:
        num_questions += 1
        total_score_questions += int(ques["Score"])
    try:
        score_questions = total_score_questions / num_questions #In case there are no questions
    except:
        score_questions = 0
    print("The user has " + str(num_questions) + " questions with the average score of those questions is " + str(score_questions) + ". ")

    # Count the number of answers owned and the average score for those answers
    num_answers = 0
    total_score_answers = 0
    for ans in answers:
        num_answers += 1
        total_score_answers += int(ans["Score"])
    try:
        score_answers = total_score_answers / num_answers #In case there are no answers
    except:
        score_answers = 0
    print("The user has " + str(num_answers) + " answers with the average score of those questions is " + str(score_answers) + ". ")

    # Count the number of votes registered for the user
    num_votes = 0
    for item in vote:
        num_votes += 1
    print("The number of votes registered for the user: " + str(num_votes))

def post_question(user_id, myposts, mytags):
    """ The user should be able to post a question by providing 
    a title text, a body text, and zero or more tags 
    Input: user_id - if they provides the user_id allow it to insert in the document if not then None
            myposts - post collection to access the data
            mytags - tag collection to access the data"""

    # The post creation date should be set to the current date
    current_date = datetime.now().isoformat()

    # Prompt the user to enter the title, body, and tags of the question
    title = input("Enter the title: ")
    title = title.lower()
    body = input("Enter the body: ")
    body = body.lower()
    
    # Prompt the user to enter tags
    tags_list = []
    flag = True
    while flag:
        num = input("How many tags you want to enter? ")
        #check if the user enters the digit
        if num.isdigit():
            flag = False
        else:
            print("Invalid", end= '')
    
    for i in range(int(num)):
        tag = input("Enter tag number " + str(i + 1) + ": ")
        tag = tag.lower()
        tags_list.append(tag)

    tag = "" 
    # if the user does not enter any tag, set tag to None
    if len(tags_list) == 0:
        tag = None

    # formatting the tag
    for item in tags_list:
        tag += ("<" + item + ">")

    for t in tags_list:
        # Random tag id
        flag = True
        tag_id = random.randint(0, 1000000000000)
        while flag:
            tag_id += 1
            result = mytags.find({"Id": str(tag_id)})
            try:
                result[0]
            except:
                flag = False
            else:
                flag = True

        # Check whether the tag existed or not
        result = mytags.find({"TagName": t}).collation({"locale": 'en', "strength": 1})
        for item in result:
            try:
                item
            except:
                tag_insert = [
                    {
                        "Id": str(tag_id),
                        "TagName": t,
                        "Count": 1
                    }
                ]
                mytags.insert_many(tag_insert)
            else:
                mytags.update_many(
                    {"Id": item["Id"]},
                    {"$inc": {"Count": 1}}
                )

    # Random the post id and check whether it exists
    flag1 = True
    post_id = random.randint(0, 1000000000)
    while flag1:
        post_id += 1
        result1 = myposts.find({"Id": str(post_id)})
        try:
            result1[0]
        except:
            flag1 = False
        else:
            flag1 = True

    # If the user do not provide the user id, the OwnerUserId will be set to None
    # The quantities Score, ViewCount, AnswerCount, CommentCount, and FavoriteCount are all set to zero
    # The content license is set to "CC BY-SA 2.5"

    if user_id is not None:
        question = [
            {
                "Id": str(post_id),
                "PostTypeId": "1",
                "CreationDate": str(current_date),
                "Score": 0,
                "ViewCount": 0,
                "Body": body,
                "OwnerUserId": user_id,
                "Title": title,
                "Tags": tag,
                "AnswerCount": 0,
                "CommentCount": 0,
                "FavouriteCount": 0,
                "ContentLicense": "CC BY-SA 2.5"
            }
        ]
    else:
        question = [
            {
                "Id": str(post_id),
                "PostTypeId": "1",
                "CreationDate": str(current_date),
                "Score": 0,
                "ViewCount": 0,
                "Body": body,
                "OwnerUserId": None,
                "Title": title,
                "Tags": tag,
                "AnswerCount": 0,
                "CommentCount": 0,
                "FavouriteCount": 0,
                "ContentLicense": "CC BY-SA 2.5"
            }
        ]

    # insert the question to the database
    myposts.insert_many(question)

def search_questions(posts):
    """The user should be able to provide one or more keywords,
    and the system should retrieve all posts that contain at least
    one keyword either in title, body, or tag fields
    Input: posts - post collection to access the data
    Output: None (if the user want to perform search) or question (if the user want to perform the question action) """

    # create the list of all keyword provided by user
    keyword_list1 = [] #Keyword with length is less than 3
    keyword_list2 = [] #Keyword with length is equal or greater than 3

    flag = True
    while flag:
        check = True
        keyword = input("Enter the keyword you are looking for in the post: ")
        keyword = keyword.lower()

        # If the user enter the keyword that already existed in the program
        if keyword not in keyword_list1 and len(keyword) < 3:
            keyword_list1.append(keyword)

        elif keyword not in keyword_list2 and len(keyword) >= 3:
            keyword_list2.append(keyword)
        else:
            print("You enter the keyword that already existed. ")
            check = False
        while check:
            # Check if the user wants to enter more keywords.
            flag1 = input("If you want to continue to enter keyword, press y: ")
            flag1 = flag1.lower()

            if flag1 == "y":
                flag = True
                check = False
            else:
                flag = False
                check = False

            # If the keyword_list is empty, not allow the user to continue
        if len(keyword) == 0:
            print("You do not provide any keywords. Please try again")
            flag = True
            keyword_list1 = []
            keyword_list2 = []
    
    #List of posts that contains the keyword less than 3
    posts_contain_keywords1 = []

    #Create the index to support the search for keyword which has length less than 3
    posts.create_index("Body")
    posts.create_index("Tags")
    posts.create_index("Title")

    for key in keyword_list1:
        result = posts.find({"$and": [{"PostTypeId": "1"}, {
            '$or': [{"Title": {"$regex": key, "$options": "-i"}}, {"Body": {"$regex": key, "$options": "-i"}}, {"Tags": {"$regex": key, "$options": "-i"}}]}]})
        try:
            for item in result:
                posts_contain_keywords1.append(item)
        except:
            continue

    #List of posts that contains the keyword equal or greater than 3
    posts_contain_keywords2 = []
    for key in keyword_list2:
        result = posts.find({"$and": [{"PostTypeId": "1"}, {"Terms": key}]})
        try:
            for item in result:
                posts_contain_keywords2.append(item)
        except:
            continue

    #List to contains all the post from keyword 1 and keyword 2
    posts_contain_keywords = []
    for post in posts_contain_keywords1:
        if post not in posts_contain_keywords:
            posts_contain_keywords.append(post)
    
    for post in posts_contain_keywords2:
        if post not in posts_contain_keywords:
            posts_contain_keywords.append(post)

    # display the title, the creation date, the score, and the answer count
    if len(posts_contain_keywords) == 0:
        print("There are no questions with provided keyword.")
        return None
    else: 
        for item in posts_contain_keywords:
            print(item['Id'] + ' | ' + item['Title'] + ' | ' + item['CreationDate'] + ' | ' + str(item['Score']) + ' | ' + str(item['AnswerCount']))

    #Ask the user if they want to select one question to see all the field
    flag1 = True
    while flag1:
        option = input("Do you want to see all field of one question (y/n): ")
        option = option.lower()
        if option == 'y':
            flag1 = False
        elif option == 'n':
            return None
        else:
            print("Wrong option", end='')

    #If the user ask choose to see 1 question to see all field, ask them to perform question_action
    check = True
    while check:
        question = input("Select a question id to see all fields of it: ")
        for item in posts_contain_keywords:
            if question == item["Id"]:
                posts.update(
                    {"Id": question},
                    {"$inc": {"ViewCount": 1}}
                )
                print(item)
                check = False
        if check:
            print("Your input is not in the list. Please select again!")

    return question

def answer(user_id, posts, question_id):
    """The user should be able to answer the question by providing a text. 
    Input: user_id: use to insert into the document if the current user decides to provide
            posts: post collection
            question_id: to know which question they want to answer
    Output: None"""

    current_date = datetime.now().isoformat()  # Format of the creationdate

    # Ask the user to provide the text:
    body = input("Enter the answer: ")
    body = body.lower()

    # Random the post id and check whether it exists
    flag = True
    post_id = random.randint(0, 10000000000000)
    while flag:
        post_id += 1
        result = posts.find({"Id": str(post_id)})
        try:
            result[0]
        except:
            flag = False
        else:
            flag = True

    # How do we handle if there are no "acceptedAnsweredId", do we need to include it in the insertion and put None.
    # An answer record should be inserted into the database, with body field set to the provided text.
    # A unique id should be assigned to the post by your system, the post type id should be set to 2.
    # The post creation date should be set to the current date.
    # The owner user id should be set to the user posting it.
    # The parent id should be set to the id of the question.
    # The quantities Score and CommentCount are all set to zero and the content license is set to "CC BY-SA 2.5".

    answer = [{"Id": str(post_id),
               "PostTypeId": "2",
               "CreationDate": str(current_date),
               "OwnerUserId": user_id,
               "ParentId": question_id,
               "Body": body,
               "Score": 0,
               "CommentCount": 0,
               "ContentLicense": "CC BY-SA 2.5"}]

    posts.insert_many(answer)

def list_answer(posts, question_id):
    """List all the answer that has parent id == qid
    For the answer has been marked as accepted answer for the qid, display 1st with the star
    Display the body (first 80 characters, creation date, score)
    Ask the user if they want to see all other information
    Ask the user if they want to perform answer action
    Input: posts - post collection to access the data
            question_id if the user wants to see the answer
    Output: return 'n', None (if there are no answers on the list_answer or the user does not want 
            to perform answer action) display (the answer id they want to vote in answer action)"""

    # Find the question with input id
    question = posts.find({"Id": question_id})

    # Find the list of answers that has been marked as an accepted answer for the question
    answer_list = posts.find({"$and": [{"PostTypeId": "2"}, {"ParentId": question_id}]})
    star = ""
    show_list = []
    check_list = []
    for item in answer_list:
        check_list.append(item)
        if question[0]["AcceptedAnswerId"] == item["Id"]:
            if len(item["Body"]) <= 80:
                star = "*" + item["Id"] + " | " + item["Body"] + " | " + item["CreationDate"] + " | " + str(item["Score"])
            else:
                star = "*" + item["Id"] + " | " + item["Body"][:81] + " | " + item["CreationDate"] + " | " + str(item["Score"])
        else:
            if len(item["Body"]) <= 80:
                show_list.append(" " + item["Id"] + " | " + item["Body"] + " | " + item["CreationDate"] + " | " + str(item["Score"]))
            else:
                show_list.append(" " + item["Id"] + " | " + item["Body"][:81] + " | " + item["CreationDate"] + " | " + str(item["Score"]))
    # print the accepted answer id first
    print(star)
    # print other result
    for post in show_list:
        print(post)

    # Check if there are any answers for given question
    if len(check_list) == 0:
        print("There are no answers for the given question")
        return None

    #Ask the user if they want to see all the field
    flag1 = True
    while flag1:
        option = input("Do you want to see all field of one answer (y/n): ")
        option = option.lower()
        if option == 'y':
            flag1 = False
        elif option == 'n':
            return None
        else:
            print("Wrong option", end='')

    # Ask the user if they want to see all the information
    display = input("Enter an answer id listed above to see all fields: ")
    display = display.lower()

    # Check the input and let the user see all the result
    flag = True
    while flag:
        for item in check_list:
            if item["Id"] == display:
                flag = False
        if flag:
            display = input("You entered an invalid answer id. Please try again: ")
            display = display.lower()

    #Print all the information of the post the user want to see
    final_result = posts.find({"Id": display})
    print(final_result[0])

    # Ask the user to perform an answer action
    flag = True
    option = input("Do you want to perform answer action (y/n): ")
    option = option.lower()
    while flag:
        if option == 'y':
            return display
        elif option == 'n':
            return 'n'
        else:
            option = input("Try again. Do you want to perform answer action (y/n): ")
            option = option.lower()

def vote(user_id, posts, votes, pid):
    """The user should be able to vote on the selected question or answer if not voted already on the same post.
    The vote should be recorded in Votes with a unique vote id assigned by your system,
    the post id set to the question/answer id, vote type id set to 2, and the creation date set to the current date.
    If the current user is not anonymous, the user id is set to the current user.
    With each vote, the score field in Posts will also increase by one"""

    # The post creation date should be set to the current date
    current_date = datetime.now().isoformat()

    # Check whether the user voted or not
    check = True
    while check and user_id is not None:
        check_vote = votes.find({"$and": [{"UserId": user_id}, {"PostId": pid}]})
        try:
            check_vote[0]
        except:
            check = False
        else:
            print("You have already voted for this post.")
            return None

    # Random the post id and check whether it exists
    flag = True
    vote_id = random.randint(0, 100000000000)
    while flag:
        vote_id += 1
        result = posts.find({"Id": str(vote_id)}).collation({"locale": 'en', "strength": 1})
        try:
            result[0]
        except:
            flag = False
        else:
            flag = True

    # Insert data into Votes
    if user_id is None:
        vote = [
            {
                "Id": str(vote_id),
                "PostId": pid,
                "VoteTypeId": "2",
                "CreationDate": str(current_date)
            }
        ]
    else:
        vote = [
            {
                "Id": str(vote_id),
                "PostId": pid,
                "VoteTypeId": "2",
                "UserId": user_id,
                "CreationDate": str(current_date)
            }
        ]

    votes.insert_many(vote)

    # update Posts with the score in crease by 1
    posts.update_one(
        {"Id": pid},
        {"$inc": {"Score": 1}}
    )

    print("You vote successfully")

def main():
    # Take port number
    port_number = str(sys.argv[1]).lower()

    # Handle port number if the server is busy
    try:
        client = MongoClient('mongodb://localhost:{}'.format(port_number))
    except:
        print("Port number is busy. Try again")
        return

    # Connect to a database named 291db
    db = client['291db']

    # Open the collection
    myposts = db["Posts"]
    mytags = db["Tags"]
    myvotes = db["Votes"]

    # ask the user if they wish to provide the id
    option = input("Do you want to provide the user id? (y/n) ")
    option = option.lower()
    flag = True
    while flag:
        if option == "y":
            user_id = input("Please enter an user id: ")
            report(user_id, myposts, myvotes)           #Display the report if the user decide yes
            flag = False
        elif option == "n":
            user_id = None
            flag = False
        else:
            option = input("Wrong option. Try again (y/n): ")
            option = option.lower()

    # Ask the user to provide post action
    check = True
    while check:
        #Ask the user to provide an action 
        menu = input("Post a question (1), Search for questions (2) and Exit (3): ")
        if menu == '1':
            post_question(user_id, myposts, mytags) #Post a question
        elif menu == '2':
            pid = search_questions(myposts) #Search for question 
            if pid != None:
                check1 = True               #If there is a question after the search ask them for question action
                while check1:
                    decision = input("Answer (1), List_answer (2), Vote (3): ")
                    if decision == '1':
                        answer(user_id, myposts, pid) #Answer the question and go back to the menu
                        check1 = False
                    elif decision == '2':
                        result = list_answer(myposts, pid) #List the answer for the question and ask for answer action
                        if result == 'n' or result == None:
                            check1 = False
                        else:
                            vote(user_id, myposts, myvotes, result) #If yes, vote for the post the user has asked
                            check1 = False
                    elif decision == '3':
                        vote(user_id, myposts, myvotes, pid) #Vote for a post in the search question
                        check1 = False
                    else:
                        print("Wrong option", end = '')
        elif menu == '3':                                   #Terminate the program
            check = False
        else:
            print('Wrong option.', end ='')


if __name__ == "__main__":
    main()

