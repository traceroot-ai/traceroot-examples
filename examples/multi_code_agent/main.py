    @traceroot.trace()
    def should_retry(self, state: AgentState) -> str:
        """Determine if we should retry after a failed execution"""
        # Only retry if:
        # 1. This was a coding task
        # 2. Execution failed
        # 3. We haven't exceeded max retries
        if (state["is_coding"]
                and state["execution_result"].get("success") is False
                and state["retry_count"] < state["max_retries"]):
-            logger.error(f"Execution failed on attempt "
-                        f"{state['retry_count'] + 1}. Retrying...")
+            # Combine into a single f-string so the attempt number is logged correctly
+            logger.error(f"Execution failed on attempt {state['retry_count'] + 1}. Retrying...")
             return "retry"
         else:
             return "end"
