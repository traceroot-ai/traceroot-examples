@@
-    @traceroot.trace()
-    def should_retry(self, state: dict) -> None:
-        """Stub: decide whether to retry"""
-        pass
+    @traceroot.trace()
+    def should_retry(self, state: dict) -> bool:
+        """
+        Decide whether to retry based on retry_count and max_retries in the state.
+        """
+        retry_count = state.get("retry_count", 0)
+        max_retries = state.get("max_retries", 0)
+        will_retry = retry_count < max_retries
+        logger.info(
+            f"should_retry check: retry_count={retry_count}, max_retries={max_retries}, will_retry={will_retry}"
+        )
+        return will_retry
