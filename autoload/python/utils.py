import time
import sys
import os
import vim

class Options:
    instance = None

    def __init__(self):
        self.refresh_key = vim.eval('do#get("do_refresh_key")')
        self.update_time = int(vim.eval("do#get('do_update_time')"))
        self.new_process_window_command = vim.eval('do#get("do_new_process_window_command")')
        self.auto_show_process_window = bool(int(vim.eval('do#get("do_auto_show_process_window")')))
        self.check_interval = int(vim.eval("do#get('do_check_interval')"))

        if self.check_interval < 500:
            self.check_interval = 500

    @classmethod
    def reload(cls):
        cls.instance = Options()

    @classmethod
    def inst(cls):
        """Get the Options instance.
        """
        if cls.instance is None:
            cls.reload()
        return cls.instance

    @classmethod
    def refresh_key(cls):
        return cls.inst().refresh_key

    @classmethod
    def check_interval(cls):
        return cls.inst().check_interval

    @classmethod
    def update_time(cls):
        return cls.inst().update_time

    @classmethod
    def new_process_window_command(cls):
        return cls.inst().new_process_window_command

    @classmethod
    def auto_show_process_window(cls):
        return cls.inst().auto_show_process_window

class Logger:
    """ Abstract class for all logger implementations.

    Concrete classes will log messages using various methods,
    e.g. write to a file.
    """

    (ERROR,INFO,DEBUG) = (0,1,2)
    TYPES = ("ERROR","Info","Debug")
    debug_level = ERROR

    def __init__(self, debug_level):
        pass

    def log(self, string, level):
        """ Log a message """
        pass

    def shutdown(self):
        """ Action to perform when closing the logger """
        pass

    def time(self):
        """ Get a nicely formatted time string """
        return time.strftime("%a %d %Y %H:%M:%S", \
                time.localtime())

    def format(self, string, level):
        display_level = self.TYPES[level]
        """ Format the error message in a standard way """
        return "- [%s] {%s} %s" %(display_level, self.time(), str(string))


class FileLogger(Logger):
    """ Log messages to a window.

    The window object is passed in on construction, but
    only created if a message is written.
    """
    def __init__(self, debug_level, filename):
        self.filename = os.path.expanduser(filename)
        self.f = None
        self.debug_level = int(debug_level)

    def __open(self):
        try:
            self.f = open(self.filename,'w')
        except IOError as e:
            raise LogError("Invalid file name '%s' for log file: %s" \
                    %(self.filename, str(e)))
        except:
            raise LogError("Error using file '%s' as a log file: %s" \
                    %(self.filename, sys.exc_info()[0]))


    def shutdown(self):
        if self.f is not None:
            self.f.close()

    def log(self, string, level):
        if level > self.debug_level:
            return
        if self.f is None:
            self.__open()
        self.f.write(\
            self.format(string,level)+"\n")
        self.f.flush()

class Log:

    loggers = {}

    def __init__(self,string,level = Logger.INFO):
        Log.log(string,level)

    @classmethod
    def log(cls, string, level = Logger.INFO):
        for k, l in cls.loggers.items():
            l.log(string,level)

    @classmethod
    def set_logger(cls, logger):
        k = logger.__class__.__name__
        if k in cls.loggers:
            cls.loggers[k].shutdown()
        cls.loggers[k] = logger

    @classmethod
    def remove_logger(cls, type):
        if type in cls.loggers:
            cls.loggers[type].shutdown()
            return True
        else:
            print("Failed to find logger %s in list of loggers" % type)
            return False

    @classmethod
    def shutdown(cls):
        for k, l in cls.loggers.items():
            l.shutdown()
        cls.loggers = {}

class LogError(Exception):
    pass

def log(string, level = Logger.INFO):
    Log.log(string, level)
