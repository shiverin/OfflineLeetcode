import json
import time
from leetscrape import GetQuestionsList, GetQuestion
import re
import ast
import html

# --- Helper functions with robust parsing and debugging ---

def parse_args_from_string(arg_string: str, problem_title: str) -> dict:
    """
    Parses key-value argument strings like 'nums = [2,7,11,15], target = 9'
    into a Python dictionary.
    Handles lists, nested structures, and avoids extra nesting.
    """
    #print(f"    [DEBUG] --- Starting parse_args_from_string for '{problem_title}' ---")
    #print(f"    [DEBUG]   Raw arg_string: '{arg_string}'")

    args = {}
    # Step 1: Split top-level commas only (avoid splitting inside brackets)
    bracket_level = 0
    current = ""
    pairs = []
    for char in arg_string:
        if char in "[{(":
            bracket_level += 1
        elif char in "]})":
            bracket_level -= 1
        if char == "," and bracket_level == 0:
            pairs.append(current)
            current = ""
        else:
            current += char
    if current:
        pairs.append(current)

    # Step 2: Parse each key=value pair
    for pair in pairs:
        if "=" not in pair:
            continue
        key, value = pair.split("=", 1)
        key = key.strip()
        value = value.strip()
        try:
            evaluated = ast.literal_eval(value)
            # Flatten single-element tuples at the outermost level
            if isinstance(evaluated, tuple) and len(evaluated) == 1:
                evaluated = evaluated[0]
            args[key] = evaluated
            #print(f"    [DEBUG] Parsed key='{key}': {evaluated}")
        except Exception as e:
            args[key] = value
            #print(f"    [DEBUG] Failed to parse value for key='{key}', using raw: '{value}' Error: {e}")

    #print(f"    [DEBUG] Final parsed args dict: {args}")
    #print(f"    [DEBUG] --- Finished parse_args_from_string ---")
    return args

def extract_test_cases_from_description(description: str, problem_title: str) -> list:
    """
    Extracts and parses test cases from a LeetCode problem description.
    """
    #print(f"  [DEBUG] --- Starting extract_test_cases_from_description for '{problem_title}' ---")
    if not description:
        #print("  [DEBUG] Description empty. Returning []")
        return []

    example_blocks = re.findall(r'<pre>([\s\S]*?)</pre>', description)
    #print(f"  [DEBUG] Found {len(example_blocks)} <pre> blocks")
    test_cases = []

    for i, block in enumerate(example_blocks):
        #print(f"  [DEBUG] --- Processing <pre> block {i+1} ---")
        decoded_block = html.unescape(block)
        clean_block = re.sub(r'<.*?>', '', decoded_block).strip()

        input_match = re.search(r'Input:\s*(.*)', clean_block)
        output_match = re.search(r'Output:\s*(.*)', clean_block)

        if input_match and output_match:
            input_str = input_match.group(1).strip()
            output_str = output_match.group(1).strip()
            #print(f"  [DEBUG] Input: {input_str}")
            #print(f"  [DEBUG] Output: {output_str}")

            input_dict = parse_args_from_string(input_str, problem_title)

            try:
                output_val = ast.literal_eval(output_str)
            except Exception:
                output_val = output_str

            if input_dict:
                final_case = {"input": input_dict, "output": output_val}
                test_cases.append(final_case)
                #print(f"  [DEBUG] Appended test case: {final_case}")
        else:
            #print("  [DEBUG] Could not find Input/Output in block, skipping.")
            pass
    #print(f"  [DEBUG] --- Finished extract_test_cases_from_description. Total: {len(test_cases)} ---")
    return test_cases


# --- Main Scraper Script ---

def create_database():
    #print("🚀 Starting LeetCode scrape...")
    try:
        ls = GetQuestionsList()
        ls.scrape()
        all_questions_df = ls.questions
        #print(f"✅ Found {len(all_questions_df)} total problems.")
    except Exception as e:
        #print(f"❌ CRITICAL: Failed to fetch problem list. Error: {e}")
        return

    final_database = {}
    fetched_count = 0
    MAX_PROBLEMS_TO_FETCH = None  # None to process all

    for _, problem in all_questions_df.iterrows():
        if MAX_PROBLEMS_TO_FETCH is not None and fetched_count >= MAX_PROBLEMS_TO_FETCH:
            #print(f"\n🏁 Reached fetch limit of {MAX_PROBLEMS_TO_FETCH} problems.")
            break
        if problem['paidOnly']:
            continue

        slug = problem['titleSlug']
        qid = str(problem['QID'])
        title = problem['title']
        print(f"\nProcessing QID {qid}: {title} ({slug})")

        try:
            question = GetQuestion(titleSlug=slug).scrape()
            test_cases = extract_test_cases_from_description(question.Body, title)

            if not test_cases:
                #print(f"    - Warning: No test cases extracted.")
                pass

            function_name = "solution"
            if hasattr(question, 'metaData') and isinstance(question.metaData, str):
                try:
                    function_name = json.loads(question.metaData).get('name', 'solution')
                except json.JSONDecodeError:
                    pass

            final_database[qid] = {
                "title": title,
                "slug": slug,
                "difficulty": question.difficulty,
                "description": question.Body,
                "function_name": function_name,
                "template": question.Code if hasattr(question, 'Code') else "",
                "test_cases": test_cases,
            }

            #print(f"    ✓ Processed successfully. Test cases: {len(test_cases)}")
            fetched_count += 1
            time.sleep(1.5)
        except Exception as e:
            print(f"    ❌ Error processing {slug}: {e}")
            time.sleep(2)

    try:
        with open("database.json", 'w', encoding='utf-8') as f:
            json.dump(final_database, f, indent=4)
        print(f"\n✅ Success! Database saved to 'database.json'.")
    except Exception as e:
        print(f"\n❌ Failed to write database file. Error: {e}")


if __name__ == "__main__":
    create_database()
