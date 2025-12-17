# In judge.py  
  
import importlib.util  
import os  
import sys  
import time  
  
class Judge:  
    def __init__(self, database):  
        self.db = database  
  
    # Modify the signature to accept the user's code directly  
    def run(self, question_id, user_code_str):  
        if question_id not in self.db:  
            return {"status": "error", "message": f"Question ID {question_id} not found."}  
  
        q_data = self.db[question_id]  
        func_name = q_data['function_name']  
  
        # --- IMPORTANT SECURITY NOTE ---  
        # Writing the code to a file and executing it is a security risk.  
        # For a local-only app, it's okay, but never do this on a public server  
        # without proper sandboxing (e.g., Docker containers).  
        # Let's create a temporary file for the code.  
        temp_file_path = "temp_solution.py"  
        with open(temp_file_path, "w") as f:  
            f.write(user_code_str)  
  
        # Dynamically import the user's module from the temporary file  
        try:  
            spec = importlib.util.spec_from_file_location("solution", temp_file_path)  
            user_module = importlib.util.module_from_spec(spec)  
            spec.loader.exec_module(user_module)  
              
            user_func = getattr(user_module, func_name)  
  
        except Exception as e:  
            # Clean up the temp file  
            os.remove(temp_file_path)  
            return {"status": "error", "message": f"Syntax Error: {e}"}  
          
        # --- Test Execution ---  
          
        test_case_results = []  
        passed_count = 0  
          
        for idx, case in enumerate(q_data['test_cases']):  
            inputs = case['input']  
            expected_output = case['output']  
            case_result = {  
                "id": idx + 1,  
                "input": inputs,  
                "expected": expected_output,  
            }  
              
            try:  
                start_time = time.time()  
                # Assuming inputs is a list of arguments  
                actual_output = user_func(*inputs)  
                duration = (time.time() - start_time) * 1000  
  
                # Note: Comparing complex data structures might need a better method  
                if actual_output == expected_output:  
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
  
        # Clean up the temp file  
        os.remove(temp_file_path)  
  
        # --- Compile Final Report ---  
        final_report = {  
            "all_passed": passed_count == len(q_data['test_cases']),  
            "passed_count": passed_count,  
            "total_count": len(q_data['test_cases']),  
            "results": test_case_results  
        }  
          
        return final_report