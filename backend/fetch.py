import json  
import time  
from leetscrape import GetQuestionsList, GetQuestion  
import re  
import ast  
  
# --- Helper functions adapted from leetscrape source code ---  
  
def parse_args_from_string(arg_string: str) -> dict:  
    """  
    A simplified helper to parse key-value argument strings like 'nums = [1,2,3], target = 9'  
    into a Python dictionary. This is a crucial part of the library's logic.  
    """  
    args = {}  
    # Use regex to find all key = value pairs  
    # This handles nested brackets and quotes reasonably well  
    pattern = r'(\w+)\s*=\s*($$.*?$$|\".*?\"|\'.*?\'|\S+)'  
    matches = re.findall(pattern, arg_string)  
      
    for key, value in matches:  
        try:  
            # Use ast.literal_eval for safe evaluation of Python literals  
            args[key.strip()] = ast.literal_eval(value.strip())  
        except (ValueError, SyntaxError):  
            # Fallback for simple unquoted strings  
            args[key.strip()] = value.strip()  
    return args  
  
def extract_test_cases_from_description(description: str) -> list:
    """
    Extract Input/Output pairs from <pre> blocks in the problem description.
    Flatten list inputs like 'nums' if they are nested.
    """
    if not description:
        return []

    example_blocks = re.findall(r'<pre>([\s\S]*?)</pre>', description)
    test_cases = []

    for block in example_blocks:
        clean_block = re.sub(r'<.*?>', '', block).strip()
        input_match = re.search(r'Input:\s*(.*)', clean_block)
        output_match = re.search(r'Output:\s*(.*)', clean_block)

        if input_match and output_match:
            input_str = input_match.group(1).strip()
            output_str = output_match.group(1).strip()

            # Parse input string into dictionary
            input_dict = parse_args_from_string(input_str)

            # Flatten any nested lists for 'nums' (or other list arguments)
            for k, v in input_dict.items():
                if isinstance(v, list) and len(v) == 1 and isinstance(v[0], list):
                    input_dict[k] = v[0]

            # Parse output
            try:
                output_val = ast.literal_eval(output_str)
            except (ValueError, SyntaxError):
                output_val = output_str

            if input_dict:
                test_cases.append({
                    "input": input_dict,
                    "output": output_val
                })

    return test_cases

  
# --- Main Scraper Script ---  
  
def create_database():  
    """  
    Fetches LeetCode problems and builds a database, using a test case  
    extraction method that mimics the leetscrape library's internal source code.  
    """  
    print("🚀 Starting LeetCode scrape...")  
  
    try:  
        ls = GetQuestionsList()  
        ls.scrape()  
        all_questions_df = ls.questions  
        print(f"✅ Found {len(all_questions_df)} total problems.")  
    except Exception as e:  
        print(f"❌ CRITICAL: Failed to fetch problem list. Error: {e}")  
        return  
  
    final_database = {}  
    fetched_count = 0  
    MAX_PROBLEMS_TO_FETCH = 50 # Set to None to fetch all  
  
    for _, problem in all_questions_df.iterrows():  
        if MAX_PROBLEMS_TO_FETCH is not None and fetched_count >= MAX_PROBLEMS_TO_FETCH:  
            print(f"\n🏁 Reached fetch limit of {MAX_PROBLEMS_TO_FETCH} problems.")  
            break  
              
        if problem['paidOnly']:  
            continue  
  
        slug = problem['titleSlug']  
        qid = str(problem['QID'])  
          
        print(f"\nProcessing QID {qid}: {problem['title']} ({slug})")  
  
        try:  
            question = GetQuestion(titleSlug=slug).scrape()  
              
            # Extract test cases by parsing the description HTML  
            test_cases = extract_test_cases_from_description(question.Body)  
            if not test_cases:  
                print(f"    - Warning: No test cases could be extracted from description.")  
  
            # Get function name from metaData  
            function_name = "solution"  
            if hasattr(question, 'metaData') and isinstance(question.metaData, str):  
                try:  
                    function_name = json.loads(question.metaData).get('name', 'solution')  
                except json.JSONDecodeError: pass  
  
            final_database[qid] = {  
                "title": question.title,  
                "slug": question.titleSlug,  
                "difficulty": question.difficulty,  
                "description": question.Body,  
                "function_name": function_name,  
                "template": question.Code if hasattr(question, 'Code') else "",  
                "test_cases": test_cases,  
            }  
              
            print(f"    ✓ Successfully processed. Found {len(test_cases)} test cases.")  
            fetched_count += 1  
            time.sleep(1.5)  
  
        except Exception as e:  
            print(f"    ❌ Error processing {slug}: {e}")  
            time.sleep(2)  
  
    try:  
        with open("database.json", 'w', encoding='utf-8') as f:  
            json.dump(final_database, f, indent=4)  
        print(f"\n\n✅ Success! Database saved to 'database.json'.")  
    except Exception as e:  
        print(f"\n\n❌ CRITICAL: Failed to write database file. Error: {e}")  
  
if __name__ == "__main__":  
    create_database()