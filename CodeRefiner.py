import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
import subprocess
import tempfile
import sys

load_dotenv()

class AgentState(TypedDict):
    source_code: str
    audit_report: str
    test_code: str
    test_results: str    
    iteration_count: int
    
def call_auditor(state: AgentState):
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    instruction = "You are a strict code auditor. Find errors in logic, but DO NOT write test code."
    
    response = llm.invoke([
        SystemMessage(content=instruction),
        HumanMessage(content=state["source_code"])
    ])
    
    return {"audit_report": response.content}
    
def call_coder(state: AgentState):
    print("\033[94mCoder analyzes and improves source code...\033[0m")
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    system_prompt = (
        """ You are a Python developer. Your task is to fix the source code 
        based on the audit report and any errors from testing (if this is the next iteration).
        Focus on fixing logical gaps (e.g., handling of bool types, empty lists).
        Return ONLY clean, fixed Python code, without any Markdown (```) markup and without explanations."""
    )
    
    user_msg = f"Current source code:\n{state['source_code']}\n\nAuditor's Report:\n{state['audit_report']}"
    
    if state.get("test_results"):
        user_msg += f"\n\nFailed test results:\n{state['test_results']}"

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_msg)
    ])
    
    clean_code = response.content.replace("```python", "").replace("```", "").strip()

    return {"source_code": clean_code}
    
def call_tester(state: AgentState):
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    current_iteration = state.get("iteration_count", 0) + 1

    system_prompt = (
        """ You are a Senior QA Automation Engineer.

        YOUR TASK: Write Pytest tests ONLY for the int and float types.

        CRITICAL RULES:

        1. DO NOT use Decimal or Fraction.

        2. DO NOT use any additional imports beyond 'import pytest'.

        3. Test ONLY what is actually in the source code.

        4. If a function throws a TypeError for a non-list, make sure the test checks it correctly.

        FORMAT: Pure Python code only, no ```.

        """
    )
    
    user_msg = f"Source code:\n{state['source_code']}\n\nAudit report:\n{state['audit_report']}"
    if state.get("test_results"):
        user_msg += f"\n\nPrevious errors:\n{state['test_results']}"

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_msg)
    ])
    
    clean_code = response.content.replace("```python", "").replace("```", "").strip()
    
    return {"test_code": clean_code, "iteration_count": current_iteration}
    
def call_runner(state: AgentState):
    print("\033[94mRunner starts work...\033[0m") 
    
    src = state.get("source_code", "")
    tst = state.get("test_code", "")
    
    clean_test_code = tst.replace("```python", "").replace("```", "")
    
    full_code = f"{src}\n\n{clean_test_code}"
    
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as tmp:
        tmp.write(full_code)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", tmp_path, "-v"], 
            capture_output=True, 
            text=True,
            shell=False
        )
      
        logs = result.stdout + "\n" + result.stderr
        output = f"Status: {'SUCCESS' if result.returncode == 0 else 'FAIL'}\n{logs}"
        
        print(f"\033[94mPytest completed with code {result.returncode}\033[0m")
    except Exception as e:
        output = f"Error: {str(e)}"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
            
    return {"test_results": output}
    
def should_continue(state: AgentState):
    if "Status: SUCCESS" in state.get("test_results", ""):
        print("\033[92mTests passed! We're done!.\033[0m")
        return END
    
    if state.get("iteration_count", 0) >= 3:
        print("\033[91mYou've reached your revision limit. We're closing...\033[0m")
        return END
    
    print(f"\033[94mTests failed (Attempt {state['iteration_count']}). Back to Coder!\033[0m")
    return "coder"
    
    
input_file = "input_code.py"
default_code = """
    def get_average_grade(grades):
    # Intentional error 1: Failure to check if the list is empty (throws a ZeroDivisionError)
    # Intentional error 2: Failure to validate whether the elements are numbers
    # Intentional error 3: Failure to validate the scale (ratings should be 1-6)
    total = sum(grades)
    return total / len(grades)
    """

if os.path.exists(input_file):
    with open(input_file, "r", encoding="utf-8") as f:
        source_to_test = f.read()
    print(f"\033[94mLoaded code from {input_file}\033[0m")
else:
    source_to_test = default_code
    print(f"\033[93mFile {input_file} not found. Using default example.\033[0m")
    
workflow = StateGraph(AgentState)

workflow.add_node("auditor", call_auditor)
workflow.add_node("coder", call_coder)     
workflow.add_node("tester", call_tester)
workflow.add_node("runner", call_runner)

workflow.set_entry_point("auditor")
workflow.add_edge("auditor", "coder")      
workflow.add_edge("coder", "tester")       
workflow.add_edge("tester", "runner")       

workflow.add_conditional_edges(
    "runner",
    should_continue,
    {
        "coder": "coder", 
        END: END
    }
)

app = workflow.compile()

test_input = {
    "source_code": source_to_test,
    "iteration_count": 0
}

print("\033[95mSTART OF THE PROCESS\033[0m")
final_state = app.invoke(test_input)

print(f"\n\033[95mAUDITOR'S REPORT\033[0m")
print(final_state.get("audit_report"))

print(f"\n\033[95mGENERATED TESTS (PYTEST)\033[0m")
print(final_state.get("test_code"))

print(f"\n\033[95mTEST RUN RESULT (RUNNER)\033[0m")
print(final_state.get("test_results"))

print(f"\n\033[95mCORRECTED SOURCE CODE (CODER)\033[0m")
print(final_state.get("source_code"))

if final_state.get("source_code"):
    if not os.path.exists("generated_code"):
        os.makedirs("generated_code")
    
    source_file_name = "generated_code/fixed_source_code.py"
    with open(source_file_name, "w", encoding="utf-8") as f:
        f.write(final_state["source_code"])
    
    print(f"\033[92m✅ Success! Corrected source code has been saved in: {source_file_name}\033[0m")

if final_state.get("test_code"):
    if not os.path.exists("generated_tests"):
        os.makedirs("generated_tests")
    
    test_file_name = "generated_tests/test_output.py"
    
    report_content = final_state.get("audit_report", "No auditor report.")
    full_test_file_content = f'"""\nAUDITOR\'S REPORT:\n\n{report_content}\n"""\n\n{final_state["test_code"]}'
    
    with open(test_file_name, "w", encoding="utf-8") as f:
        f.write(full_test_file_content)
    
    print(f"\033[92m✅ Success! Tests with Auditor's Report saved in: {test_file_name}\033[0m")
