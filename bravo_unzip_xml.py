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
DIR_NAME  = "DIR_NAME"

# Database connection parameter values
PARAMETER_LIST_VALUE = {}
PARAMETER_LIST_VALUE [ FILE_NAME ]  = "T:/bravo/testbestanden/Venray/v1/venray_trans_all_StUF_cf/venray_trans_l0002_StUF_cf/venray_trans_l0002_StUF_cf.xml"
PARAMETER_LIST_VALUE [ DIR_NAME ]   = "T:/bravo/testbestanden/Venray/v2/venray_StUF_20130927_all_SVB/zip"

# Menu options
MNU_FILE_SELECT   = "MNU_FILE_SELECT"
CHANGE_TAG_FILE   = "CHANGE_TAG_FILE"
CHANGE_TAG_DIR    = "CHANGE_TAG_DIR"
MNU_EXIT          = "MNU_EXIT"

# Menu options dictionary
MENU_OPTIONS = {}
MENU_OPTIONS [ MNU_FILE_SELECT ]  = "Select XML file"
MENU_OPTIONS [ CHANGE_TAG_FILE ]  = "Change SVB tag into LV tag for zipfile"
MENU_OPTIONS [ CHANGE_TAG_DIR ]   = "Change SVB tag into LV tag for all zipfiles in directory"
MENU_OPTIONS [ MNU_EXIT ]         = "Exit"


# Function to start gui
def gui_start () :
    logger.info( "Start initialising GUI" )
    while True :
        msg   = "What do you want?"
        options = [ MENU_OPTIONS [ MNU_FILE_SELECT ], MENU_OPTIONS [ CHANGE_TAG_FILE ], MENU_OPTIONS [ CHANGE_TAG_DIR ], MENU_OPTIONS [ MNU_EXIT ] ]
        reply=buttonbox(msg,None,options)
        if reply == MENU_OPTIONS [ MNU_FILE_SELECT ] :
            gui_file_selection ()
        elif reply == MENU_OPTIONS [ CHANGE_TAG_FILE ] :
            change_svb_into_lv_file ()
        elif reply == MENU_OPTIONS [ CHANGE_TAG_DIR ] :
            change_change_svb_into_lv_dir ()
        elif reply == MENU_OPTIONS [ MNU_EXIT ] :
            break

# Function to build gui for file selection
def gui_file_selection () :
    logger.info( "Start GUI file selection" )
    title = 'XML file selection'
    msg   = 'Select file'
    file  = fileopenbox(msg, title, str(PARAMETER_LIST_VALUE[ FILE_NAME ]))
    PARAMETER_LIST_VALUE[ FILE_NAME ] = str(file)

def change_change_svb_into_lv_dir () :
    try :
        logger.info ("Start replace LV by SVB for all zipfile in directory")
        for zipfile in glob.glob(PARAMETER_LIST_VALUE [ DIR_NAME ] +"/*.zip"):
            PARAMETER_LIST_VALUE[ FILE_NAME ] = str(zipfile)
            logger.info("Start processing for file: " + str(PARAMETER_LIST_VALUE[ FILE_NAME ]))
            change_svb_into_lv_file ()
    except Exception, err:
        logger.info ( "Start replace LV by SVB for all zipfile in directory failed failed: ERROR: %s\n" % str(err) )          

    
def change_svb_into_lv_file () :
    try :
        logger.info( "Start unzip file" )
        (filepath, filename)  = os.path.split(PARAMETER_LIST_VALUE[ FILE_NAME ])
        (shortname, extension) = os.path.splitext(filename)    
        zip = zipfile.ZipFile(PARAMETER_LIST_VALUE[ FILE_NAME ])
        zip.extractall( filepath + '/' + shortname ) 
        PARAMETER_LIST_VALUE[ FILE_NAME ] = filepath + '/' + shortname + '/' + shortname +'.xml' 
        logger.info( "End unzip file" )  
    except Exception, err:
        logger.info ( "Unzip file failed: ERROR: %s\n" % str(err) )    
    
    try :        
        logger.info( "Start replace LV by SVB" )
        # Input file        
        fIn = open(PARAMETER_LIST_VALUE[ FILE_NAME ], 'r' ) 
        # Output file
        (filepath, filename)  = os.path.split(PARAMETER_LIST_VALUE[ FILE_NAME ])
        (shortname, extension) = os.path.splitext(filename)
        file_name = shortname + '_SVB_pp' + '.xml' 
        output_file = filepath + "/" + file_name   
        zip_file = filepath + "/" + shortname + '_SVB_pp' + '.zip'   
        logger.info( "Open XML file  " + str(output_file) )
        fOut = open( output_file, 'w')
        # Read inputfile line by line
        for line_in in fIn :
            line_out = line_in.replace( 'stuf-geo:mtbLVDi01', 'stuf-geo:mtbSVBDi01' )
            fOut.write(line_out)
        fIn.close()            
        fOut.close()
        logger.info( "End replace LV by SVB" )
        logger.info( "Start zip XML file  " + str(output_file) )   
        os.chdir( filepath )
        zipFile = zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED )
        zipFile.write( file_name )
        zipFile.close()
        logger.info( "End zip XML file" )    
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