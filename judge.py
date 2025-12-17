import importlib.util
import os
import sys
import time

class Judge:
    def __init__(self, database):
        self.db = database

    def run(self, question_id):
        if question_id not in self.db:
            print(f"❌ Error: Question ID {question_id} not found.")
            return

        q_data = self.db[question_id]
        slug = q_data['slug']
        func_name = q_data['function_name']
        
        # Path to user's solution file
        file_path = f"questions/{slug}.py"
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            print(f"   Run 'python main.py gen {question_id}' to create it.")
            return

        # Dynamically import the user's module
        try:
            spec = importlib.util.spec_from_file_location("solution", file_path)
            user_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(user_module)
            
            # Get the solution class or function
            if hasattr(user_module, 'Solution'):
                sol_instance = user_module.Solution()
                user_func = getattr(sol_instance, func_name)
            else:
                print("❌ Error: Could not find class 'Solution' in file.")
                return
        except Exception as e:
            print(f"❌ Syntax Error in your code: {e}")
            return

        print(f"\n🏃 Running tests for: {q_data['title']}...")
        print("-" * 40)

        passed = 0
        total = len(q_data['test_cases'])

        for idx, case in enumerate(q_data['test_cases']):
            inputs = case['input']
            expected = case['output']
            
            try:
                start_time = time.time()
                # Unpack arguments if there are multiple, else pass single
                if len(inputs) > 1:
                    result = user_func(**inputs)
                else:
                    result = user_func(list(inputs.values())[0])
                duration = (time.time() - start_time) * 1000

                if result == expected:
                    print(f"✅ Test {idx+1}: Passed ({duration:.2f}ms)")
                    passed += 1
                else:
                    print(f"❌ Test {idx+1}: Failed")
                    print(f"   Input:    {inputs}")
                    print(f"   Expected: {expected}")
                    print(f"   Got:      {result}")

            except Exception as e:
                print(f"❌ Test {idx+1}: Runtime Error -> {e}")

        print("-" * 40)
        if passed == total:
            print(f"🎉 ACCEPTED ({passed}/{total})")
        else:
            print(f"⚠️  WRONG ANSWER ({passed}/{total})")