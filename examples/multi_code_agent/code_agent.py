@@ def generate_code(self, query: str, plan: str, historical_context: str = "") -> str:
-        if code.endswith("```"):
-            code = code[:-3]
-
-        code = code.strip()
+        # Remove any markdown code fences that may wrap the generated code
+        lines = code.splitlines()
+        # Strip leading fence
+        if lines and lines[0].strip().startswith("```"):
+            lines = lines[1:]
+        # Strip trailing fence
+        if lines and lines[-1].strip().startswith("```"):
+            lines = lines[:-1]
+        # Reconstruct code and trim whitespace
+        code = "\n".join(lines).strip()
         return code
