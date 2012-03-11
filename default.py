# -*- coding: utf-8 -*-

__addonID__      = "plugin.video.vdrrecords"
__author__       = "Senufo"
__date__         = "06-03-2012"
__version__      = "0.1.0"

import xbmcplugin
import xbmcgui
import xbmcaddon

import sys
import os
import re
import time
import md5
import string
# plugin modes
MODE_FIRST = 10
MODE_SECOND = 20

# parameter keys
PARAMETER_KEY_MODE = "mode"

# menu item names
FIRST_SUBMENU = "First Submenu"
SECOND_SUBMENU = "Second Submenu"
# plugin handle
handle = int(sys.argv[1])


addon	= xbmcaddon.Addon(__addonID__)	
ROOTDIR            = addon.getAddonInfo('path')
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )
MEDIA_PATH = os.path.join( BASE_RESOURCE_PATH, "media" )

__settings__ = xbmcaddon.Addon(__addonID__)
__language__ = __settings__.getLocalizedString
DEBUG = __settings__.getSetting( "debug" ) == "true"

TYPES = {'categories' :{
        "JT":"/programmes-tv-info/video-integrale/",
        "Magazines":"/magazine/video-integrale/",
        "Séries - Fictions":"/series-tv/video-integrale/",
        "Jeux":"/jeux-tv/video-integrale/",
        "Jeunesse":"/programmes-tv-jeunesse/video-integrale/",
        "Divertissement":"/emissions-tv/video-integrale/",
        "Sports":"/sport/video-integrale/"
        }}
# utility functions
def parameters_string_to_dict(parameters):
    ''' Convert parameters encoded in a URL to a dict. '''
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


def addDirectoryItem(name, isFolder=True, parameters={}):
    ''' Add a list item to the XBMC UI.'''
    isFolder=False
    li = xbmcgui.ListItem(name)
    li.setInfo( type="Video", infoLabels={ "Title": name })
    #url = sys.argv[0] + '?' + urllib.urlencode(parameters)
    url = sys.argv[0] + '?' + '/video/France_4/2011-09-02.09.50.36-0.rec/00001.ts' 
    #return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url,
                                       listitem=li, isFolder=False)

def addDir(name,url,mode,iconimage):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"name="+urllib.quote_plus(name)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png",thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name })
    ok=xbmcplugin.addDirectory(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok

# UI builder functions
def show_root_menu():
    ''' Show the plugin root menu. '''
    addDirectoryItem(name=FIRST_SUBMENU, parameters={ PARAMETER_KEY_MODE: MODE_FIRST }, isFolder=True)
    addDirectoryItem(name=SECOND_SUBMENU, parameters={ PARAMETER_KEY_MODE: MODE_SECOND }, isFolder=True)
    addDirectoryItem(name="Sous menu 3", parameters={ PARAMETER_KEY_MODE: 30 }, isFolder=True)
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)
    
def show_first_submenu():
    ''' Show first submenu. '''
    for i in range(0, 5):
        name = "%s Item %d" % (FIRST_SUBMENU, i)
        addDirectoryItem(name, isFolder=False)
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)

def show_second_submenu():
    ''' Show second submenu. '''
    for i in range(0, 10):
        name = "%s Item %d" % (SECOND_SUBMENU, i)
        addDirectoryItem(name, isFolder=False)
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)

# parameter values
params = parameters_string_to_dict(sys.argv[2])
mode = int(params.get(PARAMETER_KEY_MODE, "0"))
#mode = 0
print "##########################################################"
print("Mode: %s" % mode)
print "##########################################################"

# Depending on the mode, call the appropriate function to build the UI.
print "arg0 = %s, arg1 = %s , arg2 = %s " % (sys.argv[0],sys.argv[1], sys.argv[2])
if not sys.argv[2]:
    # new start
    ok = show_root_menu()
else:
    file = sys.argv[2]
    file = string.replace(sys.argv[2], '?', '')
    print "FILE = %s " % file
    xbmc.Player().play(file)
#elif mode == MODE_FIRST:
#    ok = show_first_submenu()
#elif mode == MODE_SECOND:
#    ok = show_second_submenu()
################################################################################
# BEGIN !
################################################################################

if ( __name__ == "__main__" ):
    try:
        print "==============================="
        print "  VDR Records - Version: %s"%__version__
        print "==============================="
        print

        #params=get_params()
        url=None
        name=None
        mode=None
       #xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
        print "sys.arg = %s " % sys.argv[ 1 ]
        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    except:
        print "Erreur"
