import toml
import os
import sys
import logging
import inspect
from colorlog import ColoredFormatter

file_handler = logging.FileHandler('superwrapper.log')
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)


class Logging:
    def __init__(self, debug, relative_path=None):
        
        # Initialize class variables
        self.debug = debug
        self.relative_path = relative_path

        # Set the log level for the logger
        LOG_LEVEL = logging.DEBUG

        # Define a log format with color support
        LOGFORMAT = ('%(log_color)s%(asctime)s.%(msecs)03d %(levelname)s:  %(file)s -> %(function)s: %(message)s')
        formatter = ColoredFormatter(LOGFORMAT)

        # Set the root logger level to the debug level
        logging.root.setLevel(LOG_LEVEL)

        # Create a stream handler (for console output) and set its level and formatter
        stream = logging.StreamHandler()
        stream.setLevel(LOG_LEVEL)
        stream.setFormatter(formatter)

        # Initialize the logger
        self.logger = logging.getLogger('pythonConfig')
        self.extra_log = {'file': '', 'function': ''}
        standard_formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s: %(file)s -> %(function)s: %(message)s', 
                                            datefmt='%Y-%m-%d %H:%M:%S')

        # Example file handler (commented out because 'file_handler' and 'console_handler' are not defined)
        file_handler.setFormatter(standard_formatter)

        # Add handlers only if debugging is enabled
        if self.debug:
            self.logger.addHandler(file_handler)
            # self.logger.addHandler(console_handler)
            self.logger.addHandler(stream)  # Adding the stream handler to the logger

        # Wrap the logger with LoggerAdapter to include extra context in log messages
        self.logger = logging.LoggerAdapter(self.logger, self.extra_log)

        # Log that the logging system has been initialized
        self.logger.debug("Logging initialized")
        
        
    def update_data(self, file, function):
        file = file.replace(self.relative_path, '')[1:]
        self.extra_log['file'] = file
        self.extra_log['function'] = function
        
    def info(self, message):        
        self.update_data(inspect.stack()[1][1], inspect.stack()[1][3])
        self.logger.info(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def critical(self, message):
        self.logger.critical(message)
    
    def exception(self, message):
        self.logger.exception(message)
    
    def log(self, level, message):
        self.logger.log(level, message)
    
    def example(self):
        self.logger.debug("This is a debug message")
        self.logger.info("This is an info message")
        self.logger.warning("This is a warning message")
        self.logger.error("This is an error message")
        self.logger.critical("This is a critical message")
        try:
            1/0
        except Exception as e:
            self.logger.exception(e)
    
    
config = {}
config = toml.load('config.toml') 