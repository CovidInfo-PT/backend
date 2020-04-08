import logging
from enum import Enum

class GlobalLogger():
    
    def __init__(self, global_log_path):
        self.logger = logging.getLogger('GlobalLog')
        hdlr = logging.FileHandler(global_log_path)
        formatter = logging.Formatter('[%(asctime)s | %(levelname)s] %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr) 
        self.logger.setLevel(logging.INFO)
        
    def log(self, log_level, log_message, class_identifier):
        self.logger.log(log_level, "{} -> {}".format(class_identifier, log_message))






        