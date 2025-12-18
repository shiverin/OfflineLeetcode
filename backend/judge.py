import importlib.util  
import os  
import time  
  

# --- LeetCode Standard Environment ---  
LEETCODE_PREPended_CODE = """  
import collections, heapq, functools, itertools, math, random, re, sys, copy  
from typing import List, Optional, Tuple, Deque, Dict, Set  
from collections import deque, Counter, defaultdict  
from heapq import heappush, heappop, heapify  
from functools import lru_cache  
  
# Dummy classes for LeetCode's data structures  
class ListNode:  
    def __init__(self, val=0, next=None):  
        self.val = val  
        self.next = next  
class TreeNode:  
    def __init__(self, val=0, left=None, right=None):  
        self.val = val  
        self.left = left  
        self.right = right  
"""  
# --- End of LeetCode Environment ---  
  
# --- Helper Function to convert "Title Case" to "camelCase" ---  
def to_camel_case(title_str: str) -> str:  
    """Converts a string like 'Two Sum' or 'Add Two Numbers' to 'twoSum' or 'addTwoNumbers'."""  
    words = title_str.split(' ')  
    if not words:  
        return ""  
    # The first word is lowercase, and all subsequent words are capitalized.  
    return words[0].lower() + ''.join(word.capitalize() for word in words[1:])  


class Judge:  
    def __init__(self, database):  
        self.db = database  
  
# In judge.py  
  
    def run(self, question_id, user_code_str):  
        if question_id not in self.db:  
            return {"status": "error", "message": f"Question ID {question_id} not found."}  
    
        q_data = self.db[question_id]
        func_name = "solution"
    
        # --- THE CORRECTED STRING PROCESSING ---  
        
        # 1. Define the essential imports that are needed for class/function definitions.  
        # This prevents the 'NameError: name "List" is not defined' error.  
        typing_imports = "from typing import List, Optional, Tuple, Deque, Dict, Set"  
    
        # 2. Combine all parts in the correct order.  
        # The user's code now has the typing imports directly above it.  
        full_code = f"{LEETCODE_PREPended_CODE}\n\n{typing_imports}\n\n{user_code_str}"  
    
        # --- END OF FIX ---  
            
        temp_file_path = "temp_solution.py"  
        with open(temp_file_path, "w", encoding='utf-8') as f:  
            f.write(full_code)  
    
        try:  
            spec = importlib.util.spec_from_file_location("solution", temp_file_path)
            user_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(user_module)

            if hasattr(user_module, 'Solution'):
                solution_instance = user_module.Solution()
                # dynamically pick the first callable method that doesn't start with '_'
                func_name = next(
                    (name for name in dir(solution_instance)
                    if callable(getattr(solution_instance, name)) and not name.startswith("_")),
                    None
                )
                if not func_name:
                    os.remove(temp_file_path)
                    return {"status": "error", "message": "No callable method found in Solution class."}
                user_func = getattr(solution_instance, func_name)
            else:
                # dynamically pick the first top-level function in the module
                func_name = next(
                    (name for name in dir(user_module)
                    if callable(getattr(user_module, name)) and not name.startswith("_")),
                    None
                )
                if not func_name:
                    os.remove(temp_file_path)
                    return {"status": "error", "message": "No top-level function found in module."}
                user_func = getattr(user_module, func_name)
    
        except AttributeError:  
            os.remove(temp_file_path)  
            return {"status": "error", "message": f"Execution Error: Function '{func_name}' or class 'Solution' not found in your code. Check for syntax errors or missing type hint imports (e.g., 'List'). {user_code_str}"}  
        except Exception as e:  
            os.remove(temp_file_path)  
            return {"status": "error", "message": f"Syntax Error: {e}"}  
            
        test_case_results = []  
        passed_count = 0  
          
        for idx, case in enumerate(q_data['test_cases']):  
            inputs_dict = case['input']  

            expected_output = case['output']  
            case_result = {"id": idx + 1, "input": inputs_dict, "expected": expected_output}  
              
            try:  
                start_time = time.time()  
                # Use ** to unpack the dictionary into named arguments  
                actual_output = user_func(**inputs_dict)  
                duration = (time.time() - start_time) * 1000  
  
                # Improved comparison for list outputs  
                is_passed = False  
                if isinstance(actual_output, list) and isinstance(expected_output, list):  
                    is_passed = sorted(actual_output) == sorted(expected_output)  
                else:  
                    is_passed = actual_output == expected_output  
  
                if is_passed:  
                    case_result["passed"] = True  
                    passed_count += 1  
                else:  
                    case_result["passed"] = False  
                  
                case_result["actual"] = actual_output  
                case_result["duration"] = f"{duration:.2f}ms"  
                case_result["error"] = None  
            except Exception as e:  
                case_result["passed"] = False  
                case_result["actual"] = None  
                case_result["error"] = f"Runtime Error: {e}"  
              
            test_case_results.append(case_result)  
  
        os.remove(temp_file_path)  
  
        final_report = {  
            "all_passed": passed_count == len(q_data['test_cases']),  
            "passed_count": passed_count,  
            "total_count": len(q_data['test_cases']),  
            "results": test_case_results  
        }  
          
        return final_report