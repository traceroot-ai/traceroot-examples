import subprocess
+import re
 
 class ExecutionAgent:
     def __init__(self, timeout: int = 30):
         self.timeout = timeout
@@ -50,6 +51,14 @@ class ExecutionAgent:
         # Get code from the agent result
-        code = result.stdout
+        code = result.stdout
+
+        # Extract Python code from markdown fences to avoid syntax errors caused by explanation text
+        fence_pattern = r"```(?:python)?\n(.*?)```"
+        match = re.search(fence_pattern, code, re.DOTALL)
+        if match:
+            code = match.group(1)
+
         # Write code to temporary file for execution
         tmp_file_path = self._create_temp_file(code)
         try:
