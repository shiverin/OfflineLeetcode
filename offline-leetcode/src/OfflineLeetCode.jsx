import React, { useState, useEffect } from 'react';
import { Play, Check, X, Code, BookOpen, List } from 'lucide-react';
import './index.css'; // <-- this is required for Tailwind styles

const PROBLEMS = {
  twoSum: {
    id: 'twoSum',
    title: 'Two Sum',
    difficulty: 'Easy',
    description: `Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order.`,
    examples: [
      { input: 'nums = [2,7,11,15], target = 9', output: '[0,1]', explanation: 'Because nums[0] + nums[1] == 9, we return [0, 1].' },
      { input: 'nums = [3,2,4], target = 6', output: '[1,2]', explanation: '' },
      { input: 'nums = [3,3], target = 6', output: '[0,1]', explanation: '' }
    ],
    template: `def twoSum(nums, target):
    # Write your code here
    pass`,
    testCases: [
      { input: [[2, 7, 11, 15], 9], output: [0, 1] },
      { input: [[3, 2, 4], 6], output: [1, 2] },
      { input: [[3, 3], 6], output: [0, 1] },
      { input: [[1, 5, 3, 7, 9], 12], output: [2, 4] }
    ],
    functionName: 'twoSum'
  },
  reverseString: {
    id: 'reverseString',
    title: 'Reverse String',
    difficulty: 'Easy',
    description: `Write a function that reverses a string. The input string is given as an array of characters s.

You must do this by modifying the input array in-place with O(1) extra memory.`,
    examples: [
      { input: 's = ["h","e","l","l","o"]', output: '["o","l","l","e","h"]', explanation: '' },
      { input: 's = ["H","a","n","n","a","h"]', output: '["h","a","n","n","a","H"]', explanation: '' }
    ],
    template: `def reverseString(s):
    # Write your code here (modify s in-place)
    pass`,
    testCases: [
      { input: [['h', 'e', 'l', 'l', 'o']], output: ['o', 'l', 'l', 'e', 'h'] },
      { input: [['H', 'a', 'n', 'n', 'a', 'h']], output: ['h', 'a', 'n', 'n', 'a', 'H'] }
    ],
    functionName: 'reverseString',
    checkInPlace: true
  },
  maxSubArray: {
    id: 'maxSubArray',
    title: 'Maximum Subarray',
    difficulty: 'Medium',
    description: `Given an integer array nums, find the subarray with the largest sum, and return its sum.`,
    examples: [
      { input: 'nums = [-2,1,-3,4,-1,2,1,-5,4]', output: '6', explanation: 'The subarray [4,-1,2,1] has the largest sum 6.' },
      { input: 'nums = [1]', output: '1', explanation: '' },
      { input: 'nums = [5,4,-1,7,8]', output: '23', explanation: '' }
    ],
    template: `def maxSubArray(nums):
    # Write your code here
    pass`,
    testCases: [
      { input: [[-2, 1, -3, 4, -1, 2, 1, -5, 4]], output: 6 },
      { input: [[1]], output: 1 },
      { input: [[5, 4, -1, 7, 8]], output: 23 },
      { input: [[-1, -2, -3, -4]], output: -1 }
    ],
    functionName: 'maxSubArray'
  },
  isPalindrome: {
    id: 'isPalindrome',
    title: 'Valid Palindrome',
    difficulty: 'Easy',
    description: `A phrase is a palindrome if, after converting all uppercase letters into lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward. Alphanumeric characters include letters and numbers.

Given a string s, return true if it is a palindrome, or false otherwise.`,
    examples: [
      { input: 's = "A man, a plan, a canal: Panama"', output: 'true', explanation: 'After removing non-alphanumeric chars: "amanaplanacanalpanama" is a palindrome.' },
      { input: 's = "race a car"', output: 'false', explanation: '' },
      { input: 's = " "', output: 'true', explanation: '' }
    ],
    template: `def isPalindrome(s):
    # Write your code here
    pass`,
    testCases: [
      { input: ['A man, a plan, a canal: Panama'], output: true },
      { input: ['race a car'], output: false },
      { input: [' '], output: true },
      { input: ['0P'], output: false }
    ],
    functionName: 'isPalindrome'
  }
};

const OfflineLeetCode = () => {
  const [selectedProblem, setSelectedProblem] = useState('twoSum');
  const [code, setCode] = useState('');
  const [results, setResults] = useState(null);
  const [showSidebar, setShowSidebar] = useState(true);
  const [activeTab, setActiveTab] = useState('description');

  const problem = PROBLEMS[selectedProblem];

  useEffect(() => {
    setCode(problem.template);
    setResults(null);
  }, [selectedProblem]);

  const runCode = () => {
    try {
      const testResults = problem.testCases.map((testCase, index) => {
        try {
          const func = new Function('return ' + code)();
          const funcToTest = func[problem.functionName];
          
          if (!funcToTest) {
            throw new Error(`Function ${problem.functionName} not found`);
          }

          let result;
          if (problem.checkInPlace) {
            const inputCopy = JSON.parse(JSON.stringify(testCase.input[0]));
            funcToTest(inputCopy);
            result = inputCopy;
          } else {
            result = funcToTest(...testCase.input);
          }

          const passed = JSON.stringify(result) === JSON.stringify(testCase.output);

          return {
            index: index + 1,
            passed,
            input: testCase.input,
            expected: testCase.output,
            actual: result,
            error: null
          };
        } catch (err) {
          return {
            index: index + 1,
            passed: false,
            input: testCase.input,
            expected: testCase.output,
            actual: null,
            error: err.message
          };
        }
      });

      const allPassed = testResults.every(r => r.passed);
      setResults({ testResults, allPassed });
    } catch (err) {
      setResults({
        testResults: [],
        allPassed: false,
        error: `Code Error: ${err.message}`
      });
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'Easy': return 'text-green-600';
      case 'Medium': return 'text-yellow-600';
      case 'Hard': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {showSidebar && (
        <div className="w-64 bg-white border-r border-gray-200 overflow-y-auto">
          <div className="p-4 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-800">Problems</h2>
          </div>
          <div className="p-2">
            {Object.values(PROBLEMS).map(prob => (
              <button
                key={prob.id}
                onClick={() => setSelectedProblem(prob.id)}
                className={`w-full text-left p-3 rounded-lg mb-2 transition-colors ${
                  selectedProblem === prob.id
                    ? 'bg-blue-50 border border-blue-200'
                    : 'hover:bg-gray-50'
                }`}
              >
                <div className="font-medium text-gray-800">{prob.title}</div>
                <div className={`text-sm ${getDifficultyColor(prob.difficulty)}`}>
                  {prob.difficulty}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="bg-white border-b border-gray-200 p-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setShowSidebar(!showSidebar)}
              className="p-2 hover:bg-gray-100 rounded"
            >
              <List size={20} />
            </button>
            <h1 className="text-xl font-bold text-gray-800">{problem.title}</h1>
            <span className={`text-sm font-medium ${getDifficultyColor(problem.difficulty)}`}>
              {problem.difficulty}
            </span>
          </div>
          <button
            onClick={runCode}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Play size={16} />
            Run Code
          </button>
        </div>

        <div className="flex-1 flex overflow-hidden">
          <div className="w-1/2 flex flex-col border-r border-gray-200">
            <div className="flex border-b border-gray-200">
              <button
                onClick={() => setActiveTab('description')}
                className={`px-4 py-2 font-medium ${
                  activeTab === 'description'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                <div className="flex items-center gap-2">
                  <BookOpen size={16} />
                  Description
                </div>
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6 bg-white">
              <div className="prose max-w-none">
                <p className="text-gray-700 whitespace-pre-line mb-6">{problem.description}</p>
                
                <h3 className="text-lg font-semibold text-gray-800 mb-3">Examples:</h3>
                {problem.examples.map((example, idx) => (
                  <div key={idx} className="mb-4 p-4 bg-gray-50 rounded-lg">
                    <div className="font-medium text-gray-700 mb-1">Example {idx + 1}:</div>
                    <div className="text-sm">
                      <div className="mb-1"><span className="font-medium">Input:</span> {example.input}</div>
                      <div className="mb-1"><span className="font-medium">Output:</span> {example.output}</div>
                      {example.explanation && (
                        <div><span className="font-medium">Explanation:</span> {example.explanation}</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="w-1/2 flex flex-col">
            <div className="flex-1 flex flex-col">
              <div className="flex items-center justify-between p-2 bg-gray-100 border-b border-gray-200">
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Code size={16} />
                  <span>Python</span>
                </div>
              </div>
              
              <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                className="flex-1 p-4 font-mono text-sm bg-gray-900 text-gray-100 resize-none focus:outline-none"
                spellCheck="false"
              />
            </div>

            {results && (
              <div className="h-64 overflow-y-auto border-t border-gray-200 bg-white">
                <div className={`p-4 border-b ${results.allPassed ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
                  <div className="flex items-center gap-2 font-semibold">
                    {results.allPassed ? (
                      <>
                        <Check className="text-green-600" size={20} />
                        <span className="text-green-800">All Tests Passed!</span>
                      </>
                    ) : (
                      <>
                        <X className="text-red-600" size={20} />
                        <span className="text-red-800">Some Tests Failed</span>
                      </>
                    )}
                  </div>
                </div>

                {results.error && (
                  <div className="p-4 text-red-600 text-sm font-mono">{results.error}</div>
                )}

                <div className="p-4">
                  {results.testResults.map((result, idx) => (
                    <div key={idx} className="mb-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
                      <div className="flex items-center gap-2 mb-2">
                        {result.passed ? (
                          <Check className="text-green-600" size={16} />
                        ) : (
                          <X className="text-red-600" size={16} />
                        )}
                        <span className="font-semibold text-gray-700">Test Case {result.index}</span>
                      </div>
                      
                      <div className="text-sm space-y-1 font-mono">
                        <div><span className="text-gray-600">Input:</span> {JSON.stringify(result.input)}</div>
                        <div><span className="text-gray-600">Expected:</span> {JSON.stringify(result.expected)}</div>
                        <div><span className="text-gray-600">Actual:</span> {JSON.stringify(result.actual)}</div>
                        {result.error && (
                          <div className="text-red-600">Error: {result.error}</div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default OfflineLeetCode;