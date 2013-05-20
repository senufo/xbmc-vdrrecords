# -*- coding: utf-8 -*-
"""
Class for no display key with remote
"""
import xbmc
import xbmcgui

class Password(xbmcgui.WindowXML):
    """
    Clavier pour password
    """
    def onInit( self ):
        """
        Init Class EPGWIndow
        """
        xbmcgui.WindowXML.__init__(self)
        self.password = ''
        print "Class PASSWORD"

    def onAction(self, action):
        """
        get key for password
        """
        print "ID Action %d" % action.getId()
        print "Code Action %d" % action.getButtonCode()
        if action.getId() == 58:
            self.password = self.password + '0'
            taille = len(self.password)
            self.getControl(4).setLabel('*' * taille)
        if action.getId() == 59:
            self.password = self.password + '1'
            taille = len(self.password)
            self.getControl(4).setLabel('*' * taille)
        if action.getId() == 60 or action.getId() == 142:
            self.password = self.password + '2'
            taille = len(self.password)
            self.getControl(4).setLabel('*' * taille)
        if action.getId() == 61 or action.getId() == 143:
            self.password = self.password + '3'
            taille = len(self.password)
            self.getControl(4).setLabel('*' * taille)
        if action.getId() == 62 or action.getId() == 144:
            self.password = self.password + '4'
            taille = len(self.password)
            self.getControl(4).setLabel('*' * taille)
        if action.getId() == 63 or action.getId() == 145:
            self.password = self.password + '5'
            taille = len(self.password)
            self.getControl(4).setLabel('*' * taille)
        if action.getId() == 64 or action.getId() == 146:
            self.password = self.password + '6'
            taille = len(self.password)
            self.getControl(4).setLabel('*' * taille)
        if action.getId() == 65 or action.getId() == 147:
            self.password = self.password + '7'
            taille = len(self.password)
            self.getControl(4).setLabel('*' * taille)
        if action.getId() == 66 or action.getId() == 148:
            self.password = self.password + '8'
            taille = len(self.password)
            self.getControl(4).setLabel('*' * taille)
        if action.getId() == 67 or action.getId() == 149:
            self.password = self.password + '9'
            taille = len(self.password)
            self.getControl(4).setLabel('*' * taille)



    def onClick( self, controlId ):
        """
        Actions when mouse click on control
        """
        if controlId == 21:
            print "PASSWORD = %s " % self.password
            self.close()

