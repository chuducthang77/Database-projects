# ----------------------------------------------------
# Mini Project 1:
#
# Team member: Chu Duc Thang, Duong Hoang Son, Nguyen Minh Hoang
# ----------------------------------------------------


import sqlite3
import time
from getpass import getpass
import random
import sys

connection = None
cursor = None


def connect(path):
    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA forteign_keys=ON; ')
    connection.commit()
    return


def login_handle():
    '''
    Handle the login option by the user
    Input: None
    Output: user_id - return the user_id to determine how sign in the system
    '''
    global connection, cursor

    print('-'*40)
    print('Your login process begins')
    print('-'*40)

    # Ask for user id
    user_id = input("Please enter the user id: ")
    user_id = user_id.lower()  # prevent case sensitivity

    # Find the user id in the database
    data = (user_id,)
    cursor.execute('SELECT u.uid FROM users u WHERE u.uid = ?;', data)
    result = cursor.fetchone()

    # Check whether the user id is in the database, if not continously ask the user to enter
    flag = True
    while flag:
        if result == None:
            user_id = input(
                "The user id is invalid. Please enter the user id: ")
            user_id = user_id.lower()  # prevent case sensitivity
            data = (user_id,)
            cursor.execute('SELECT u.uid FROM users u WHERE u.uid = ?;', data)
            result = cursor.fetchone()
        elif result[0] != None:
            flag = False

    # If the user id is correct, ask the user for password
    # Make the password become invisible while enter in
    password = getpass("Please enter the password: ")
    cursor.execute('SELECT u.pwd FROM users u WHERE u.uid = ?;', data)
    result1 = cursor.fetchone()

    # Check whether the password is correct
    flag1 = True
    while flag1:
        if result1[0] != password:
            password = getpass(
                "The password is invalid. Please enter the password: ")
        else:
            flag1 = False

    # After successfully login in, display welcome message
    print("-"*40)
    print("Welcome to your account!!!")

    connection.commit()
    return user_id


def register_handle():
    '''
    Allow the new user to register new account into the system
    If they choose the account that already exist --> Ask them to enter the new one
    If the user id they choose is unique --> Ask the name, city and password
    Update the resgister date to the current date
    Update in the database
    Input: None
    Output: user_id - return the user_id to determine how sign in the system
    '''

    global connection, cursor

    current_date = time.strftime("%Y-%m-%d")

    print('-'*40)
    print('Your registration process begins')
    print('-'*40)

    # Ask the user to choose the user id
    user_id = input("Please choose an user id: ")
    user_id = user_id.lower()  # prevent case sensitivity

    # Check if the user is already existed in the database
    flag = True
    cursor.execute('SELECT u.uid FROM users u;')
    results = cursor.fetchall()

    while flag:
        check = True
        for item in results:
            if item[0] == user_id:
                check = False
        if not check:
            user_id = input(
                "The id you choose has been taken. Please choose a different user id: ")
            user_id = user_id.lower()  # prevent case sensitivity
            flag = True
        elif len(user_id) == 0:
            user_id = input(
                "You cannot have an empty id. Please choose an user id: ")
            user_id = user_id.lower()  # prevent case sensitivity
            flag = True
        elif len(user_id) > 4:
            user_id = input(
                "Your user id can not be more than four characters. Please choose a different user id: ")
            user_id = user_id.lower()  # prevent case sensitivity
            flag = True
        else:
            flag = False

    # If not, ask the user to enter name, city, password

    name = input("Please enter your name: ")
    name = name.lower()  # prevent case sensitivity

    city = input("Please enter your city: ")
    city = city.lower()  # prevent case sensitivity

    # Ask the user to enter the password, and check if the user
    flag1 = True
    while flag1:
        password = getpass("Please enter your password: ")
        if len(password) == 0:
            print("\nYou are not allowed to enter empty password. ", end='')
            flag1 = True
        else:
            flag1 = False

    # Update the value into the database
    data = (user_id, name, password, city, current_date)
    cursor.execute(
        'INSERT INTO users(uid, name, pwd, city, crdate) VALUES (?, ?, ?, ?, ?) ', data)

    # Message for successfully register an account
    print('-'*40)
    print("You successfully register in the database")

    connection.commit()
    return user_id


def post_question(user_id):
    '''
    Allow the user to post question
    Ask the user to provide title and body text
    poster will be update based on the user_id
    The pid will be given by the program
    The date is also given by the program
    Input: user_id - Determine who is the poster
    Output: None
    '''

    global connection, cursor

    current_date = time.strftime("%Y-%m-%d")

    # Ask the user to enter the title and body
    title = input("Enter the title of the question: ")
    title = title.lower()  # prevent case sensitivity

    body = input("Enter the body of the question: ")
    body = body.lower()  # prevent case sensitivity

    # Random choose the pid and check whether the pid is unique in the database. If not, keep increase the pid by 1 until it is unique
    flag = True
    id = random.randint(0, 9999)
    count = 0
    while flag != None:
        id = (id + 1) % 10000
        pid = str(id)
        cursor.execute(
            'select posts.pid from posts where posts.pid = ?', (pid,))
        flag = cursor.fetchone()
        count += 1

    # Check if the pid of system has been full
    if count == 9999:
        print("The system is full. You cannot have more posts.")
        return

    # Update to the database system
    data = (pid, current_date, title, body, user_id)
    cursor.execute(''' INSERT INTO posts(pid, pdate, title, body, poster) VALUES
	                (?, ?, ?, ?, ?); 
                    ''', data)
    cursor.execute(
        'INSERT INTO questions(pid, theaid) VALUES (?, NULL);', (pid,))

    # Sucessfully message
    print('-'*40)
    print("You successfully post a question")

    connection.commit()


def search_post(user_id):
    """
    Allow the user to search for post they are looking for given the keywords
    Ask the user to enter the keywords they are looking for
    Check if the keyword already given, if the user do not provide any keywords, 
    Save the keywords into the list
    Create the dictionary: the key is pid, the value is the number of appearance
    Run the queries to return for each keyword, if the pid is in the dictionary increment by 1
    Otherwise, create a new one and set it equal to 1
    If the user provides all the keywords does not appear within body, title and tags of any posts, print error message and return
    If not, sort the dictionary based on the number of matching keywords
    If there are more than 5 values, print only 5 and print the option whether want to see more options
    If yes, print the next 5 values. The process keeps going until the users hits no or there are no more posts to display
    Ask the user to perform post action
    Input: user_id - To determine whether the user_id can perform post action
    Output: state - Whether the user want to logout of the system
    """

    global cursor, connection

    # Ask the user to enter the keywords they are looking for
    keyword_list = []
    flag = "y"
    while flag == "y":
        keyword = input("Enter the keyword you are looking for in the post: ")
        keyword = keyword.lower()

        # If the user enter the keyword that already existed in the program
        if keyword not in keyword_list:
            keyword_list.append(keyword)
        else:
            print("You enter the keyword that already existed in the program. ")

        # Check if the user wants to enter more keywords.
        flag = input("If you want to continue to enter keyword, press y: ")
        flag = flag.lower()

        # If the keyword_list is empty, not allow the user to continue
        if len(keyword) == 0:
            print("You do not provide any keywords. Please try again")
            flag = "y"
            keyword_list = []

    # For each keyword, search the pid that has the keyword in the either body, tag, title
    num_appearance = {}
    for key in keyword_list:
        data = ('%'+key+'%', '%'+key+'%', '%'+key+'%')
        cursor.execute('''SELECT p1.pid
            FROM posts p1
            WHERE p1.title LIKE ?
            UNION
            SELECT p2.pid
            FROM posts p2
            WHERE p2.body LIKE ?
            UNION
            SELECT t.pid
            FROM tags t
            WHERE t.tag LIKE ?;''', data)
        result = cursor.fetchall()
        if result != []:  # If there are keyword the user are looking for is valid
            for i in range(len(result)):
                # If the pid already in the dictionary, increment the appearance by 1
                if result[i][0] not in num_appearance:
                    num_appearance[result[i][0]] = 1
                else:
                    num_appearance[result[i][0]] += 1

    # Check if the user provides any valid keywords
    if len(num_appearance) == 0:
        print('-'*40)
        print('There are no valid keywords you are looking for in the database')
        connection.commit()
        return

    # Sort the dictionary based on the number of appearance and put the keys back in another list of pid for print
    sort_num_appearance = sorted(
        num_appearance.items(), key=lambda x: x[1], reverse=True)
    sorted_pid_list = []
    for i in range(len(sort_num_appearance)):
        sorted_pid_list.append(sort_num_appearance[i][0])

    # Display the first 5 result in the dictionary
    available = []  # Keep track which pid the user can perform post action
    decision = 'y'
    index = 0
    while decision == 'y':
        print('-'*178)
        print('{0:^8}|{1:^10}|{2:^50}|{3:^80}|{4:^8}|{5:^8}|{6:^8}'.format(
            'PostID', 'Post Date', 'Title', 'Body', 'Poster', '#Votes', '#Answer'), end="\n")
        print('{0:8}+{1:10}+{2:50}+{3:80}+{4:8}+{5:8}+{6:8}'.format('-' *
                                                                    8, '-'*10, '-'*50, '-'*80, '-'*8, '-'*8, '-'*8), end="\n")
        if index + 5 > len(sorted_pid_list):  # Check out of range data
            end = len(sorted_pid_list)
        else:
            end = index + 5
        for i in range(index, end):
            cursor.execute('''select p.pid, p.pdate, p.title, p.body, p.poster,
                                        ifnull(cvote.vote,0),
                                        (case
                                        when p.pid in (select pid from answers) then 'N/A'
                                        when p.pid in (select pid from questions) and (canswer.answer is NULL) then '0'
                                        else canswer.answer
                                        end)
                              from posts p 
                              left join (SELECT v.pid pid, max(v.vno) vote
                                        FROM votes v
                                        GROUP BY v.pid) as cvote on cvote.pid = p.pid
                              left join (SELECT a.qid qid, count(a.pid) answer
                                        FROM answers a
                                        GROUP BY a.qid) as canswer on canswer.qid = p.pid
                              where p.pid = ?;''', (sorted_pid_list[i],))
            result1 = cursor.fetchone()
            available.append(result1[0])
            print('{0:^8}|{1:^10}|{2:50}|{3:80}|{4:^8}|{5:^8}|{6:^8}'.format(result1[0], result1[1], result1[2][0:47] + '...' if len(
                result1[2]) > 50 else result1[2], result1[3][0:77] + '...' if len(result1[3]) > 80 else result1[3], result1[4], result1[5], result1[6]), end='\n')

        # Update the index
        index += 5

        # If the current index is less than length of sorted_pid_list, allow the user to display more results
        if index < len(sorted_pid_list):  # Check again this
            print('-'*178)
            decision = input("Do you want to display more results (y/n): ")
            decision = decision.lower()
        else:
            decision = 'n'

    # Ask the user to perform which post option they want to perform
    # Check if the option is valid
    check = True
    state = None
    while check:
        print('-'*178)
        option = input("Post action - Answer to a question (1), Vote for a post (2),  Mark an accepted answer for post (3), Give a badge (4), Add a tag (5), Edit (6), Logout (7): ")
        option = option.lower()
        if option == '1':
            answer(user_id, available)
            check = False
        elif option == '2':
            vote(user_id, available)
            check = False
        elif option == '3':
            if privileged_check(user_id):  # check if the user is the privileged or not
                mark(available)
                check = False
            else:
                print('-'*40)
                print("You are not privileged user!!! You cannot perform the action")
                check = True
        elif option == '4':
            if privileged_check(user_id):  # check if the user is the privileged or not
                give_badge(available)
                check = False
            else:
                print('-'*40)
                print("You are not privileged user!!! You cannot perform the action")
                check = True
        elif option == '5':
            if privileged_check(user_id):  # check if the user is the privileged or not
                add_tag(available)
                check = False
            else:
                print('-'*40)
                print("You are not privileged user!!! You cannot perform the action")
                check = True
        elif option == '6':
            if privileged_check(user_id):  # check if the user is the privileged or not
                edit(available)
                check = False
            else:
                print('-'*40)
                print("You are not privileged user!!! You cannot perform the action")
                check = True
        elif option == '7':
            state = 'log in'
            return state
        else:
            print('-'*40)
            print("You enter the wrong option. Please choose again! ")

    connection.commit()


def answer(user_id, available):
    '''
    Allow the user to answer a question
    Check if the displaying posts has a question to answer. If all displaying posts are answer posts, return immediately
    Else, ask the user to provide the post id they are want to answer
    Check if the post is within the available list, and if the pid is in fact a question
    If satisfied, ask the user the body and title 
    Then the system will randomize the pid and save all the information in the database
    Input: user_id - use the user_id to determine who is the poster of the post
            available - list of displaying posts from the search_post function
    Output: None
    '''

    global connection, cursor

    current_date = time.strftime("%Y-%m-%d")

    # Check if the available does contain the question for answer. If print the message and return immediately
    check = False
    for id in available:
        cursor.execute(
            'select questions.pid from questions where questions.pid = ?;', (id,))
        result = cursor.fetchone()
        if result != None:
            check = True

    if check == False:
        print('-'*40)
        print("There are no questions in the available list for you to answer")
        return

    # If the user do not provide the pid for question, continue to ask
    qid = input("Enter the post id you are looking for: ")
    qid = qid.lower()  # prevent case sensitivity
    flag = True
    while flag:
        # Validate the input within the available list
        for id in available:
            if id == qid:
                flag = False
        if flag:
            qid = input(
                "You do not enter a valid post id. Enter the post id you are looking for: ")
            qid.lower()
            continue
        # Check if the qid id is in the question lists
        cursor.execute('''select pid from questions where pid = ?;''', (qid,))
        result = cursor.fetchone()
        if result == None:
            qid = input(
                "You do not enter a valid quetion id. Enter the question id: ")
            qid.lower()
            flag = True
        else:
            flag = False

    # If the user provides the valid pid

    title = input("Enter the title: ")
    title = title.lower()  # prevent case sensitivity

    body = input("Enter the body: ")
    body = body.lower()  # prevent case sensitivity

    # Random choose the pid and check whether the pid is unique in the database. If not, keep increase the pid by 1 until it is unique
    flag = True
    id = random.randint(0, 9999)
    count = 0
    while flag != None:
        id = (id + 1) % 10000
        pid = str(id)
        cursor.execute(
            'select posts.pid from posts where posts.pid = ?', (pid,))
        flag = cursor.fetchone()
        count += 1

    # Check if the pid of system has been full
    if count == 9999:
        print("The system is full. You cannot have more posts.")
        return

    # Update the database
    data1 = (pid, current_date, title, body, user_id)
    data2 = (pid, qid)
    cursor.execute(
        '''INSERT INTO posts(pid, pdate, title, body, poster) VALUES (?, ?, ?, ?, ?);''', data1)
    cursor.execute('''INSERT INTO answers(pid, qid) VALUES (?, ?);''', data2)

    # Answer the quetion successfully
    print('-'*40)
    print('You answer the question successfully')

    connection.commit()


def vote(user_id, available):
    """
    Ask the user which post they want to post
    Check if among posts in the available list, does the current user_id votes all the posts
    Check if the post exists in the available list
    Check whether the user have already voted on the post
    If not ask the user to re-enter which post they want to enter
    If yes, update the data properly
    Input: user_id - use the user_id to determine who is the poster of the post
            available - list of displaying posts from the search_post function
    Output: None
    """

    global connection, cursor

    current_date = time.strftime("%Y-%m-%d")

    # Check if the current user has already voted all the posts in the available list
    check = True
    for id in available:
        data = (id,)
        cursor.execute(
            "select votes.uid from votes where votes.pid = ? and votes.uid = ?;", (id, user_id))
        result = cursor.fetchone()
        if result == None:
            check = False

    if check:
        print('-'*40)
        print('You already voted all the posts in the available list!!!')
        return

    # Ask the user to enter the pid
    pid = input("Enter the pid you want to vote: ")
    pid = pid.lower()  # prevent case sensitivity

    # Check if the pid in the available id they allow to vote
    flag = True
    while flag:
        # Check if pid in the available id
        if pid in available:
            flag = False
        else:
            print('-'*40)
            pid = input(
                "You do not enter a valid pid. Enter the pid you want to vote: ")
            pid = pid.lower()
            continue

        # Check if already voted
        cursor.execute(
            "select votes.uid from votes where votes.pid = ? and votes.uid = ?;", (pid, user_id))
        result = cursor.fetchone()
        if result == None:
            flag = False
        else:
            print('-'*40)
            pid = input(
                "You have already voted. Enter the pid you want to vote: ")
            pid = pid.lower()
            flag = True

    # If the pid is valid, return the number of votes the post has
    cursor.execute('select votes.vno from votes where votes.pid = ?;', (pid,))
    vno = cursor.fetchall()
    if vno == []:  # If the post has the 1st vote
        vno = 1
    else:
        vno = int(vno[-1][0]) + 1
    # Update the votes in the database
    data = (pid, vno, current_date, user_id)
    cursor.execute('''INSERT INTO votes(pid, vno, vdate, uid) VALUES
	                (?, ?, ?, ?);''', data)
    # Vote the quetion successfully
    print('-'*40)
    print('You vote the post successfully')

    connection.commit()


def mark(available):
    '''
    Allow the user to mark the accepted answer for the specific question
    Check for all posts in the available list, if there are no answer posts, print that message that you cannot mark.
    Otherwise, ask the user to enter the pid for a answer
    Check if the post id does exist in the available list and in the answers table
    If it does, return the question id for answer id above
    If the question does not have any accepted answer. Mark the accepted answer immediately 
    If the question does have an accepted answer. Ask the user if they want to replace the previous one or not
    If yes, record the new accepted answer in the db
    Otherwise, leave information unchanged
    Input: available - list of displaying posts from search_post
    Output: None
    '''
    global connection, cursor

    # Check if the available does contain the answer for question. If not, print the message and return immediately
    check = False
    for id in available:
        cursor.execute(
            'select answers.pid from answers where answers.pid = ?;', (id,))
        result = cursor.fetchone()
        if result != None:
            check = True

    if check == False:
        print('-'*40)
        print("There are no answers in the available list for you to mark")
        return

    aid = input("Enter the answer id: ")
    aid = aid.lower()  # prevent case sensitivity

    # Check if the question id in the available list
    flag = True
    while flag:
        if aid in available:
            flag = False
        if flag:
            aid = input(
                "You do not enter a valid answer id. Enter the answer id: ")
            aid.lower()
            continue
        # Check if the answer id is in the answer lists
        cursor.execute('''select pid from answers where pid = ?;''', (aid,))
        result = cursor.fetchone()
        if result == None:
            aid = input(
                "You do not enter a valid answer id. Enter the answer id: ")
            aid.lower()
            flag = True
        else:
            flag = False

    # Return the qid of the answer above
    cursor.execute('select qid from answers where pid = ?;', (aid,))
    qid = cursor.fetchone()[0]

    # Check if the question does have an accepted answer
    cursor.execute(
        'select questions.theaid from questions where questions.pid = ?;', (qid,))
    accepted = cursor.fetchone()[0]
    data = (aid, qid)
    if accepted == None:  # If there are no accepted answer
        cursor.execute('''UPDATE questions
                          SET theaid = ?
                          WHERE pid = ?;''', data)
        # Successfully message
        print('-'*40)
        print("You successfully mark the accepted answer for the post ")
    else:
        check = True
        while check:
            decision = input(
                "Do you want to replace the old accepted answer with the new one (y/n)? ")
            decision = decision.lower()  # prevent case sensitivity

            if decision == 'y':
                cursor.execute('''UPDATE questions
                                  SET theaid = ?
                                  WHERE pid = ?;''', data)
                # Successfully message
                print('-'*40)
                print("You successfully mark the accepted answer for the post ")
                check = False
            elif decision == 'n':
                # Message
                print('-'*40)
                print("You have not changed the accepted answer for the post ")
                check = False
            else:
                print("You do not enter a valid option. ", end='')

    connection.commit()


def give_badge(available):
    '''
    Allow the user to give badge to the user having posts in the available list
    Check among available lists, if all the poster of the post in the available list has been given any badges on the current_date
    If yes, print the message that all the poster of posts in the available list has been given a badge and return the function
    Ask the user to enter the uid s/he wants to give badge
    Check if the give uid has been given any badges on the current day
    If not, asks the user to provide another user id
    If yes, Ask the user to enter the name of the badge
    Check whether the user enter the correct badge name
    If all of the constraint above are satisfied, record in the database
    Input: available - list of displaying posts from search_post
    Output: None
    '''
    global connection, cursor

    current_date = time.strftime("%Y-%m-%d")

    # Check if all the user in the available list has been given a badge in the same day the another users decides to give them a badge
    check = True
    for id in available:
        cursor.execute(
            "select posts.poster from posts, ubadges where posts.pid = ? and ubadges.uid = posts.poster and ubadges.bdate = ?;", (id, current_date))
        result = cursor.fetchone()
        if result == None:
            check = False

    if check:
        print("-"*40)
        print("All the user in the available list has been given a badge!!!!")
        return

    # Ask the user id he/she wants to give the badge
    uid = input("Enter the user id you want to give the badge to: ")
    uid = uid.lower()  # prevent case sensitivity

    # Check if the user id does exist in the list of available
    check = True
    while check:
        for id in available:
            cursor.execute(
                "select poster from posts where pid = ? and poster = ?;", (id, uid))
            result = cursor.fetchone()
            if result != None:
                check = False
        if check:
            uid = input(
                "You enter the wrong user id. Enter the user id you want to give the badge to: ")
            uid = uid.lower()  # prevent case sensitivity

        cursor.execute(
            'select bdate from ubadges where uid = ? and bdate = ?;', (uid, current_date))
        result1 = cursor.fetchone()
        if result1 != None:
            check = True
            uid = input(
                "You cannot give badge to the user on the same day. Enter the user id you want to give the badge to: ")

    # Ask the user to enter the badge name
    bname = input("Enter the badge name you want to give to user: ")
    bname = bname.lower()  # prevent case sensitivity

    # Check if the user enter the correct badge name and check if the same badge name on the same day
    cursor.execute("select bname from badges;")
    badges = cursor.fetchall()
    flag = False
    while not flag:
        if badges != None:
            for item in badges:
                if item[0] == bname:
                    flag = True
            if not flag:
                bname = input(
                    "The badge name is incorrect. Enter the badge name you want to give to user: ")
                bname = bname.lower()  # prevent case sensitivity
        else:
            # Prevent the case there are no badge name in the database
            print("There are no badge name exist!!!")
            return

    # Update in the database 
    data = (uid, current_date, bname)
    cursor.execute('''INSERT INTO ubadges(uid, bdate, bname) VALUES
	                    (?, ?, ?);''', data)
    # print the message that you successfully give the badge to the user
    print("-"*40)
    print('You successfully give the badge to the user')

    connection.commit()


def add_tag(available):
    '''
    Allow the user to add tag
    Ask the user which post they want to add tag
    Check whether the post exists in the available list
    If not, ask the user again
    If yes, ask the user to enter the tag name
    Check whether the tag name is already associated with the post
    If yes, ask the user again
    If not, update the database
    Input: available - list of displaying posts from search_post
    Output: None
    '''
    global connection, cursor

    # Ask the post id he/she wants to add tag
    pid = input("Enter the post id you want to add tag: ")
    pid = pid.lower()  # prevent case sensitivity

    # Check if the post id does exist in the available list
    flag = True
    while flag:
        for id in available:
            if id == pid:
                flag = False
        if flag:
            pid = input(
                "You do not enter a valid post id. Enter the pid you want to vote: ")
            pid.lower()

    # Ask the tag he/she wants to give to the post
    tag = input("Enter the tag you want to give to the post: ")
    tag = tag.lower()  # prevent case sensitivity

    # Check if the same tag already gives to the same post
    cursor.execute("select tag from tags where pid = ?;", (pid,))
    tag_list = cursor.fetchall()
    flag = True
    while flag:
        check = False
        if tag_list == None:
            flag = False
        else:
            for item in tag_list:
                if item[0] == tag:
                    check = True
            if check:
                tag = input(
                    "The tag you give already existed. Enter the tag you want to give to the post: ")
                tag = tag.lower()  # prevent case sensitivity
            else:
                flag = False

    # Update in the database
    data = (pid, tag)
    cursor.execute('''INSERT INTO tags(pid, tag) VALUES
	                    (?, ?);''', data)

    # Successfully add the tag
    print('-'*40)
    print("You add the tag to the post successfully")

    connection.commit()


def edit(available):
    '''
    Allow the user to edit the post
    Ask the user which post they want to edit the title and the body
    Check whether the user exists in the available list
    Ask the user to enter the title and ask the user to enter the body
    Update the title and the body, while keep the pid, pdate, poster unchanged
    Input: available - list of displaying posts from search_post
    Output: None
    '''

    global connection, cursor

    # Ask the post id he/she wants to edit title or body
    pid = input("Enter the post id you want to edit title or body or both: ")
    pid = pid.lower()  # prevent case sensitivity

    # Check if the post id in the available list
    flag = True
    while flag:
        # Validate the input within the available list
        for id in available:
            if id == pid:
                flag = False
        if flag:
            pid = input(
                "You do not enter a valid post id. Enter the post id you want to edit title or body or both: ")
            pid.lower()

    # Ask whether the user wants to edit the title or not
    decision = input("Do you want to edit the title (y/n): ")
    decision = decision.lower()  # prevent case sensitivity
    check = True
    while check:
        if decision != 'y' and decision != 'n':
            decision = input('You choose the wrong option, please try again: ')
            decision = decision.lower()
        else:
            check = False
    if decision == 'y':
        title = input("Enter the title you want to edit: ")
        title = title.lower()  # prevent case sensitivity
        data = (title, pid)
        cursor.execute('''UPDATE posts 
                        SET title = ?
                        WHERE pid = ?;''', data)
    elif decision == 'n':
        pass

    # Ask whether the user wants to edit the body or not
    decision1 = input("Do you want to edit the body (y/n): ")
    decision1 = decision1.lower()  # prevent case sensitivity
    check1 = True
    while check1:
        if decision1 != 'y' and decision1 != 'n':
            decision1 = input(
                'You choose the wrong option, please try again: ')
            decision1 = decision1.lower()
        else:
            check1 = False

    if decision1 == 'y':
        body = input("Enter the body you want to edit: ")
        body = body.lower()  # prevent case sensitivity
        data1 = (body, pid)
        cursor.execute('''UPDATE posts 
                        SET body = ?
                        WHERE pid = ?;''', data1)
    elif decision1 == 'n':
        pass

    # Successful message
    if decision == 'y' and decision1 == 'y':
        print('-'*40)
        print("You successfully edit the title and body of the post")
    elif decision == 'y' and decision1 == 'n':
        print('-'*40)
        print('You successfully edit the title of the post')
    elif decision == 'n' and decision1 == 'y':
        print('-'*40)
        print('You successfully edit the body of the post')
    else:
        print('-'*40)
        print('Nothing has been updated')

    connection.commit()


def privileged_check(user_id):
    '''
    Check whether the user is a privileged or not
    Input: user_id - current user_id to check whether they are privileged or not
    Output: True/False - boolean with respect to they are and they are not privileged
    '''
    global connection, cursor

    
    cursor.execute('select uid from privileged;')
    privilege = cursor.fetchall()
    if privilege != None:  # If there are no privileged user
        for member in privilege:
            if member[0] == user_id:
                connection.commit()
                return True

    connection.commit()
    return False


def main():
    '''
    Control the programing
    Input: None
    Output: None
    '''
    global connection, cursor

    path_name = sys.argv[1]
    path_name = path_name.lower()  # prevent case sensitivity

    path = "./{}".format(path_name)
    connect(path)

    # Welcome message
    print("-"*40)
    print("Welcome to the system")

    # Status of the program to determine if the user want to log out or exit the program
    status = 'log in'
    while status == 'log in':
        # Option to register or log in
        print("-"*40)
        option = input("Login (l) or register (r) or quit(q): ")
        option = option.lower()  # prevent case sensitivity

        # Hanlding the option
        flag = True
        while flag:
            if option != 'l' and option != 'r' and option != 'q':
                option = input(
                    "Please try again. You do not choose the correct option: ")
                option = option.lower()  # prevent case sensitivity
            else:
                flag = False

        if option == 'l':
            # return user_id to determine whether the user is privileged or not
            user_id = login_handle()
        elif option == 'r':
            # return user_id to determine whether the user is privileged or not
            user_id = register_handle()
        else:
            break

        # After successfully login in the system, prompt the user to do the following tasks
        flag1 = True
        while flag1:
            print('-'*40)
            decision = input(
                '''Post a question (1), Search for posts (2), Log out (3), Exit (4): ''')
            if decision == '1':
                post_question(user_id)
            elif decision == '2':
                result = search_post(user_id)
                if result == 'log in':  # Check the status of the program depends on the result of the search_post action
                    flag1 = False
            elif decision == '3':
                flag1 = False
            elif decision == '4':
                flag1 = False
                status = 'exit'
            else:
                print("You enter a wrong option. Please try again")

    connection.commit()
    connection.close()
    return


if __name__ == "__main__":
    main()
