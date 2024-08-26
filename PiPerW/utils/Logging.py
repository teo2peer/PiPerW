import logging
from colorlog import ColoredFormatter
import sys
from PiPerW.utils.Singleton import Singleton
import inspect


#---------------------------
#     Logging class
#---------------------------
class Logging(metaclass=Singleton):
    def __init__(self, debug, relative_path=None):
        '''
        Logging class for PiPerW
        
        :param debug: bool: Enable debug logging
        :param relative_path: str: Relative path to the main script
        '''
        
        # Initialize class variables
        self.debug = debug
        self.relative_path = relative_path

        # rename output.log to output.old.log
        try:
            with open('output.log', 'r') as f:
                pass
            os.rename('output.log', 'output.old.log')
        except:
            pass
        
        self.file_handler = logging.FileHandler('output.log')
        self.console_handler = logging.StreamHandler(sys.stdout)
        self.console_handler.setLevel(logging.INFO)

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
        self.file_handler.setFormatter(standard_formatter)

        # Add handlers 
        self.logger.addHandler(self.file_handler)
        
        # Display debug messages if debug is enabled
        if self.debug:
            self.logger.addHandler(stream)  # Adding the stream handler to the logger

        # Wrap the logger with LoggerAdapter to include extra context in log messages
        self.logger = logging.LoggerAdapter(self.logger, self.extra_log)

        # Log that the logging system has been initialized
        self.logger.debug("Logging initialized")
        
        
    def update_data(self, file, function):
        '''
        Update the file and function in the extra_log dictionary

        :param file: str: File name
        :param function: str: Function name
        '''
        
        file = file.replace(self.relative_path, '')[1:]
        self.extra_log['file'] = file
        self.extra_log['function'] = function
        
    def info(self, message):
        '''
        Log an info message
        
        :param message: str: Message to log
        '''        
        self.update_data(inspect.stack()[1][1], inspect.stack()[1][3])
        self.logger.info(message)
    
    def warning(self, message):
        '''
        Log a warning message
        
        :param message: str: Message to log
        '''
        self.logger.warning(message)
    
    def error(self, message):
        '''
        Log an error message
        
        :param message: str: Message to log
        '''
        self.logger.error(message)
    
    def critical(self, message):
        '''
        Log a critical message
        
        :param message: str: Message to log
        '''
        self.logger.critical(message)
    
    def exception(self, message):
        '''
        Log an exception message
        
        :param message: str: Message to log
        '''
        self.logger.exception(message)
        

# Export the Logging class
Logging = Logging