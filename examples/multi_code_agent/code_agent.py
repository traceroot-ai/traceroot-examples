@@ def generate_code(self, query: str, plan: str, historical_context: str = "") -> str:
-        if code.endswith("```"):
-            code = code[:-3]
-
-        code = code.strip()
+        # Remove leading code fence with optional language tag
+        if code.startswith("```"):
+            fence_end = code.find("\n")
+            if fence_end != -1:
+                code = code[fence_end+1:]
+        # Remove trailing code fence
+        if code.endswith("```"):
+            code = code[:-3]
+
+        # Trim surrounding whitespace
+        code = code.strip()
