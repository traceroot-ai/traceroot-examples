import logging
from traceroot import trace

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@trace()
def logging_function_2():
    logger.info("This is an info message 2")
    logger.warning("This is a warning message 2")
-   logger.error("This is an error message 2")
+   logger.error("This is an error message 2", exc_info=True)

@trace()

def logging_function():
    logger.info("This is an info message")
    logger.warning("This is a warning message")
-   logger.error("This is an error message")
+   logger.error("This is an error message", exc_info=True)
    logging_function_2()

@trace()
def main():
    logging_function()

if __name__ == "__main__":
    main()
