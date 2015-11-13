#! /usr/bin/python

""" Template function """

# standard library imports
import os
import re
import sys
import glob
import shutil
import zipfile
import logging

# related third party imports
import cx_Oracle
from easygui import *
import xml.dom.minidom

# Module name
MODULE_NAME = "LoadObjectDictionary"

FILE_NAME = "FILE_NAME"

# Database connection parameter values
PARAMETER_LIST_VALUE = {}
PARAMETER_LIST_VALUE [ FILE_NAME ]  = "T:/bravo/testbestanden/Venray/v1/venray_trans_all_StUF_cf/venray_trans_l0002_StUF_cf/venray_trans_l0002_StUF_cf.xml"

# Menu options
MNU_FILE_SELECT   = "MNU_FILE_SELECT"
MNU_PRETTY_XML    = "MNU_PRETTY_XML"
MNU_EXIT          = "MNU_EXIT"

# Menu options dictionary
MENU_OPTIONS = {}
MENU_OPTIONS [ MNU_FILE_SELECT ]  = "Select XML file"
MENU_OPTIONS [ MNU_PRETTY_XML ]   = "Format XML file"
MENU_OPTIONS [ MNU_EXIT ]         = "Exit"


# Function to start gui
def gui_start () :
    logger.info( "Start initialising GUI" )
    while True :
        msg   = "What do you want?"
        options = [ MENU_OPTIONS [ MNU_FILE_SELECT ], MENU_OPTIONS [ MNU_PRETTY_XML ], MENU_OPTIONS [ MNU_EXIT ] ]
        reply=buttonbox(msg,None,options)
        if reply == MENU_OPTIONS [ MNU_FILE_SELECT ] :
            gui_file_selection ()
        elif reply == MENU_OPTIONS [ MNU_PRETTY_XML ] :
            converto_to_pretty_xml ()
        elif reply == MENU_OPTIONS [ MNU_EXIT ] :
            break

# Function to build gui for file selection
def gui_file_selection () :
    logger.info( "Start GUI file selection" )
    title = 'XML file selection'
    msg   = 'Select file'
    file  = fileopenbox(msg, title, str(PARAMETER_LIST_VALUE[ FILE_NAME ]))
    PARAMETER_LIST_VALUE[ FILE_NAME ] = str(file)
    
def converto_to_pretty_xml () :
    try :        
        logger.info( "Start format XML" )
        xml_document = xml.dom.minidom.parse(PARAMETER_LIST_VALUE[ FILE_NAME ]) 
        logger.info( "End parse" )
        (filepath, filename)  = os.path.split(PARAMETER_LIST_VALUE[ FILE_NAME ])
        (shortname, extension) = os.path.splitext(filename)
        file_name = shortname + '_formatted' + '.xml' 
        output_file = filepath + "/" + file_name   
        fOut = open( output_file, 'w')
        logger.info( "Start pp" )
        fOut.write(u''.join((xml_document.toprettyxml() )).encode('utf-8').strip())
        fOut.close()
        logger.info( "End format XML" )    
    except Exception, err:
        logger.info ( "Replace LV by SVB failed: ERROR: %s\n" % str(err) )        

# Start script
if __name__ == "__main__":
    try:
        try :
            # Initialize logger
            logger = logging.getLogger(MODULE_NAME)
            logger.setLevel(logging.DEBUG)
            stream_hdlr = logging.StreamHandler()
            formatter   = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            stream_hdlr.setFormatter(formatter)
            logger.addHandler(stream_hdlr)
            
            # Start GUI
            gui_start ()
        except Exception, err:
            logger.info ( "Installation failed: ERROR: %s\n" % str(err) )
    except Exception, err:
        print "Installation failed: ERROR: %s\n" % str(err)
        sys.exit(1)
    else:
        sys.exit(0)