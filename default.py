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
import os.path
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
def addDir(name,url='xx',mode=1,iconimage='icon.png', isFolder=False):
#def addDirectoryItem(name, isFolder=True, parameters={}):
    ''' Add a list item to the XBMC UI.'''
    #isFolder=False
    li = xbmcgui.ListItem(name)
    li.setInfo( type="Video", infoLabels={ "Title": name })
    #url = sys.argv[0] + '?' + urllib.urlencode(parameters)
    url = sys.argv[0] + '?' + url + '/00001.ts' 
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url,
                                       listitem=li, isFolder=isFolder)

# UI builder functions
def show_root_menu():
    ''' Show the plugin root menu. '''
    path = '/video/'
    listRecords = []
    Folders = []
    for root, dirs, files in os.walk(path): 
        #print "root = %s " % root
        #print "dirs = %s " % dirs
        #print "files = %s " % files
        try: 
            #print dirs[0]
            if re.search('\d{4}-\d{2}-\d{2}\.', dirs[0]):
                titres = root.split('/')
                #print "-1 = %s, -2 = %s " % (titres[-1],titres[-2])
                if 'video' in titres[-2]:
                    path = root + '/' + dirs[0]
                    #print 'PATH = %s ' % path
                    Folder = False
                    tree = {'root': root, 'dirs': dirs, 'files': files, 'Folder':
                            Folder}
                    listRecords.append(tree)
                    #addDir(titres[-1], path, 1, "icon.png")
                    #print "not folder"
                else:
                    isFolder = True
                    if titres[-2] in Folders:
                        Folder = titres[-2]
                     #   print "Folder = %s " % Folder
                    else:
                        Folder = titres[-2]
                        #print "Append Folder = %s " % Folder
                        Folders.append(titres[-2])
                        tree = {'root': root, 'dirs': dirs, 'files': files, 'Folder':
                            Folder}
                        listRecords.append(tree)

                    #addDir(titres[-2], root, 1, "icon.png", isFolder=True)
                    #print "Folder = %s " % titres[-2]
        except:
            pass
    for record in listRecords:
        print "==> %s " % record
        #print "Folder = %s " % record['Folder']
        if record['Folder']:
            titres = record['root'].split('/')
            #print 'Titres = %s' % titres[-2]
            name = re.sub(r'%|@','',titres[-2])
            addDir(name, isFolder=True)
        else:
            chemin = '%s/%s' % (record['root'],record['dirs'][0])
            print "Chemin = %s " % chemin
            titres = record['root'].split('/')
            print 'Titres = %s' % titres[-1]
            name = re.sub(r'%|@','',titres[-1])
            addDir(name, chemin, 1, "icon.png", isFolder=False)
                #addDir(titres[-2], root, 1, "icon.png", isFolder=False)
 
        #if 'info' in files :
        #    print root
        #    titres = root.split('/')
        #    print 'Titres = %s' % titres[-2]
        #    name = re.sub(r'%|@','',titres[-2])
            #addDir(name, root, 1, "icon.png")
    #addDirectoryItem(name=SECOND_SUBMENU, parameters={ PARAMETER_KEY_MODE: MODE_SECOND }, isFolder=True)
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)
    
# parameter values
#params = parameters_string_to_dict(sys.argv[2])
#mode = int(params.get(PARAMETER_KEY_MODE, "0"))
mode = 0
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
###############################################################################
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
