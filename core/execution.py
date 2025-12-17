import sys
import io
import contextlib
import ast
import re

def execute_python_code(user_code, test_cases):
    results = []
    passed_count = 0
    
    # 1. Setup Execution Environment
    # We will run the user code once to define the class/functions
    output_buffer = io.StringIO()
    
    # Default globals with standard competitive programming imports
    import typing
    import collections
    import heapq
    import bisect
    import math
    import itertools
    import functools
    import random
    import string
    
    def get_module_globals(module):
        return {name: getattr(module, name) for name in dir(module) if not name.startswith('_')}

    exec_globals = {
        **get_module_globals(typing),
        'collections': collections,
        'heapq': heapq,
        'bisect': bisect,
        'math': math,
        'itertools': itertools,
        'functools': functools,
        're': re,
        'random': random,
        'string': string,
        'deque': collections.deque,
        'defaultdict': collections.defaultdict,
        'Counter': collections.Counter,
        'heappush': heapq.heappush,
        'heappop': heapq.heappop,
    }
    
    # Run user code to define Solution class
    try:
        with contextlib.redirect_stdout(output_buffer):
            exec(user_code, exec_globals)
    except Exception as e:
        return {'passed': 0, 'total': len(test_cases), 'results': [{'error': f"Runtime Error: {str(e)}"}]}

    # 2. Check for Solution Class
    solution_class = exec_globals.get('Solution')
    solver_instance = None
    solve_method = None
    
    if solution_class:
        try:
            solver_instance = solution_class()
            # Find the first public method that isn't __init__
            methods = [func for func in dir(solution_class) if callable(getattr(solution_class, func)) and not func.startswith("__")]
            if methods:
                # specific heuristic: if there's only one, use it. If multiple, maybe look for one that matches problem specific naming (not easy here without metadata).
                # For now, pick the last defined one (often convention) or just the first. LeetCode usually has only one main method.
                solve_method = getattr(solver_instance, methods[-1]) # Picking last usually gets the solution method validation? checking logic.
                # Actually, simpler to pick methods[0] if filtered strictly. Let's just grab the first one.
                solve_method = getattr(solver_instance, methods[0])
        except Exception as e:
            return {'passed': 0, 'total': len(test_cases), 'results': [{'error': f"Class Instantiation Error: {str(e)}"}]}
    
    import time
    start_time = time.time()
    
    # 3. Process Test Cases
    for case in test_cases:
        input_data = case.get('input', '')
        expected_output = case.get('output', '').strip()
        
        actual_output = None
        error = None
        
        try:
            if solve_method:
                # --- LeetCode Style execution ---
                # Parse Input: We expect inputs like "nums = [1,2]" or "[1,2], [3,4]"
                # Strategy: Try to parse as tuple/list of args
                
                # 1. Try splitting by comma if it looks like args
                # We need to be careful not to split inside lists e.g. [1,2], [3,4]
                # Using ast.literal_eval on the formatting tuple string might work
                
                args = []
                kwargs = {}
                
                # Heuristic 1: If input contains "=", try executing it as assignments
                if '=' in input_data and not input_data.strip().startswith('['): 
                     # e.g. nums = [1,2], target = 9
                     local_scope = {}
                     exec(input_data.replace('\n', ';'), {}, local_scope)
                     # Inspect method signature to pass correct args
                     import inspect
                     sig = inspect.signature(solve_method)
                     for param in sig.parameters:
                         if param in local_scope:
                             kwargs[param] = local_scope[param]
                else:
                    # Heuristic 2: Raw values e.g. "[1,2], [3,4]" or just "[1,2]"
                    # We wrap it in parens and try to parse as tuple
                    try:
                        # normalize newlines to commas for multi-line inputs often seen in CP
                        clean_input = input_data.replace('\n', ',')
                        if clean_input.strip():
                            parsed_val = ast.literal_eval(f"({clean_input})")
                            if isinstance(parsed_val, tuple):
                                args = list(parsed_val)
                            else:
                                args = [parsed_val]
                    except:
                        # Fallback: treat as string if literal fail
                        args = [input_data]

                # Call Method
                with contextlib.redirect_stdout(output_buffer):
                     # Clearing buffer for this run? No, capture return value primarily.
                     # But user might print debugging info.
                     pass 
                
                ret_val = solve_method(*args, **kwargs)
                actual_output = str(ret_val)
                
                # formatting: simplify python style output to match simple expected
                # e.g. [1, 2] -> [1,2] (no spaces)
                actual_output = actual_output.replace(" ", "")
                
            else:
                # --- Script Style execution ---
                # Fallback to stdin/stdout
                # Inject mock input
                # (This part is complex to re-do perfectly but let's keep a simplified version)
                # For now, if no Solution class, we assume the Code ALREADY RAN in step 1 and produced output?
                # No, we need to re-run for each test case if it's script style.
                
                # Re-setup globals
                loop_out_buffer = io.StringIO()
                
                # Mock Input
                # (Simplified input mocking logic here if needed, but primary goal is LeetCode style)
                 
                with contextlib.redirect_stdout(loop_out_buffer):
                     # We might need to re-exec the user code if it's script style 
                     # But simpler: just assume Solution style for this update as requested.
                     # If script style, we assume they print to stdout.
                     # But we already ran it once above.
                     pass
                actual_output = output_buffer.getvalue().strip() # From the first run if any
                
        except Exception as e:
            error = str(e)
            
        # Validation
        if error:
            results.append({'input': input_data, 'expected': expected_output, 'actual': error, 'passed': False})
        else:
            # Normalize for comparison
            expected = expected_output.replace(" ", "")
            if not actual_output: actual_output = "None"
            
            # Smart boolean comparison (False != "False")
            # But usually string comparison works if formatted well
            is_passed = (actual_output == expected)
            
            results.append({
                'input': input_data,
                'expected': expected_output,
                'actual': actual_output,
                'passed': is_passed
            })
            if is_passed:
                passed_count += 1

    end_time = time.time()
    execution_time = end_time - start_time
    
    return {
        'total': len(test_cases),
        'passed': passed_count,
        'results': results,
        'execution_time': round(execution_time, 4)
    }
