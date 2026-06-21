
import requests
import json
import time
from datetime import datetime
import sqlite3

promptfile = "prompts.json"
def loadPrompts():
    with open(promptfile, 'r') as file:
        data = json.load(file)
        prompts = [item['text'] for item in data if 'text' in item]
        id  = [item['id'] for item in data if 'id' in item]
    return prompts, id 

# ANSI COLORS
class Color:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
now = datetime.now()


def divider():
    print(f"\n{Color.MAGENTA}" + "=" * 80 + f"{Color.RESET}")
    
    
def savetoDB(item, response, category, rating, runid,prompt_id, elapsed, now):
    DB_PATH2 = "responses.db"
    connection = sqlite3.connect(DB_PATH2)
    cursor = connection.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS responses(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt TEXT,
                    response TEXT,
                    category TEXT,
                    rating INTEGER,
                    runid INTEGER,
                    prompt_id INTEGER,
                    latency REAL,
                    timestamp DATETIME
                    )
                    """
                   )
                   
    cursor.execute("""
                   INSERT INTO responses (prompt, response, category, rating, runid, prompt_id, latency, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                   """, (item, response, category, rating, runid, prompt_id, elapsed, now))
    connection.commit()
    connection.close()
    #print(f"{Color.GREEN}Data saved to database successfully.{Color.RESET}")
    
prompts, id = loadPrompts()

def getResponse(prompts, id):
    loadPrompts()
    
    runid = 0
    for index, item in enumerate(prompts, start=1):
        divider()
        prompt_id = id[index - 1]  # Get the corresponding id for the current prompt 
        """print(
            f"{Color.BOLD}{Color.CYAN}"
            f"PROMPT {index}/{total}"
            f"{Color.RESET}"
        )

        print(f"\n{Color.YELLOW}Input Prompt:{Color.RESET}")
        print(f"{item}\n")"""

        start = time.time()

        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": f"""
                    In a concise manner answer the following prompt: {item}

                    Additionally make four keys:
                    'prompt'
                    'response'
                    'category': the category is either factual, reasoning, or creative you can only choose between those three,
                    'id': {prompt_id}
                    """,
                    "stream": False
                }
            )

            data = response.json()
            
            elapsed = round(time.time() - start, 2)
            
            
            
            """print(f"{Color.GREEN}Response:{Color.RESET}\n")
            print(data.get('response', 'No response found'))"""
            
            #splitting the response into dictionary
            text = data.get('response', 'No response found')
            parsed_data = {}
            for line in text.splitlines():
                     if line.startswith("**") and ":" in line:
                        key, value = line.split(":", 1)
                        key = key.replace("**", "").strip().lower()
                        value = value.strip()

                        parsed_data[key] = value
            
            category = parsed_data.get('category', 'No category found')
            
            """print(
                f"\n{Color.CYAN}"
                f"Completed in {elapsed} seconds"
                f"{Color.RESET}"
            )"""
            rating = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "id": prompt_id,
                    "prompt": f"""Rate the response to the following prompt on a scale of 1-10 as close to a human as you can. The prompt is: {item},
                     solely rate it type nothing else, save it to a key titled 'rating' and return the json response with solely the rating, be as strict as possible.""",
                    "response": data.get('response', 'No response found'),
                    "stream": False
                }
            )
            
            rating = [char for char in rating.json().get('response', 'No rating found') if char.isdigit()]
            rating = "".join(rating)
            """print(f"\n{Color.GREEN}Rating: {rating}{Color.RESET}\n")"""
            runid +=1
            savetoDB(item, data.get('response', 'No response found'), category, int(rating), runid, prompt_id, elapsed, now)
            
            
        except Exception as e:

            print(f"{Color.RED}ERROR DETECTED:{Color.RESET}")
            print(e)

        divider()


if __name__ == "__main__":
    getResponse(prompts, id)



               
               

