@@     def generate_code(
         self,
         query: str,
         plan: str,
         historical_context: str = "",
     ) -> str:
         formatted_prompt = self.code_prompt.format(
             query=query, plan=plan, historical_context=historical_context)
         logger.info(f"CODE AGENT prompt:\n{formatted_prompt}")

         chain = self.code_prompt | self.llm
         response = chain.invoke({
             "query": query,
             "plan": plan,
             "historical_context": historical_context
         })

-        # Clean up the response to extract just the code
-        code = response.content.strip()
-        # Remove markdown code blocks if present
-        if code.startswith("```python"):
-            code = code[9:]
-        elif code.startswith("```"):
-            code = code[3:]
-
-        if code.endswith("```"):
-            code = code[:-3]
-
-        code = code.strip()
+        # Clean up the response to extract just the code and remove markdown
+        code = response.content
+        # Remove opening fences
+        if code.startswith("```python"):
+            code = code[len("```python"):]
+        elif code.startswith("```"):
+            code = code[len("```"):]
+        # Remove everything after the closing fence to drop trailing text
+        if "```" in code:
+            code = code.split("```")[0]
+        code = code.strip()

         logger.info(f"Generated code:\n{code}")
         return code