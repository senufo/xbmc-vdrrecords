# -*- coding: utf-8 -*-
"""
view vdr records with parental control
"""
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
def addFile(name, url, mode=1, iconimage='icon.png', isProtect=False):
    ''' Add a list item to the XBMC UI.'''
    isFolder = False
    li = xbmcgui.ListItem(name)
    #VideoPlayer.Tagline Small Summary of current playing Video, Critique
    #VideoPlayer.PlotOutline Small Summary of current playing Video, Intrigue
    #VideoPlayer.Plot Complete Text Summary of current playing Video, Résumé 
    info_file = open('%s/info' % url, 'r')
    for line in info_file:
        if re.search('^D',line):
            summary = re.sub("^D ",'',line)
            summary = re.sub('\|','\n',summary)
    info_file.close()
    li.setInfo( type="Video", infoLabels={ "Title": name, 'Plot': summary})
    url = sys.argv[0] + '?url=' + url + '&title=' + name + "&mode=" + str(mode) + "&protect=" + str(isProtect)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url,
                                       listitem=li, isFolder=isFolder)
#Add FOLDER in list
def addDir(name,url='xx', mode=1, iconimage='icon.png', isFolder=False):
    ''' Add a folder item to the XBMC UI.'''
    #isFolder=False
    li = xbmcgui.ListItem(name)
    li.setInfo( type="Video", infoLabels={ "Title": name })
    url = sys.argv[0] + '?url=' + url + '&mode=' + str(mode) 
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url,
                                       listitem=li, isFolder=isFolder)


# UI builder functions
def show_menu(path, racine='video'):
    ''' Show the plugin menu. '''
    #list of vdr records
    listRecords = []
    #list of folders
    Folders = []
    for root, dirs, files in os.walk(path): 
        try: 
            #On recherche les répertoires de VDR de la forme
            # 2011-02-10.20.30.42-0.rec
            if re.search('\d{4}-\d{2}-\d{2}\.', dirs[0]):
                #On décompose le chemin complet
                titres = root.split('/')
                #Si racine correspond à -2 c'est la fin du chemin
                if racine in titres[-2]:
                    Folder = False
                    files = os.listdir('%s/%s' % (root,dirs[0]))
                    tree = {'root': root, 'dirs': dirs, 'files': files, 
                            'Folder': Folder}
                    listRecords.append(tree)
                else:
                    #Sinon c'est un répertoire
                    isFolder = True
                    #On test si c'est la 1ere fois que l'on voit ce répertoire
                    if titres[-2] in Folders:
                        Folder = titres[-2]
                    else:
                        Folder = titres[-2]
                        Folders.append(titres[-2])
                        tree = {'root': root, 'dirs': dirs, 'files': files, 
                                'Folder': Folder}
                        listRecords.append(tree)
        except:
            #Erreur ce n'est pas un répertoire VDR
            pass
    #On affiche la liste
    for record in listRecords:
        #C'est un répertoire
        if record['Folder']:
            titres = record['root'].split('/')
            print 'record FOLDER = %s' % record
            folder = '/'.join(titres[:-1])
            name = re.sub(r'%|@', '', titres[-2])
            addDir(name, folder, mode=10, isFolder=True)
        #C'est un fichier
        else:
            chemin = '%s/%s' % (record['root'], record['dirs'][0])
            titres = record['root'].split('/')
            name = re.sub(r'%|@', '', titres[-1])
            #Ce répertoire a le controle parental actif
            if 'protection.fsk' in '/'.join(record['files']):
                isProtect = True
            else:
                isProtect = False
            addFile(name, chemin, 1, "icon.png", isProtect)
 
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)
    
# parameter values
params = parameters_string_to_dict(sys.argv[2])

# Depending on the mode, call the appropriate function to build the UI.
#On recupere les parametres de la listBox
params = parameters_string_to_dict(sys.argv[2])
if not sys.argv[2]:
    # new start
    path = addon.getSetting('dir')

    #path = '/video/'
    ok = show_menu(path)
elif int(params['mode']) == MODE_FILE:
    #print "mode = %s " % params['mode']
    #print "url = %s " % params['url']
    #print "protect = %s " % params['protect']
    #windowed true=play video windowed, false=play users  preference
    #windowed = True
    listitem = xbmcgui.ListItem(params['title'])
    #remplace _ par des espaces
    titre = params['title'].replace('_',' ')
   #Permet d'avoir le titre au lieu de 00001.ts
    listitem.setInfo('video', {'Title': titre})
    #On regarde combien de fichier ts on a
    files = glob.glob('%s/*.ts' % params['url'])
    #On trie l'ordre des fichiers
    files.sort()
    stack = "stack://" + " , ".join( files )
    print "==> STACK = %s " % stack
    #On vérifie la protection parentale
    if "True" in params['protect']:
        dialog = xbmcgui.Dialog()
                #'Entrez le code parental'
        locstr = addon.getLocalizedString(id=40100) 
        pin = dialog.numeric(0, locstr)
        print "code = %s " % pin
        if "5536" not in pin:
            locstr = addon.getLocalizedString(id=40101)
            locstr2 = addon.getLocalizedString(id=40102)
            #         (" Erreur", " Mauvais code ")
            dialog.ok(locstr, locstr2)
        else:     
            print "FILE = %s " % file
            xbmc.Player().play( stack, listitem )
    else:
        xbmc.Player().play( stack, listitem )
        print "FIN SCRIPT================"
#On a selectionné un dossier
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
        url = None
        name = None
        mode = None
        print "sys.arg = %s " % sys.argv[ 1 ]
        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), 
                                 sortMethod=xbmcplugin.SORT_METHOD_LABEL )
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    except:
        print "Erreur"
