# -*- coding: utf-8 -*-
"""
view vdr records with parental control
"""
__addonID__      = "plugin.video.vdrrecords"
__author__       = "Senufo"
__date__         = "09-05-2013"
__version__      = "0.1.9"

import xbmcplugin
import xbmcgui
import xbmcaddon
import password

import sys
import os
import os.path
import glob
import re
import time

#Variables globales

temps = 0
# plugin modes
MODE_FILE = 1
MODE_FOLDER = 10

# plugin handle
handle = int(sys.argv[1])

__addon__	= xbmcaddon.Addon(__addonID__)
__cwd__        = __addon__.getAddonInfo('path')
__version__    = __addon__.getAddonInfo('version')
__language__   = __addon__.getLocalizedString

__profile__    = xbmc.translatePath( __addon__.getAddonInfo('profile') )
__resource__   = xbmc.translatePath( os.path.join( __cwd__, 'resources',
                                                          'lib' ) )
sys.path.append (__resource__)

DEBUG = __addon__.getSetting( "debug" ) == "true"
KEYBOARD = __addon__.getSetting( "keyboard" ) == "true"

if (DEBUG == "true"):
    DEBUG = LOGDEBUG
else:
    DEBUG = -1 #LOGNONE

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
                #xbmc.log(msg='paramDict[%s] = %s " % (paramSplits[0], paramSplits[1]),level=DEBUG)
    return paramDict

def getSTACK(urlstack):
    """
    make a stack for video files
    """
    #On regarde combien de fichier ts on a
    files = glob.glob('%s/*.ts' % urlstack)
    xbmc.log(msg='FILES %s' % files,level=DEBUG)
    if not files:
        files = glob.glob('%s/0*.vdr' % urlstack)
    #xbmc.log(msg='FILES %s' % files,level=DEBUG)
    #On trie l'ordre des fichiers
    files.sort()
    files.reverse()
    stack = "stack://" + " , ".join( files )
    xbmc.log(msg='STACK = %s ' % stack,level=DEBUG)
    return stack

#Add a file in list
def addFile(name, url_file, mode=1, iconimage='icon.png', isProtect=False):
    ''' Add a list item to the XBMC UI.'''
    isFolder = False
    #remplace les _ par des espaces
    name = re.sub('_',' ',name)
    li = xbmcgui.ListItem(name, 'label2') #,
    #VideoPlayer.Tagline Small Summary of current playing Video, Critique
    #VideoPlayer.PlotOutline Small Summary of current playing Video, Intrigue
    #VideoPlayer.Plot Complete Text Summary of current playing Video, Résumé
    summary = ""
    #Prend en compte les video de VDR < 1.7.0
    try:
        info_file = open('%s/info' % url_file, 'r')
    except:
        info_file = open('%s/info.vdr' % url_file, 'r')
    #Mets des valeurs par défaut pour les infos
    realisateur = ' '
    annee = 0
    category = 'CATEGORY'
    acteurs = []
    for line in info_file:
        #xbmc.log(msg='INFO_FILE LINE = %s ' % line,level=DEBUG)
        if re.search('^E',line):
            heure = line[2:].split(' ')
            time_start = time.gmtime(int(heure[1]))
            heure_start = '%02d:%02d' % (time_start.tm_hour,time_start.tm_min)
            aired = '%02d-%02d-%04d' % (time_start.tm_wday,
                                   time_start.tm_mon,time_start.tm_year)
            #Durée exprimée en secondes dans le fichier info de VDR
            #pour XBMC il le faut en minutes
            #Attention il peut y avoir des erreurs dans ce fichier (ePG)
            duration = (int(heure[2])/60)
        #Description du record
        if re.search('^D', line):
            #print 'D lines = %s' % line
            realisateur = ''
            lines = line.split('|')
            flag1 = False
            #Recupere les acteurs
            for info in lines:
                if re.match(' \n',info):
                    flag1 = False
                if flag1:
                    acteurs.append(info)
                if re.match('Acteurs',info) :
                    flag1 = True
            for info in lines:
                real = re.search('R.+alis.+ (\w+ \w+)', info,  re.IGNORECASE)
                year = re.search('Ann.+e : (\w+)', info)
                cat = re.search('Cat.+gorie : (.+)', info)
                actors = re.search('Avec : (.+)', info)
                if real:
                    realisateur = real.group(1)
                if year:
                    annee = year.group(1)
                if cat:
                    category = cat.group(1)
                if actors:
                    #xbmc.log(msg='GROUP = %s ' % actors.groups(),level=DEBUG)
                    acteurs = actors.group(1).split(',')
                    #xbmc.log(msg='Acteurs = %s, actors = %s ' %  (acteurs,actors.group(1)),level=DEBUG)
            summary = re.sub("^D ", '', line)
            summary = re.sub('\|', '\n', summary)
            #sum_uni = unicode(summary, errors='replace')
    info_file.close()
    li.setInfo( type="Video", infoLabels={ "Title": name, 'Plot': summary,
                                          'director' : realisateur,
                                          'genre' : category,
                                          'year' : int(annee),
                                          'aired' : aired,
                                          'duration' : duration,
                                          'cast' : acteurs})
    #print 'Plot = %s' % summary
    li.setProperty('IsPlayable', 'true')
    if isProtect:
        url_2 = sys.argv[0] + '?url=' + url_file + '&title=' + name + "&mode=" + str(mode) + "&protect=" + str(isProtect)
        li.setProperty('IsPlayable', 'false')
        #xbmc.log(msg='URL = %s, url_file => %s ' % (url_2, url_file),level=DEBUG)
    else:
        url_2 = getSTACK( url_file )
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url_2,
                                       listitem=li, isFolder=isFolder)
#Add FOLDER in list
def addDir(name, url='xx', mode=1, iconimage='icon.png', isFolder=False):
    ''' Add a folder item to the XBMC UI.'''
    #isFolder=False
    li = xbmcgui.ListItem(name)
    li.setInfo( type="Video", infoLabels={ "Title": name })
    url = sys.argv[0] + '?url=' + url + '&mode=' + str(mode)
    #xbmc.log(msg='addDir : url = %s , Titre = %s, Folder = %s' % (url, name, isFolder),level=DEBUG)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url,
                                       listitem=li, isFolder=isFolder)


# UI builder functions
def show_menu(path, racine='video'):
    ''' Show the plugin menu. '''
    #xbmc.log(msg='Show MENU path = %s, racine = %s' % (path,racine),level=DEBUG)
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
                    files = os.listdir('%s/%s' % (root, dirs[0]))
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
            #print 'record FOLDER = %s' % record
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
            CodeParental = True
            if CodeParental:
                addFile(name, chemin, 1, "icon.png", isProtect)
            elif isProtect:
                pass
            else:
                addFile(name, chemin, 1, "icon.png", isProtect)

    xbmcplugin.endOfDirectory(handle=int(handle), succeeded=True)

#Debut du programme
password = __addon__.getSetting('pin')
password_ok = True
# parameter values
params = parameters_string_to_dict(sys.argv[2])

# Depending on the mode, call the appropriate function to build the UI.
#On recupere les parametres de la listBox
params = parameters_string_to_dict(sys.argv[2])
handle = sys.argv[1]

if not sys.argv[2]:
    # new start
    path = __addon__.getSetting('dir')
    ok = show_menu(path)
elif int(params['mode']) == MODE_FILE:
    listitem = xbmcgui.ListItem(params['title'])
    #remplace _ par des espaces
    titre = params['title'].replace('_',' ')
    #Permet d'avoir le titre au lieu de 00001.ts
    listitem.setInfo('video', {'Title': titre})
    #On vérifie la protection parentale
    if "True" in params['protect']:
        #Classe Password pour pb visibilité de touche
        # de la télécommande
        dialog = xbmcgui.Dialog()
                #'Entrez le code parental'
        locstr = __addon__.getLocalizedString(id=40100)
        #Clavier pour ne pas voir le password avec le télécommande
        if KEYBOARD:
            dia_pass = Password('DialogNum.xml', __cwd__ ,"Default")
            dia_pass.doModal()
            pin = dia_pass.password
            del dia_pass
        else:
            #Clavier virtuel pour mot de passe
            kb = xbmc.Keyboard('', 'heading', True)
            kb.setDefault('') # optional
            kb.setHeading(locstr) # optional
            kb.setHiddenInput(True) # optional
            kb.doModal()
            if (kb.isConfirmed()):
                pin = kb.getText()
        #Password défini dans settings.xml
        password = __addon__.getSetting('pin')

        #Pas le bon MdP
        if password not in pin:
            locstr = __addon__.getLocalizedString(id=40101)
            locstr2 = __addon__.getLocalizedString(id=40102)
            #         (" Erreur", " Mauvais code ")
            dialog.ok(locstr, locstr2)
            params['mode'] = MODE_FOLDER
        else:
            #Le MdP est correct on joue la video
            #xbmc.log(msg='FILE = %s ' % stack,level=DEBUG)
            url = params['url']
            #Si plusieurs fichiers ts on les empile (fct stack de xbmc)
            stack = getSTACK(url)
            #On ren l'item Playable
            listitem.setProperty('IsPlayable', 'true')
            listitem.setPath(stack)
            #On mets le bon titre
            listitem.setInfo('video', {'Title': titre})
            xbmc.Player().play( stack, listitem )
    else:
        #Pas de protection on joue direct
        #Ne sert pas à effacer
        #xbmc.executebuiltin( "PlayMedia(%s)" % stack )
        xbmc.log( 'Mon Player',level=DEBUG)
    xbmc.log(msg='FIN SCRIPT================',level=DEBUG)

#On a selectionné un dossier
elif int(params['mode']) == MODE_FOLDER:
    path = params['url']
    path = re.sub('%2f','/',path)
    rep = path.split('/')
    #xbmc.log(msg='Selection Dossier = %s, rep = %s' % (path,rep),level=DEBUG)

    ok = show_menu(path, racine=rep[-1])

###############################################################################
# BEGIN !
################################################################################

if ( __name__ == "__main__" ):
    try:
        xbmc.log(msg='===============================',level=LOGNOTICE)
        xbmc.log(msg='  VDR Records - Version: %s' % __version__,level=LOGNOTICE)
        xbmc.log(msg='===============================',level=LOGNOTICE)

        #params=get_params()
        url = None
        name = None
        mode = None
        xbmc.log(msg='sys.arg = %s ' % sys.argv[ 1 ],level=DEBUG)

        if password_ok == True:
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ),
                                     sortMethod=xbmcplugin.SORT_METHOD_LABEL )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ),
                                     sortMethod=xbmcplugin.SORT_METHOD_NONE )
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
        else:
            xbmc.log(msg='password_ok = %s ' % password_ok,level=DEBUG)

    except:
        xbmc.log(msg='Erreur',level=DEBUG)

