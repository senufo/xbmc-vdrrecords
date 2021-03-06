# -*- coding: utf-8 -*-
"""
view vdr records with parental control
"""
__addonID__      = "plugin.video.vdrrecords"
__author__       = "Senufo"
__date__         = "21-05-2013"
__version__      = "0.2.3"

import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs
#le module password est devenu inutile
#import password
from password import *

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

__addon__      = xbmcaddon.Addon(__addonID__)
__cwd__        = __addon__.getAddonInfo('path')
__version__    = __addon__.getAddonInfo('version')
__language__   = __addon__.getLocalizedString

__profile__    = xbmc.translatePath( __addon__.getAddonInfo('profile') )
__resource__   = xbmc.translatePath( os.path.join( __cwd__, 'resources',
                                                  'lib' ) )
xbmc_version = xbmc.__version__
sys.path.append (__resource__)

DEBUG_LEVEL = __addon__.getSetting( "debug" ) == "true"
KEYBOARD = __addon__.getSetting( "keyboard" ) == "true"
exclude = __addon__.getSetting( "exclude" )
exclude_dirs = exclude.split(',')
print "EXLCUE DIRS", exclude_dirs
if DEBUG_LEVEL:
    DEBUG_LEVEL = xbmc.LOGDEBUG
else:
    DEBUG_LEVEL = xbmc.LOGNONE

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
                xbmc.log(msg='paramDict[%s] = %s ' % (paramSplits[0], paramSplits[1]),level=DEBUG_LEVEL)
    return paramDict

def getSTACK(urlstack):
    """
    make a stack for video files
    """
    #On regarde combien de fichier ts on a
    files = glob.glob('%s/*.ts' % urlstack)
    #xbmc.log(msg='FILES %s' % files,level=DEBUG_LEVEL)
    if not files:
        files = glob.glob('%s/0*.vdr' % urlstack)
    #xbmc.log(msg='FILES %s' % files,level=DEBUG_LEVEL)
    #On trie l'ordre des fichiers
    files.sort()
    #files.reverse()
    stack = "stack://" + " , ".join( files )
    xbmc.log(msg='STACK = %s ' % stack,level=DEBUG_LEVEL)
    return stack

#Add a file in list
def addFile(name, url_path, mode=1, iconimage='icon.png', isProtect=False):
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
    #print "url_path = ", os.path.join(url_path,'info')
    #Pour XBMC Frodo
    if (xbmc_version == '2.0'):
        if xbmcvfs.exists(os.path.join(url_path,'info')):
            print "xbmc version => Version 2.O"
            info_file = xbmcvfs.File(os.path.join(url_path,'info'), 'r')
        else:
            print "xbmc version => Version 2"
            info_file = xbmcvfs.File(os.path.join(url_path,'info.vdr'), 'r')
        #On lit le fichier et on le transforme en liste (\n)
        info_tab = info_file.read()
        info_tab = info_tab.split('\n')
    else:
    #Pour XBMC Eden
        try:
            print "xbmc version => Version 1.3"
            info_file = open(os.path.join(url_path,'info'), 'r')
        except:
            print "xbmc version => Version 1.3"
            info_file = open(os.path.join(url_path,'info.vdr'), 'r')
        info_tab = info_file
    #Mets des valeurs par défaut pour les infos
    realisateur = ' '
    annee = 0
    aired = ''
    duration = ''
    category = 'CATEGORY'
    acteurs = []
    for line in info_tab:
        xbmc.log(msg='INFO_FILE LINE = %s ' % line,level=DEBUG_LEVEL)
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
                    #xbmc.log(msg='GROUP = %s ' % actors.groups(),level=DEBUG_LEVEL)
                    acteurs = actors.group(1).split(',')
                    #xbmc.log(msg='Acteurs = %s, actors = %s ' %  (acteurs,actors.group(1)),level=DEBUG_LEVEL)
            summary = re.sub("^D ", '', line)
            summary = re.sub('\|', '\n', summary)
            #sum_uni = unicode(summary, errors='replace')
    info_file.close()
    #Essai classement par date
    #Ajoute le champs DATE dans infolabels
    match = re.search(".*(\d{4})-(\d{2})-(\d{2}).*", url_path)
    if match:
        Date = "%s.%s.%s" % (match.group(3),match.group(2),match.group(1))
    else: Date = "Rien"
    print "addFile date = %s" % Date
    li.setInfo( type="Video", infoLabels={ "Title": name, 'Plot': summary,
                                          'director' : realisateur,
                                          'genre' : category,
                                          'year' : int(annee),
                                          'aired' : aired,
                                          'duration' : duration,
                                          'cast' : acteurs,
                                          'Date' : Date})
    #print 'Plot = %s' % summary
    li.setProperty('IsPlayable', 'true')
    if isProtect:
        url_2 = sys.argv[0] + '?url=' + url_path + '&title=' + name + "&mode=" + str(mode) + "&protect=" + str(isProtect)
        li.setProperty('IsPlayable', 'false')
        #xbmc.log(msg='URL = %s, url_path => %s ' % (url_2, url_path),level=DEBUG_LEVEL)
    else:
        url_2 = getSTACK( url_path )
    xbmc.log(msg='addFile : url_path = %s , Title = %s' % (url_path, name),level=DEBUG_LEVEL)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url_2,
                                       listitem=li, isFolder=isFolder)
#Add FOLDER in list
def addDir(name, url='None', mode=1, iconimage='icon.png', isFolder=False):
    ''' Add a folder item to the XBMC UI.'''
    li = xbmcgui.ListItem(name)
    #Ajoute le type de media (video), le titre du media
    li.setInfo( type="Video", infoLabels={ "Title": name })
    #recupere l'adresse du fichier
    url = sys.argv[0] + '?url=' + url + '&mode=' + str(mode)
    xbmc.log(msg='addDir : url = %s , Titre = %s, Folder = %s' % (url, name, isFolder),level=DEBUG_LEVEL)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url,
                                       listitem=li, isFolder=isFolder)


# UI builder functions
def show_menu(path):
    ''' Show the plugin menu. '''
    #list of vdr records
    listRecords = []
    #list of folders
    Folders = []
    #Parcours du répertoire des enregistrements de VDR
    #Compatibilité FRODO
    if (xbmc_version == '2.0'):
        print "xbmc version => Version 2.0"
        dirs, files = xbmcvfs.listdir(path)
    #Compatibilité Eden
    else:
        print "xbmc version => Version 1.3"
        dirs = os.listdir(path)
    for dir_vdr in dirs:
        try:
            #On recherche les répertoires de VDR de la forme
            # 2011-02-10.20.30.42-0.rec
            scan_dir = os.path.join(path,dir_vdr)
            if (xbmc_version == '2.0'):
                print "xbmc version => Version 2.0"
                dir_rec, files_rec = xbmcvfs.listdir(scan_dir)
            else:
                print "xbmc version => Version 1.3"
                dir_rec = os.listdir(scan_dir)
            if re.search('\d{4}-\d{2}-\d{2}.*rec', dir_rec[0]):
                Folder = False
                scan_dir = os.path.join(path,dir_vdr,dir_rec[0])
                files = os.listdir('%s' % (scan_dir))
                tree = {'root': scan_dir, 'dirs': dir_vdr, 'files': files,
                            'Folder': Folder}
                listRecords.append(tree)
            else:
                #Sinon c'est un répertoire
                files = []
                scan_dir = os.path.join(path,dir_vdr,dir_rec[0])
                if dir_vdr not in exclude_dirs:
                    tree = {'root': scan_dir, 'dirs': scan_dir, 'files': files,
                                'Folder': dir_vdr}
                    listRecords.append(tree)
        except:
            #Erreur ce n'est pas un répertoire VDR
            print "Unexpected error:", sys.exc_info()[0]
            pass

    #On affiche la liste
    for record in listRecords:
        #C'est un répertoire
        if record['Folder']:
            #ex: record['root'] => /home/henri/VDR_videos/NCIS/Alibi
            #folder => /home/henri/VDR_videos/NCIS/Alibi
            #name => NCIS
            folder = os.path.dirname(record['root'])
            name = os.path.basename(folder)
            addDir(name, folder, mode=10, isFolder=True)
            xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
            xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)
            xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DURATION)
            xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_GENRE)
            #Il faut ajouter les bons infolabel pour les tris ci-dessous
            #xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
            #xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_FILE)
        #C'est un fichier
        else:
            chemin = xbmc.translatePath(record['root'])
            folder = os.path.dirname(record['root'])
            titre = os.path.basename(folder)
            name = re.sub(r'%|@', '', titre)
            #Si la protection est True on n'affiche pas les films
            #avec protections.fsk
            if protection:
                if 'protection.fsk' not in record['files']:
                    isProtect = False
                    print "Protect = False"
                    addFile(name, chemin, 1, "icon.png", isProtect)
            else:
                isProtect = False
                addFile(name, chemin, 1, "icon.png", isProtect)

    xbmcplugin.endOfDirectory(handle=int(handle), succeeded=True)

#Debut du programme
password = __addon__.getSetting('pin')
protection = True
protection = __addon__.getSetting( "protection" ) == "true"
password_ok = True
# parameter values
params = parameters_string_to_dict(sys.argv[2])

# Depending on the mode, call the appropriate function to build the UI.
#On recupere les parametres de la listBox
params = parameters_string_to_dict(sys.argv[2])
handle = sys.argv[1]
if not sys.argv[2]:
    # new start
    if protection:
        #Classe Password pour pb visibilité de touche
        # de la télécommande
        dialog = xbmcgui.Dialog()
                #'Entrez le code parental'
        locstr = __addon__.getLocalizedString(id=40100)
        #Clavier pour ne pas voir le password avec la télécommande
        if KEYBOARD:
        #Ne fonctionne pas pb au retour de la dialogbox
            dia_pass = Password('DialogNum.xml', __cwd__ ,"Default")
            dia_pass.show()
            #pin = dia_pass.password
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
            xbmc.executebuiltin("XBMC.Notification(%s : ,%s,30)" % (locstr,locstr2))
            params['mode'] = MODE_FOLDER
            protection = True
        else:
            #Le MdP est correct on joue la video
            #xbmc.log(msg='FILE = %s ' % stack,level=DEBUG_LEVEL)
            locstr  = __addon__.getLocalizedString(id=40103) #Code
            locstr2 = __addon__.getLocalizedString(id=40104) #Code OK
            xbmc.executebuiltin("XBMC.Notification(%s : ,%s,30)" % (locstr,locstr2))
            protection = False
    else:
        protection = False
    path = __addon__.getSetting('dir')
    ok = show_menu(path)

#On a selectionné un dossier
elif int(params['mode']) == MODE_FOLDER:
    path = params['url']
    path = re.sub('%2f','/',path)
    path = xbmc.translatePath(path)
    rep = path.split('/')
    print "PARAMS :", params
    xbmc.log(msg='Selection Dossier = %s, rep = %s, params_url = %s' % (path,rep, params['url']),level=DEBUG_LEVEL)

    ok = show_menu(path)

###############################################################################
# BEGIN !
################################################################################

if ( __name__ == "__main__" ):
    try:
        xbmc.log(msg='===============================',level=DEBUG_LEVEL)
        xbmc.log(msg='  VDR Records - Version: %s' % __version__,level=DEBUG_LEVEL)
        xbmc.log(msg='  XBMC - Version: %s' % xbmc_version,level=DEBUG_LEVEL)
        xbmc.log(msg='===============================',level=DEBUG_LEVEL)

        #params=get_params()
        url = None
        name = None
        mode = None
        xbmc.log(msg='sys.arg = %s ' % sys.argv[ 1 ],level=DEBUG_LEVEL)

        if password_ok == True:
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
        else:
            xbmc.log(msg='password_ok = %s ' % password_ok,level=DEBUG_LEVEL)

    except:
        xbmc.log(msg='Erreur',level=DEBUG_LEVEL)

