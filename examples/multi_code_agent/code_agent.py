@@ def generate_code(
-        if code.endswith("```"):
-            code = code[:-3]
-
-        code = code.strip()
+        # Remove Markdown code fences if present
+        lines = code.strip().splitlines()
+        # Strip the opening fence (e.g., ``` or ```python)
+        if lines and lines[0].lstrip().startswith("```"):
+            lines = lines[1:]
+        # Strip the closing fence
+        if lines and lines[-1].lstrip().startswith("```"):
+            lines = lines[:-1]
+        code = "\n".join(lines).strip()
