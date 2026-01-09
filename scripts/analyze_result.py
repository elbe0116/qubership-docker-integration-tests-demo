# Copyright 2024-2025 NetCracker Technology Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import xml.etree.ElementTree as ET
from enum import Enum
from pathlib import Path

space = "\n**********************************************************************************************************\n"


class Status(str, Enum):
    PASS = "passed"
    FAIL = "failed"
    SKIP = "skipped"
    ERROR = "error"


def analyze_result():
    """Analyze pytest JUnit XML results and generate a summary file."""
    junit_xml_path = Path("./output/junit.xml")
    
    try:
        tree = ET.parse(junit_xml_path)
        root = tree.getroot()
    except FileNotFoundError:
        logging.error(f"JUnit XML file not found at: {junit_xml_path}")
        return
    except ET.ParseError as e:
        logging.error(f"Exception occurred while parsing JUnit XML: {e}")
        return
    except Exception as e:
        logging.error(f"Exception occurred while opening test result file: {e}")
        return

    logging.debug("Start parsing the pytest JUnit XML test result")
    
    # Initialize counters
    total_tests = 0
    total_passed = 0
    total_failed = 0
    total_skipped = 0
    total_errors = 0
    total_time = 0.0
    
    result_str = ""
    
    # Process testsuites
    testsuites = root.findall('.//testsuite')
    if not testsuites:
        # Root element might be testsuite directly
        testsuites = [root] if root.tag == 'testsuite' else []
    
    for testsuite in testsuites:
        suite_name = testsuite.get('name', 'Unknown Suite')
        suite_tests = int(testsuite.get('tests', 0))
        suite_failures = int(testsuite.get('failures', 0))
        suite_errors = int(testsuite.get('errors', 0))
        suite_skipped = int(testsuite.get('skipped', 0))
        suite_time = float(testsuite.get('time', 0))
        suite_passed = suite_tests - suite_failures - suite_errors - suite_skipped
        
        total_tests += suite_tests
        total_passed += suite_passed
        total_failed += suite_failures
        total_errors += suite_errors
        total_skipped += suite_skipped
        total_time += suite_time
        
        result_str += f"Test Suite: {suite_name}\t|\tPassed: {suite_passed}\t|\tFailed: {suite_failures}\t|\tErrors: {suite_errors}\t|\tSkipped: {suite_skipped}\n"
        result_str += space
        
        # Process individual test cases
        testcases = testsuite.findall('testcase')
        if testcases:
            result_str += "Test cases:\n"
            for testcase in testcases:
                tc_name = testcase.get('name', 'Unknown Test')
                tc_classname = testcase.get('classname', '')
                tc_time = float(testcase.get('time', 0))
                tc_time_ms = int(tc_time * 1000)  # Convert to milliseconds
                
                # Determine status
                failure = testcase.find('failure')
                error = testcase.find('error')
                skipped = testcase.find('skipped')
                
                if failure is not None:
                    status = "FAIL"
                    result_str += f"\t{tc_name}\t|\tStatus: '{status}'|\tDuration: {tc_time_ms}ms\n"
                    failure_message = failure.get('message', '')
                    failure_text = failure.text or ''
                    if failure_message:
                        result_str += f"\t\tFailure message: {failure_message}\n"
                    if failure_text.strip():
                        # Truncate long stack traces
                        lines = failure_text.strip().split('\n')
                        if len(lines) > 10:
                            truncated = '\n'.join(lines[:10]) + '\n\t\t... (truncated)'
                        else:
                            truncated = failure_text.strip()
                        result_str += f"\t\tDetails:\n\t\t{truncated.replace(chr(10), chr(10) + chr(9) + chr(9))}\n"
                elif error is not None:
                    status = "ERROR"
                    result_str += f"\t{tc_name}\t|\tStatus: '{status}'|\tDuration: {tc_time_ms}ms\n"
                    error_message = error.get('message', '')
                    if error_message:
                        result_str += f"\t\tError message: {error_message}\n"
                elif skipped is not None:
                    status = "SKIP"
                    result_str += f"\t{tc_name}\t|\tStatus: '{status}'|\tDuration: {tc_time_ms}ms\n"
                    skip_message = skipped.get('message', '')
                    if skip_message:
                        result_str += f"\t\tSkip reason: {skip_message}\n"
                else:
                    status = "PASS"
                    result_str += f"\t{tc_name}\t|\tStatus: '{status}'|\tDuration: {tc_time_ms}ms\n"
                
                result_str += "\n"
        
        result_str += space
    
    # Summary
    result_str += f"\nSUMMARY:\n"
    result_str += f"Total Tests: {total_tests}\n"
    result_str += f"Passed: {total_passed}\n"
    result_str += f"Failed: {total_failed}\n"
    result_str += f"Errors: {total_errors}\n"
    result_str += f"Skipped: {total_skipped}\n"
    result_str += f"Total Time: {total_time:.2f}s\n"
    result_str += space
    
    if total_failed > 0 or total_errors > 0:
        result_str += "RESULT: TESTS FAILED\n"
    else:
        result_str += "RESULT: TESTS PASSED\n"
    
    # Write result file
    output_path = Path('./output/result.txt')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as file_write:
        file_write.write(result_str)
    
    logging.debug("The result file has been saved")
    print(result_str)


if __name__ == "__main__":
    analyze_result()
