@@ def execute_code(self, code: str) -> dict:
-                if execution_result["success"]:
-                    logger.info(f"Execution result:\n{execution_result}")
-                else:
-                    logger.error(f"Execution failed:\n{execution_result}")
+                if execution_result["success"]:
+                    logger.info(f"Execution result:\n{execution_result}")
+                else:
+                    logger.error(
+                        f"Execution failed with return code {execution_result['return_code']}.\n"
+                        f"stdout: {execution_result['stdout']}\n"
+                        f"stderr: {execution_result['stderr']}"
+                    )
                 return execution_result
