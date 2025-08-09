import time

import traceroot

logger = traceroot.get_logger()

@traceroot.trace()
def logging_function_2():
    logger.info("This is an info message 2")
    logger.warning("This is a warning message 2")
    # Include exception info for better debugging
    logger.error("This is an error message 2", exc_info=True)

@traceroot.trace()
def logging_function():
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    # Include exception info for better debugging
    logger.error("This is an error message", exc_info=True)
    logging_function_2()

@traceroot.trace()
def main():
    logger.debug("Main function started")
    time.sleep(1)
    logging_function()
    logger.debug("Main function completed")

if __name__ == "__main__":
    main()