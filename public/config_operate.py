#coding=utf-8
"""
Author: moyh
Alter: None
"""
import ConfigParser


class ConfigOperate(object):

    def __init__(self, file):
        '''Parameter initialization,file means configuration file.'''

        self.config = file
        self.parser = ConfigParser.ConfigParser()
        self.parser.read(self.config)
    # end


    def getOption(self, section, option=''):
        '''Get an option value for a given __section.'''

        return self.parser.get(section, option)
    # end


    def getDict(self, section):
        '''Return a __section's value in dict format.'''

        commandDict = {}
        items = self.parser.items(section)
        for key, value in items:
            commandDict[key] = value
        return commandDict
    # end


    def setOption(self, section, option, value):
        """Set an option."""
        self.parser.set(section, option, value)
        with open(self.config, 'wb') as configfile:
            self.parser.write(configfile)
    # end
