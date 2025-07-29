--- a/examples/multi_code_agent/code_agent.py
+++ b/examples/multi_code_agent/code_agent.py
@@ def generate_code(self,
-        code = response
-
-        if code.endswith("```"):
-            code = code[:-3]
-
-        code = code.strip()
-        return code
+        code = response
+
+        # Remove any trailing markdown fence markers
+        if code.endswith("```"):
+            code = code[: -3]
+
+        # Strip whitespace
+        code = code.strip()
+
+        # Filter out any lines that are solely markdown fences
+        lines = code.splitlines()
+        filtered_lines = [l for l in lines if l.strip() != '```']
+        code = "\n".join(filtered_lines)
+
+        return code
