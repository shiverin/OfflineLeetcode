import React, { useState, useEffect } from 'react';  
import { Play, Check, X, Code, BookOpen, List, Loader2 } from 'lucide-react';  
import './index.css';  
  
// Base URL for your FastAPI backend  
const API_URL = 'http://127.0.0.1:8000';  
  
const OnlineLeetCode = () => {  
  // State for the list of all problems  
  const [problems, setProblems] = useState([]);  
  // State for the currently selected problem's full data  
  const [currentProblem, setCurrentProblem] = useState(null);  
  // State for the ID of the selected problem  
  const [selectedProblemId, setSelectedProblemId] = useState(null);  
  
  const [code, setCode] = useState('');  
  const [results, setResults] = useState(null);  
  const [isLoading, setIsLoading] = useState(false);  
  const [showSidebar, setShowSidebar] = useState(true);  
  
  // --- Data Fetching Effects ---  
  
  // 1. Fetch the list of all problems when the component first loads  
  useEffect(() => {  
    const fetchProblems = async () => {  
      try {  
        const response = await fetch(`${API_URL}/api/questions`);  
        const data = await response.json();  
        setProblems(data);  
        // Automatically select the first problem  
        if (data.length > 0) {  
          setSelectedProblemId(data[0].id);  
        }  
      } catch (error) {  
        console.error("Failed to fetch problems:", error);  
        // Handle error (e.g., show an error message on the page)  
      }  
    };  
    fetchProblems();  
  }, []); // Empty dependency array means this runs only once on mount  
  
  // 2. Fetch the full details of the selected problem whenever `selectedProblemId` changes  
  useEffect(() => {  
    if (!selectedProblemId) return;  
  
    const fetchProblemDetails = async () => {  
      setIsLoading(true);  
      setResults(null); // Clear previous results  
      try {  
        const response = await fetch(`${API_URL}/api/questions/${selectedProblemId}`);  
        const data = await response.json();  
        setCurrentProblem(data);  
        // Set the code template from the backend  
        setCode(data.template || `def ${data.function_name}():\n    # Write your code here\n    pass`);  
      } catch (error) {  
        console.error(`Failed to fetch details for problem ${selectedProblemId}:`, error);  
      } finally {  
        setIsLoading(false);  
      }  
    };  
  
    fetchProblemDetails();  
  }, [selectedProblemId]);  
  
  
  // --- Event Handlers ---  
  
  // 3. This function now calls the backend instead of running JS in the browser  
  const handleRunCode = async () => {  
    if (!currentProblem) return;  
  
    setIsLoading(true);  
    setResults(null);  
  
    try {  
        const response = await fetch(`${API_URL}/api/questions/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            code: code, 
            question_id: selectedProblemId 
        }),
        });
  
      const resultData = await response.json();  
      setResults(resultData);  
  
    } catch (error) {  
      console.error("Failed to run code:", error);  
      setResults({ status: 'error', message: 'Network error: Could not connect to the backend.' });  
    } finally {  
      setIsLoading(false);  
    }  
  };  
  
  // Helper for difficulty color - kept from your original code  
  const difficultyColorMap = {  
    Easy: 'text-green-600',  
    Medium: 'text-yellow-600',  
    Hard: 'text-red-600',  
  };  
  
  // --- Render Logic ---  
  
  // Display a loading spinner while fetching problem details  
  if (!currentProblem) {  
    return (  
      <div className="flex items-center justify-center h-screen bg-gray-50">  
        <Loader2 className="animate-spin text-gray-400" size={48} />  
      </div>  
    );  
  }  
  
  return (  
    <div className="flex h-screen bg-gray-50">  
      {showSidebar && (  
        <div className="w-64 bg-white border-r border-gray-200 overflow-y-auto">  
          <div className="p-4 border-b border-gray-200">  
            <h2 className="text-xl font-bold text-gray-800">Problems</h2>  
          </div>  
          <div className="p-2">  
            {problems.map(prob => (  
              <button  
                key={prob.id}  
                onClick={() => setSelectedProblemId(prob.id)}  
                className={`w-full text-left p-3 rounded-lg mb-2 transition-colors ${  
                  selectedProblemId === prob.id  
                    ? 'bg-blue-50 border border-blue-200'  
                    : 'hover:bg-gray-50'  
                }`}  
              >  
                <div className="font-medium text-gray-800">{prob.title}</div>  
                <div className={`text-sm ${difficultyColorMap[prob.difficulty] || 'text-gray-600'}`}>  
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
            <h1 className="text-xl font-bold text-gray-800">{currentProblem.title}</h1>  
            <span className={`text-sm font-medium ${difficultyColorMap[currentProblem.difficulty] || 'text-gray-600'}`}>  
              {currentProblem.difficulty}  
            </span>  
          </div>  
          <button  
            onClick={handleRunCode}  
            disabled={isLoading}  
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-400"  
          >  
            {isLoading ? <Loader2 className="animate-spin" size={16} /> : <Play size={16} />}  
            {isLoading ? 'Running...' : 'Run Code'}  
          </button>  
        </div>  
  
        <div className="flex-1 flex overflow-hidden">  
          {/* Description Panel */}  
          <div className="w-1/2 flex flex-col border-r border-gray-200">  
             <div className="flex border-b border-gray-200">  
              <div className="px-4 py-2 font-medium text-blue-600 border-b-2 border-blue-600 flex items-center gap-2">  
                  <BookOpen size={16} />  
                  Description  
              </div>  
            </div>  
            {/* Use dangerouslySetInnerHTML to render the HTML from the backend */}  
            <div  
              className="flex-1 overflow-y-auto p-6 bg-white prose max-w-none"  
              dangerouslySetInnerHTML={{ __html: currentProblem.description }}  
            />  
          </div>  
  
          {/* Code and Results Panel */}  
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
  
            {/* Results Display */}  
            {results && (  
              <div className="h-64 overflow-y-auto border-t border-gray-200 bg-white">  
                {/* Overall Status Header */}  
                <div className={`p-4 border-b ${results.all_passed ? 'bg-green-50' : 'bg-red-50'}`}>  
                  <div className="flex items-center gap-2 font-semibold">  
                    {results.all_passed ? (  
                      <><Check className="text-green-600" size={20} /> <span className="text-green-800">All Tests Passed!</span></>  
                    ) : (  
                      <><X className="text-red-600" size={20} /> <span className="text-red-800">Some Tests Failed</span></>  
                    )}  
                  </div>  
                   {results.message && <div className="mt-2 text-red-600 text-sm font-mono">{results.message}</div>}  
                </div>  
                  
                {/* Individual Test Case Results */}  
                {results.results && (  
                  <div className="p-4">  
                    {results.results.map((result) => (  
                      <div key={result.id} className="mb-4 p-3 bg-gray-50 rounded-lg border border-gray-200">  
                        <div className="flex items-center gap-2 mb-2">  
                          {result.passed ? <Check className="text-green-600" size={16} /> : <X className="text-red-600" size={16} />}  
                          <span className="font-semibold text-gray-700">Test Case {result.id}</span>  
                        </div>  
                        <div className="text-sm space-y-1 font-mono">  
                          <div><span className="text-gray-600">Input:</span> {JSON.stringify(result.input)}</div>  
                          <div><span className="text-gray-600">Expected:</span> {JSON.stringify(result.expected)}</div>  
                          <div><span className="text-gray-600">Actual:</span> {JSON.stringify(result.actual)}</div>  
                          {result.error && <div className="text-red-600">Error: {result.error}</div>}  
                        </div>  
                      </div>  
                    ))}  
                  </div>  
                )}  
              </div>  
            )}  
          </div>  
        </div>  
      </div>  
    </div>  
  );  
};  
  
export default OnlineLeetCode;