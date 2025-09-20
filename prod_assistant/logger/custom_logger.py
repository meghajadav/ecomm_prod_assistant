import os
import logging
from datetime import datetime
import structlog

class CustomLogger:
    def __init__(self, log_dir="logs"):
        '''
        create the logs directory with the default name as logs if not provided.
        log_file is created with the timestamp.log and the log file for that particular date and time is ready
        for the logs to write
        '''
        # Ensure logs directory exists
        self.logs_dir = os.path.join(os.getcwd(), log_dir)
        os.makedirs(self.logs_dir, exist_ok=True)

        # Timestamped log file (for persistence)
        log_file = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
        self.log_file_path = os.path.join(self.logs_dir, log_file)

    def get_logger(self, name=__file__):
        logger_name = os.path.basename(name)# It will take the name of the .py file to log any error or info.

        # Configure logging for console + file (both JSON)
        file_handler = logging.FileHandler(self.log_file_path) #it handles the file in which the logs to be written 
        file_handler.setLevel(logging.INFO)# it sets the level INFO and below that to be captured like info,error, critical
        file_handler.setFormatter(logging.Formatter("%(message)s"))  # Raw JSON lines the simple message without formatting

        console_handler = logging.StreamHandler()# for printing Info or error on the console
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(message)s"))

        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",  # Structlog will handle JSON rendering
            handlers=[console_handler, file_handler]
        )

        # Configure structlog for JSON structured logging
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
                structlog.processors.add_log_level,
                structlog.processors.EventRenamer(to="event"),
                structlog.processors.JSONRenderer()
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),# it will give the structured log integrated with python 
            cache_logger_on_first_use=True,
        )
         ##''' If you pass cache_logger_on_first_use=True, structlog: Builds the logger the first time you request it Then reuses the same logger instance every time afterward This means:

##Faster performance (no rebuilding loggers repeatedly)

##Consistency (same processors, same config everywhere)

##You won’t accidentally get slightly different loggers if something changes mid-run 
#        )'''
        return structlog.get_logger(logger_name)


# # --- Usage Example ---
# if __name__ == "__main__":
#     logger = CustomLogger().get_logger(__file__)
#     logger.info("User uploaded a file", user_id=123, filename="report.pdf")
#     logger.error("Failed to process PDF", error="File not found", user_id=123)