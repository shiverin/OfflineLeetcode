import sys
import json
import os
from judge import Judge

DB_FILE = "database.json"

def load_db():
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def list_questions(db):
    print(f"\n{'ID':<5} {'Difficulty':<10} {'Title'}")
    print("-" * 40)
    for qid, data in db.items():
        print(f"{qid:<5} {data['difficulty']:<10} {data['title']}")
    print("-" * 40)

def generate_template(db, qid):
    if qid not in db:
        print("Invalid ID")
        return
    
    data = db[qid]
    filename = f"questions/{data['slug']}.py"
    
    if os.path.exists(filename):
        print(f"⚠️  File {filename} already exists!")
        return

    code = f"""# {data['title']}
# {data['description']}

from typing import List

class Solution:
    def {data['function_name']}(self, {', '.join(k for k in data['test_cases'][0]['input'].keys())}):
        # Write your code here
        pass
"""
    os.makedirs("questions", exist_ok=True)
    with open(filename, 'w') as f:
        f.write(code)
    print(f"📄 Created template: {filename}")

def main():
    db = load_db()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python main.py list        -> List all questions")
        print("  python main.py gen <ID>    -> Generate a solution file for a question")
        print("  python main.py run <ID>    -> Run your solution against tests")
        return

    command = sys.argv[1]

    if command == "list":
        list_questions(db)
    elif command == "gen":
        generate_template(db, sys.argv[2])
    elif command == "run":
        runner = Judge(db)
        runner.run(sys.argv[2])
    else:
        print("Unknown command.")

if __name__ == "__main__":
    main()