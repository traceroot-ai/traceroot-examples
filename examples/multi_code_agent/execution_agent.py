import os
import subprocess
import sys
import tempfile
from typing import Any

import traceroot

logger = traceroot.get_logger()


class ExecutionAgent:

    def __init__(self):
        self.timeout = 30  # 30 seconds timeout

    @traceroot.trace()
    def execute_code(
        self,
        query: str,
        plan: str,
        code: str,
        historical_context: str = "",
    ) -> dict[str, Any]:
        """Execute Python code safely and return results"""
        try:
            # Create a temporary file for the code
            with tempfile.NamedTemporaryFile(mode='w',
                                             suffix='.py',
                                             delete=False) as f:
                f.write(code)
                temp_file = f.name
                logger.debug(f"Created temporary file {temp_file} for code execution")
                logger.info("Executing code for query: %s, plan: %s", query, plan)
                logger.debug("Code snippet:\n%s", code)

            try:
                # Execute the code using subprocess for safety
                result = subprocess.run([sys.executable, temp_file],
                                        capture_output=True,
                                        text=True,
                                        timeout=self.timeout,
                                        cwd=os.path.dirname(temp_file))

                execution_result = {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode,
                }

                if result.returncode != 0:
                    logger.error("Code execution failed with return code %d", result.returncode)
                    logger.error("stdout: %s", result.stdout)
                    logger.error("stderr: %s", result.stderr)
                    # Include code snippet for debugging
                    logger.debug("Failed code snippet:\n%s", code)
                else:
                    logger.info("Execution succeeded with stdout: %s", result.stdout)

                return execution_result

            except subprocess.TimeoutExpired as e:
                message = f"Code execution timed out after {self.timeout} seconds"
                logger.error(message + ". Code snippet:\n%s", code)
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": message,
                    "return_code": -1,
                }
            except Exception as e:
                message = f"Execution error: {str(e)}"
                logger.exception("Unexpected error during code execution for query: %s", query)
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": message,
                    "return_code": -1,
                }
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file)
                except Exception:
                    pass

        except Exception as e:
            message = f"Failed to create temporary file: {str(e)}"
            logger.exception(message)
            return {
                "success": False,
                "stdout": "",
                "stderr": message,
                "return_code": -1,
            }


def create_execution_agent():
    return ExecutionAgent()