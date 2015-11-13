#! /usr/bin/python

""" SVN tags """

# SVN keywords
# Revision : $Rev: 74 $
# Id       : $Id: GenerateCleanInstallGGM.py 74 2013-02-11 11:41:31Z mark_terlien $

# standard library imports
import sys
import os
import glob
import stat
import shutil
import logging
import datetime
import re
import xml.dom.minidom
from htmlentitydefs import name2codepoint

# related third party imports
import cx_Oracle
try :
    from easygui import *
except :
    print "No easy gui"
    None


__author__="Terlien"
__date__ ="$9-okt-2009 11:50:05$"
__copyright__ = "Copyright 2013, Transfer Solutions"


MODULE_NAME = "Generate_Insert_Statements"

# Parameters
DB_USER_SOURCE            = "DB_USER_SOURCE"
DB_PASSWORD_SOURCE        = "DB_PASSWORD_SOURCE"
DB_TNS_SOURCE             = "DB_TNS_SOURCE"

# Parameter default values
PARAMETER_LIST_VALUE = {}
PARAMETER_LIST_VALUE [ DB_USER_SOURCE ]            = "boris_owner"
PARAMETER_LIST_VALUE [ DB_PASSWORD_SOURCE ]        = "boris_owner"
PARAMETER_LIST_VALUE [ DB_TNS_SOURCE ]             = "aton.lddb.transfer-solutions.com:1521/obrs"

def htmlentitydecode(s):
    return re.sub('&(%s);' % '|'.join(name2codepoint),
            lambda m: unichr(name2codepoint[m.group(1)]), s)

# Database functions
def parse_sdo_geometry ( sdo_geometry_object, xmin, ymax ) :
    "Parse sdo_geometry to sdo_geometry text for insert"
    try:
	
	# Gtype, srid and point
	sdo_gtype = int(sdo_geometry_object.SDO_GTYPE) 
	sdo_srid = int(sdo_geometry_object.SDO_SRID)
	sdo_point = sdo_geometry_object.SDO_POINT

	# Point
	logger.debug("Process point")	
	if not sdo_point :
	    sdo_point_type = "null"
	else :
	    x = sdo_point.X
	    y = sdo_point.Y
	    z = sdo_point.Z
	    sdo_point_type = "SDO_POINT_TYPE(" + str(x) + "," + str(y) 
	    if z :
		sdo_point_type = sdo_point_type + "," + str(z)
	    else :
		sdo_point_type = sdo_point_type + ", null" 
	    sdo_point_type = sdo_point_type +")"
	
	# Element info array
	logger.debug("Process element info array")
	sdo_elem_info = sdo_geometry_object.SDO_ELEM_INFO
	if not sdo_elem_info :
	    sdo_elem_info_array = "null"
	else :
	    line_nr = 1
	    sdo_elem_info_array = "SDO_ELEM_INFO_ARRAY("
	    for elem in sdo_elem_info:
		sdo_elem_info_array = sdo_elem_info_array + str(int(elem)) + ","
		# Start newline because limit length in sqplus 
		if int(len(sdo_elem_info_array)) > int(1000 * line_nr) :
		    #sdo_elem_info_array = sdo_elem_info_array + "\r"	
		    sdo_elem_info_array = sdo_elem_info_array + "\n"
		    line_nr = line_nr + 1		
	    sdo_elem_info_array = sdo_elem_info_array[:-1] + str(")")
	
	# Ordinate array
	logger.debug("Process ordinate array")	
	sdo_ordinates = sdo_geometry_object.SDO_ORDINATES 
	is_x = True
	if not sdo_ordinates :
	    sdo_ordinate_array = "null"
	else :
	    line_nr = 1
	    coordinates = ''
	    logger.debug("Loop over ordinates")
	    for ordinate in sdo_ordinates:
		if is_x :
		    #ordinate = str(float(ordinate) - float(xmin))
		    ordinate = str(float(ordinate))
		    coordinates = coordinates + str(ordinate) + ','
		    is_x = False
		else :
		    #ordinate = str(float(ymax) - float(ordinate))
		    ordinate = str(-float(ordinate))
		    coordinates = coordinates + str(ordinate) + ' '
		    is_x = True
		# Start newline because limit length in sqplus 
		if int(len(coordinates) + len(coordinates) ) > int(1000 * line_nr) :
		    coordinates = coordinates + "\n"	
		    line_nr = line_nr + 1
	# Build geometry as text string 
	sdo_geometry_text = coordinates
	return sdo_geometry_text
    except Exception, err:
        logger.critical ( "Generate DML on database failed: ERROR: %s\n" % str(err) )	
	raise	

def get_table_list ( DbConnection ) :
    try :
        """Function to get list"""
	oracle_cursor = DbConnection.cursor()
        table_list = []
        stmt = "select table_name from user_tables"
        oracle_cursor.arraysize = 100000
        oracle_cursor.execute(stmt)
        resultset = oracle_cursor.fetchmany()
        if resultset :
            for row in resultset :
                table_list.append(str(row[0]))
        return table_list    
    except Exception, err:
        logger.critical ( "Get table_list failed: ERROR: %s\n" % str(err) )	
	raise

def write_table_svg  ( DbConnection, fIn, table_name, schema, where_clause) :
    "Function to write insert DML for table"
    # <Polygon id="test123" onmouseover="showData(evt);" attrib:NAME="MTJ" fill="#E44D26" points="0,0 0,500 500,500, 500,0 0,0      100,100 400,100 400,400, 100,400 100,100  	 200,200 200,300 300,300, 300,200 200,200		"/>
    # Init statements
    try :
	oracle_cursor = DbConnection.cursor()
	column_stmt = 'select column_name, data_type from dba_tab_columns where table_name =\'' + str(table_name) + '\' and owner = \'' + str.upper(schema) + '\''
	select_stmt = 'select '
	insert_stmt = 'insert into ' + str(table_name) + '('
	log_select  = 'select \'' + str(table_name) + '\' from dual;'
	# fIn.write(log_select + '\n')
	
	# Get MBR of geometries to be extracted to SVG
	geometry_column_select = 'select column_name from dba_tab_columns t where t.table_name =\'' + str(table_name) + '\' and t.owner = \'' + str.upper(schema) + '\' and t.data_type = \'SDO_GEOMETRY\''
	geometry_column_set = oracle_cursor.execute(geometry_column_select)
	for geometry_column in geometry_column_set :
	    geometry_column_name = str(geometry_column[0])
	mbr_select_stmt = 'select sdo_aggr_mbr(' + geometry_column_name + ') from ' + str(table_name) 
	mbr_column_set = oracle_cursor.execute(mbr_select_stmt)
	for mbr_column in mbr_column_set :
	    mbr = mbr_column[0]	
	mbr_ordinates = mbr.SDO_ORDINATES
	x_min = float(mbr_ordinates[0])
	y_min = float(mbr_ordinates[1])
	x_max = float(mbr_ordinates[2])
	y_max = float(mbr_ordinates[3])
	minx = x_min
	miny = -y_max
	width  = (x_max - x_min)
	height = (y_max - y_min)
	viewbox = 'viewBox="' + str(minx) + ' ' + str(miny) + ' ' + str(width) + ' ' + str(height) + '"' 
	logger.info(viewbox)
	fIn.write( viewbox + '\n')
    
	# Get columns and build insert and select statement
	columnset = oracle_cursor.execute(column_stmt)
	index = 1
	sdo_geometry_column = None
	column_data_type_dict = {}
	column_name_dict = {}
	for column in columnset :
	    column_name = str(column[0])
	    data_type   = str(column[1])
	    insert_stmt = insert_stmt + column_name + ', '
	    column_data_type_dict[index] = data_type
	    column_name_dict[index] = column_name
	    index = index + 1
	    if str(data_type) == str("DATE") :
		column_name = "to_char(" + str(column_name) + ",\'yyyy-mm-dd hh24:mi:ss\')"
	    if str(data_type) == str("SDO_GEOMETRY") :
		sdo_geometry_column = str(column_name) 
	    select_stmt = select_stmt + str(column_name) + ', '
	insert_stmt = insert_stmt[:-2] + ')'
	select_stmt = select_stmt[:-2] + ' from ' + str(schema) + '.' + str(table_name) + ' tab ' + where_clause
	logger.debug(select_stmt)
    
	# Get id's and build insert statements
	logger.debug(select_stmt)
	valueset = oracle_cursor.execute(str(select_stmt))
	row_num = 0
	for value in valueset :
	    # Each row in the table
	    row_num = row_num + 1
	    nr_of_values = len(value)
	    value_index = 0
	    values_list = '<polygon '
	    while int(value_index) < int(nr_of_values) :
		# Now process all columns of the table
		if value[value_index] <> None  :
		    add_attribute = True
		    data_type = column_data_type_dict[value_index+1]
		    column_name = column_name_dict[value_index+1] 
		    if str(data_type) == "VARCHAR2" or str(data_type) == "CLOB" :
			value_1   = str(value[value_index])
			value_2   = htmlentitydecode(value_1)
			value_4   = str.replace( str(value_2), "'", "''")
			value_ins = str(value_4)
		    elif str(data_type) == str("SDO_GEOMETRY") :
			add_attribute = False
			geometry = parse_sdo_geometry(value[value_index], x_min, y_max)
		    elif str(data_type) == str("BLOB") :
			add_attribute = False
		    else :
			value_ins = str(value[value_index])
		    if add_attribute :  
			values_list = values_list  + 'attrib:' + str(column_name) + '=\"' + str(value_ins) + '\" '
		value_index = value_index + 1
	    fIn.write(values_list + ' fill=\"#E44D26\" ')
	    # Geometry has to be inserted through PLSQL to prevent error when more than 1000 ordinates have to be inserted
	    if sdo_geometry_column :
		fIn.write( 'points=\"' + str(geometry) + '\"/>\n') 		
    except Exception, err:
        logger.critical ( "Generate DML on database failed: ERROR: %s\n" % str(err) )	
	raise

def gui_db_connection () :
    title = 'Database connection parameters'
    msg   = "Give database connection parameters development database"
    field_names   = [ DB_TNS_SOURCE, DB_USER_SOURCE, DB_PASSWORD_SOURCE ]
    return_values = [ PARAMETER_LIST_VALUE [DB_TNS_SOURCE], PARAMETER_LIST_VALUE[DB_USER_SOURCE], PARAMETER_LIST_VALUE[DB_PASSWORD_SOURCE] ]
    return_values = multpasswordbox(msg,title, field_names, return_values)
    if return_values :
        PARAMETER_LIST_VALUE [DB_TNS_SOURCE]      = return_values[0]
        PARAMETER_LIST_VALUE [DB_USER_SOURCE]     = return_values[1]
        PARAMETER_LIST_VALUE [DB_PASSWORD_SOURCE] = return_values[2]

def gui_svg_export () :
    gui_db_connection ()
    output_dir = diropenbox("Directory", "Give directory", "C:/temp" )
    DbConnection = cx_Oracle.connect( PARAMETER_LIST_VALUE[ DB_USER_SOURCE ], PARAMETER_LIST_VALUE[ DB_PASSWORD_SOURCE ], PARAMETER_LIST_VALUE[ DB_TNS_SOURCE ])    
    table_name = choicebox("Table selection", "Select table", get_table_list ( DbConnection )  )
    table_file  = output_dir + "/" + table_name + ".sql"
    fOut = open( table_file , 'w')
    write_table_svg ( DbConnection, fOut, table_name, PARAMETER_LIST_VALUE[ DB_USER_SOURCE ], '' ) 
    fOut.close()
    DbConnection.close()

def initLogger():
    # Initialize logger
    logger = logging.getLogger(MODULE_NAME)
    logger.setLevel(logging.INFO)
    stream_hdlr = logging.StreamHandler()
    formatter   = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    stream_hdlr.setFormatter(formatter)
    logger.addHandler(stream_hdlr)
    return logger

if __name__ == "__main__":

    try:

        try :
            # Read input parameters
            argc = len(sys.argv)
            if argc != 2:
                show_gui = True
            else :
                show_gui = False
                parameter_file_list = parse_parameter_file( sys.argv[1] )

            logger = initLogger()
            
            # Build gui for input
            if show_gui :
                # Popup GUI for parameter input
                gui_svg_export ( )
            else :
                # Run with command line parameter file import
                None

        except Exception, err:
            logger.info ( "Generation insert statements failed: ERROR: %s\n" % str(err) )

    except Exception, err:
        print "Generation insert statements failed: ERROR: %s\n" % str(err)
        sys.exit(1)



