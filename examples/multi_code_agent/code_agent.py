@@ def generate_code(
-        logger.info(f"Generated code:\n{code}")
-        if code.endswith("```"):
-            code = code[:-3]
-
-        code = code.strip()
+        logger.info(f"Generated code:\n{code}")
+        # Strip leading/trailing whitespace
+        code = code.strip()
+
+        # Remove any markdown code fence lines to avoid syntax errors
+        lines = code.splitlines()
+        filtered_lines = [line for line in lines if not line.strip().startswith("```")]
+        code = "\n".join(filtered_lines)
