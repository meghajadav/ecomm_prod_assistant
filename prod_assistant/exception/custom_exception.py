import sys #package for current execution through exc_info()
import traceback #to get the stack trace  of the execution
from typing import Optional, cast

class ProductAssistantException(Exception): # inherit Exception for custom exception class
    def __init__(self, error_message, error_details: Optional[object] = None): # constructor with error details can be sys, any message or empty
        # Normalize message
        if isinstance(error_message, BaseException): # if error_message is exception then convert that text to string and if it is just text then also convert it into str
            norm_msg = str(error_message)
        else:
            norm_msg = str(error_message)

        # Resolve exc_info (supports: sys module, Exception object, or current context)
        exc_type = exc_value = exc_tb = None# place holders
        if error_details is None: # if error_details is None get type value and traceback from sys.exc_info
            exc_type, exc_value, exc_tb = sys.exc_info()
        else:
            if hasattr(error_details, "exc_info"):  # e.g., sys if error_details is having sys then it will check for exc_info attribute in sys
                exc_info_obj = cast(sys, error_details)# it cast error_details into sys to make sure it does not change at the run time
                exc_type, exc_value, exc_tb = exc_info_obj.exc_info()# take type vale and trace back info from exc_info() os sys
            elif isinstance(error_details, BaseException): # if error_details is of exception type the take type of error_details , value of it and it has dunder method __traceback__
                exc_type, exc_value, exc_tb = type(error_details), error_details, error_details.__traceback__
            else: # it is a fallback to get the from sys
                exc_type, exc_value, exc_tb = sys.exc_info()

        # Walk to the last frame to report the most relevant location
        last_tb = exc_tb 
        while last_tb and last_tb.tb_next: # checks if last_tb and last_tb.next is Not None 
            last_tb = last_tb.tb_next 

        self.file_name = last_tb.tb_frame.f_code.co_filename if last_tb else "<unknown>"
        self.lineno = last_tb.tb_lineno if last_tb else -1
        self.error_message = norm_msg

        # Full pretty traceback (if available)
        if exc_type and exc_tb:
            self.traceback_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
        else:
            self.traceback_str = ""

        super().__init__(self.__str__())

    def __str__(self):
        # Compact, logger-friendly message (no leading spaces)
        base = f"Error in [{self.file_name}] at line [{self.lineno}] | Message: {self.error_message}"
        if self.traceback_str:
            return f"{base}\nTraceback:\n{self.traceback_str}"
        return base

    def __repr__(self):
        return f"DocumentPortalException(file={self.file_name!r}, line={self.lineno}, message={self.error_message!r})"


# if __name__ == "__main__":
#     # Demo-1: generic exception -> wrap
#     try:
#         a = 1 / 0
#     except Exception as e:
#         raise DocumentPortalException("Division failed", e) from e

#     # Demo-2: still supports sys (old pattern)
#     # try:
#     #     a = int("abc")
#     # except Exception as e:
#     #     raise DocumentPortalException(e, sys)