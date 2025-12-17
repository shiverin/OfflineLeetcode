import json
import requests
import time
from typing import Dict, List, Any

class LeetCodeScraper:
    def __init__(self):
        self.base_url = "https://leetcode.com/graphql"
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
    
    def get_problem_details(self, title_slug: str) -> Dict[str, Any]:
        """Fetch problem details from LeetCode API"""
        query = """
        query questionData($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                questionId
                title
                titleSlug
                content
                difficulty
                exampleTestcases
                metaData
            }
        }
        """
        
        payload = {
            "query": query,
            "variables": {"titleSlug": title_slug}
        }
        
        try:
            response = requests.post(self.base_url, json=payload, headers=self.headers)
            data = response.json()
            
            if "data" in data and data["data"]["question"]:
                return data["data"]["question"]
            return None
        except Exception as e:
            print(f"Error fetching {title_slug}: {e}")
            return None
    
    def parse_test_cases(self, example_testcases: str, meta_data: str) -> List[Dict]:  
        """Parse test cases from LeetCode format"""  
        try:  
            meta = json.loads(meta_data)  
            function_name = meta.get("name", "solution")  
            params = meta.get("params", [])  
            num_params = len(params)  
    
            if num_params == 0:  
                return [], function_name  
    
            lines = example_testcases.strip().split('\n')  
            
            test_cases = []  
            lines_per_case = num_params + 1  # N inputs + 1 output  
            
            for i in range(0, len(lines), lines_per_case):  
                if i + lines_per_case > len(lines):  
                    # Avoids partial test cases at the end  
                    continue  
                
                case_input_lines = lines[i : i + num_params]  
                case_output_line = lines[i + num_params]  
                
                test_case = {"input": {}}  
                
                # Parse inputs  
                for j, param_meta in enumerate(params):  
                    param_name = param_meta.get("name", f"arg{j+1}")  
                    raw_value = case_input_lines[j]  
                    try:  
                        # Attempt to parse as JSON first (handles arrays, objects, booleans, numbers)  
                        parsed_value = json.loads(raw_value)  
                    except json.JSONDecodeError:  
                        # Fallback to string if not valid JSON  
                        parsed_value = raw_value  
                    test_case["input"][param_name] = parsed_value  
    
                # Parse expected output  
                try:  
                    test_case["output"] = json.loads(case_output_line)  
                except json.JSONDecodeError:  
                    test_case["output"] = case_output_line  
                
                test_cases.append(test_case)  
            
            return test_cases, function_name  
        except Exception as e:  
            print(f"Error parsing test cases for slug: {e}")  
            return [], "solution"
    
    def update_database(self, input_file: str, output_file: str):
        """Update the database.json file with scraped data"""
        
        # Read existing database
        with open(input_file, 'r', encoding='utf-8') as f:
            database = json.load(f)
        
        print(f"Found {len(database)} problems to process...")
        
        for problem_id, problem_data in database.items():
            slug = problem_data.get("slug")
            
            if not slug:
                print(f"Skipping problem {problem_id}: No slug found")
                continue
            
            print(f"\nProcessing: {problem_data['title']} ({slug})")
            
            # Fetch problem details
            details = self.get_problem_details(slug)
            
            if not details:
                print(f"  ❌ Failed to fetch data")
                continue
            
            # Parse test cases
            if details.get("exampleTestcases") and details.get("metaData"):
                test_cases, function_name = self.parse_test_cases(
                    details["exampleTestcases"],
                    details["metaData"]
                )
                
                if test_cases:
                    problem_data["test_cases"] = test_cases
                    problem_data["function_name"] = function_name
                    print(f"  ✓ Added {len(test_cases)} test cases")
                else:
                    print(f"  ⚠ No test cases parsed")
            
            # Update description if needed
            if details.get("content"):
                problem_data["description"] = details["content"]
                print(f"  ✓ Updated description")
            
            # Rate limiting - be nice to LeetCode servers
            time.sleep(1)
        
        # Save updated database
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=4, ensure_ascii=False)
        
        print(f"\n✅ Database updated! Saved to {output_file}")


# Example usage
if __name__ == "__main__":
    scraper = LeetCodeScraper()
    
    # Update your database
    scraper.update_database("database.json", "database_updated.json")
    
    print("\n📝 Sample test case format:")
    print(json.dumps({
        "input": {
            "nums": [2, 7, 11, 15],
            "target": 9
        },
        "output": [0, 1]
    }, indent=2))