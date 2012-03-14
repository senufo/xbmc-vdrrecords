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
import glob
import re
import string

# plugin modes
MODE_FILE = 1
MODE_FOLDER = 10

# plugin handle
handle = int(sys.argv[1])

addon	= xbmcaddon.Addon(__addonID__)	
ROOTDIR            = addon.getAddonInfo('path')
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )
MEDIA_PATH = os.path.join( BASE_RESOURCE_PATH, "media" )

__settings__ = xbmcaddon.Addon(__addonID__)
__language__ = __settings__.getLocalizedString
DEBUG = __settings__.getSetting( "debug" ) == "true"

# utility functions
# parse parameters for the menu
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

#Add a file in list
def addFile(name,url,mode=1,iconimage='icon.png', isProtect=False):
    ''' Add a list item to the XBMC UI.'''
    isFolder=False
    li = xbmcgui.ListItem(name)
    li.setInfo( type="Video", infoLabels={ "Title": name })
    #url = sys.argv[0] + '?url=' + url + '/00001.ts' + '&title=' + name + "&mode=" + str(mode) + "&protect=" + str(isProtect)
    url = sys.argv[0] + '?url=' + url + '&title=' + name + "&mode=" + str(mode) + "&protect=" + str(isProtect)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url,
                                       listitem=li, isFolder=isFolder)
#Add FOLDER in list
def addDir(name,url='xx',mode=1,iconimage='icon.png', isFolder=False):
    ''' Add a list item to the XBMC UI.'''
    #isFolder=False
    li = xbmcgui.ListItem(name)
    li.setInfo( type="Video", infoLabels={ "Title": name })
    url = sys.argv[0] + '?url=' + url + '&mode=' + str(mode) 
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url,
                                       listitem=li, isFolder=isFolder)


# UI builder functions
def show_menu(path, racine='video'):
    ''' Show the plugin root menu. '''
    #path = '/video/'
    print "path = %s " % path
    listRecords = []
    Folders = []
    for root, dirs, files in os.walk(path): 
        print "root = %s " % root
        #print "dirs = %s " % dirs
        #print "files = %s " % files
        try: 
            #On recherche les répertoires de VDR de la forme
            # 2011-02-10.20.30.42-0.rec
            if re.search('\d{4}-\d{2}-\d{2}\.', dirs[0]):
                #On décompose le chemin complet
                titres = root.split('/')
                #print "-1 = %s, -2 = %s " % (titres[-1],titres[-2])
                #if 'video' in titres[-2]:
                #Si racine correspond à -2 c'est la fin du chemin
                if racine in titres[-2]:
                    Folder = False
                    #protection.fsk
                    files = os.listdir('%s/%s' % (root,dirs[0]))
                    tree = {'root': root, 'dirs': dirs, 'files': files, 'Folder':
                            Folder}
                    listRecords.append(tree)
                else:
                    #Sinon c'est un répertoire
                    isFolder = True
                    #On test si c'est la 1ere fois que l'on voit ce répertoire
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
        except:
            #Erreur ce n'est pas un répertoire VDR
            pass
    #On affiche la liste
    for record in listRecords:
        print "==> %s " % record
        if record['Folder']:
            titres = record['root'].split('/')
            #print 'Titres = %s' % titres[-2]
            print 'record FOLDER = %s' % record
            folder = '/'.join(titres[:-1])
            name = re.sub(r'%|@','',titres[-2])
            addDir(name, folder, mode=10, isFolder=True)
        else:
            chemin = '%s/%s' % (record['root'],record['dirs'][0])
            print "Chemin = %s " % chemin
            titres = record['root'].split('/')
            print 'Titres = %s' % titres[-1]
            name = re.sub(r'%|@','',titres[-1])
            if 'protection.fsk' in '/'.join(record['files']):
                isProtect = True
            else:
                isProtect = False
            addFile(name, chemin, 1, "icon.png", isProtect)
 
        #if 'info' in files :
        #    print root
        #    titres = root.split('/')
        #    print 'Titres = %s' % titres[-2]
        #    name = re.sub(r'%|@','',titres[-2])
            #addDir(name, root, 1, "icon.png")
    #addDirectoryItem(name=SECOND_SUBMENU, parameters={ PARAMETER_KEY_MODE: MODE_SECOND }, isFolder=True)
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)
    
# parameter values
params = parameters_string_to_dict(sys.argv[2])
#mode = int(params.get(PARAMETER_KEY_MODE, "0"))
#mode = 0
print "##########################################################"
#print("Mode: %s" % mode)
print "arg0 = %s, arg1 = %s , arg2 = %s " % (sys.argv[0],sys.argv[1], sys.argv[2])
print "##########################################################"

# Depending on the mode, call the appropriate function to build the UI.
#print "arg0 = %s, arg1 = %s , arg2 = %s " % (sys.argv[0],sys.argv[1], sys.argv[2])
params = parameters_string_to_dict(sys.argv[2])
if not sys.argv[2]:
    # new start
    path = '/video/'
    ok = show_menu(path)
elif int(params['mode']) == MODE_FILE:
    print "mode = %s " % params['mode']
    print "url = %s " % params['url']
    print "protect = %s " % params['protect']
    if params['protect']:
        xbmc.executebuiltin("XBMC.Notification(%s,%s)"%("Protection Parentale","Protection"))
    print "FILE = %s " % file
    #print 'arg_3 = %s ' % sys.argv[3]
    windowed = True
    listitem = xbmcgui.ListItem(params['title'])
    listitem.setInfo('video', {'Title': params['title'], 'Genre': 'Science Fiction'})
    #xbmc.Player().play( "stack://00001.ts , 00002.ts , 00003.ts" )
    #xbmc.Player().play(params['url'], listitem)
    #print "stack:/%s, 00002.ts , 00003.ts" % params['url']
    files = glob.glob('%s/*.ts' % params['url'])
    files.sort()
    print "FILES = %s " % files
    videos = [ "video/%Superman/2011-03-01.22.08.12-0.rec/00001.ts",
              "video/%Superman/2011-03-01.22.08.12-0.rec/00002.ts" ]
    stack = "stack://" + " , ".join( videos )
    stack = "stack://" + " , ".join( files )
    print "==> STACK = %s " % stack
    xbmc.Player().play( stack )
    #print("stack://video/%Superman/2011-03-01.22.08.12-0.rec/00001.ts, 00002.ts, 00003.ts")
    
    #xbmc.Player().play("stack://video/%Superman/2011-03-01.22.08.12-0.rec/00001.ts, 00002.ts")
    print "FIN SCRIPT================"
    #xbmc.Player().play(params['url'], listitem, windowed)
    #xbmc.Player().play(params['url'])
elif int(params['mode']) == MODE_FOLDER:
    #print "mode = %s " % params['mode']
    #print "url = %s " % params['url']
    #print "protect = %s " % params['protect']
    path = params['url']
    rep = path.split('/')
    #print "PATH => %s " % path
    ok = show_menu(path, racine=rep[-1])

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
