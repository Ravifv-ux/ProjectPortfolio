

import json
from pathlib import Path

import requests
import sqlite3
import os
from datetime import datetime

while True: 



    


    #Function to fetch data from API
    assignment = input("Enter the subject and the question associated: " )
    apiresponse = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3",   
        "prompt": f"""You are a homework helper designed to 
         respond to questions with short explanations, answer 
         this question {assignment}, Answer the user's homework question. You must return your response 
         strictly as a JSON object with three different keys in your answer, do not fit all the keys into one:
        'subject', 'question', and 'answer'. Do not include
        any other text or markdown outside the JSON, return keys in double quotes.""",
        'stream': False
    }
        )
    replylist = json.loads(apiresponse.json()['response'])
    #reply is the genuine reply while reply list is what i made to parse the json response into a list so i can access the different keys in the json object.
    reply = apiresponse.json()['response']
    subject = replylist['subject']
    question = replylist['question']
    #answer is the actual answer to the question, which is what we want to save in the database along with the subject and question for future reference.
    answer = "".join(replylist['answer'])

  
    try:
        print(reply)
    except requests.RequestException as e:
        print(f"Error fetching API data: {e}") 

    print(f"Subject: {subject}")
    print(f"Question: {question}")
    print(f"Response: {answer}")

    rating = int(input("Rate the response on a scale of 1-10, type a number only: "))


    #Create a SQLite database with a table: id, timestamp, subject, question, response, rating\

    #remember to make cursor in global mistake, dumb mistake
    #dont close a connection and then try to use the cursor, that is a common mistake, make sure to create the connection and cursor at the right scope.
    #commit the cursor after executing the insert statement, otherwise the changes won't be saved to the database. Always remember to commit after making changes to the database.
    
    DB_PATH = "tusmadre.db"
    print(f"Database path: {os.path.abspath(DB_PATH)}")
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()    
    def create_table():
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS saved_responses(        
            response TEXT, 
            subject TEXT,
            question TEXT,
            rating INTEGER);
            """
                        )
            
        connection.commit()
        print("Database and table created successfully: ")

    try:
        create_table()
        print("Database and table created successfully.")
        cursor.execute('INSERT INTO saved_responses VALUES (?, ?, ?, ?)', (answer, subject, question, rating)) 
        connection.commit()
        print("Data inserted successfully.")
    except Exception as e:
        print(f"Error creating database or table: {e}")

    cursor.execute('SELECT * FROM saved_responses')
    print(cursor.fetchall())
    cursor.execute('drop table if exists saved_responses')
    connection.close()
    cont = input("Do you want to continue? (yes/no): ")
    if cont.lower() != 'yes':
        break
