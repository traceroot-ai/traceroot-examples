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
        logger.warning(f"Executing code: {code}")
        try:
            # Create a temporary file for the code
            with tempfile.NamedTemporaryFile(mode='w',
                                             suffix='.py',
                                             delete=False) as f:
                f.write(code)
                temp_file = f.name
                logger.warning(f"Created temporary file: {temp_file}")

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
                    execution_result["error"] = (
                        f"Process exited with code {result.returncode}")

                logger.info(f"Execution result: {execution_result}")
                return execution_result

            except subprocess.TimeoutExpired:
                message = (f"Code execution timed out after "
                           f"{self.timeout} seconds")
                logger.error(message)
                return {
                    "success": False,
                    "stdout": message,
                    "stderr": message,
                    "return_code": -1,
                }
            except Exception as e:
                message = f"Execution error: {str(e)}"
                logger.error(f"Execution error: {str(e)}")
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
            logger.error(message)
            return {
                "success": False,
                "stdout": "",
                "stderr": message,
                "return_code": -1,
            }


def create_execution_agent():
    return ExecutionAgent()
