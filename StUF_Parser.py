#!/usr/bin/env python

###################################################
#                                                 #
# Script to import S-57 data                      # 
#                                                 #
# Author: MTJ                                     #
# Date:   1-8-2012                                #
#                                                 #
###################################################

# standard library imports
import os
import sys
import logging

# related third party imports
import cx_Oracle
from easygui import *
import uuid
import xml.dom.minidom
import xml.sax.handler

# GDAL/OGR imports
import gdal
import ogr
import osr

# Tags in StUF:Geo
GEO_OBJECT_ELEMENT   = "stuf-geo:object"
PRIMARY_KEY_ELEMENT  = "stuf-geo:lokaalID"
GEO_OBJECT_DICT      = {}

# Global Parameters
MODULE               = "StUF_Importer"
DB_USER_SOURCE       = "DB_USER_SOURCE"
DB_PASSWORD_SOURCE   = "DB_PASSWORD_SOURCE"
DB_TNS_SOURCE        = "DB_TNS_SOURCE"
STUF_FILE            = "STUF_FILE"
SHAPE_FILE           = "SHAPE_FILE"

# Database connection parameter values
PARAMETER_LIST_VALUE = {}
PARAMETER_LIST_VALUE [ DB_USER_SOURCE ]     = "sens"
PARAMETER_LIST_VALUE [ DB_PASSWORD_SOURCE ] = "senso"
PARAMETER_LIST_VALUE [ DB_TNS_SOURCE ]      = "localhost/test"
PARAMETER_LIST_VALUE [ STUF_FILE ]          = "C:/documents/BGT/Voorbeeldbestanden/denbosch-bgt-stuf-v8-1.1/denbosch-bgt-stuf-v8-1.1.xml"
PARAMETER_LIST_VALUE [ SHAPE_FILE ]         = "C:/documents/BGT/Voorbeeldbestanden/denbosch-bgt-stuf-v8-1.1/denbosch-bgt-stuf-v8-1.1.shp"

# StUF geo datatypes
STRING  = "1"

# StUF geo-attributes defintion
STUF_ATTRIBUTES_DEF = {}
STUF_ATTRIBUTES_DEF[ 'stuf-geo:namespace' ] = STRING 
STUF_ATTRIBUTES_DEF[ 'stuf-geo:lokaalID' ] = STRING 
STUF_ATTRIBUTES_DEF[ 'stuf-geo:creationDate' ] = STRING
STUF_ATTRIBUTES_DEF[ 'stuf-geo:terminationDate' ] = STRING 
STUF_ATTRIBUTES_DEF[ 'StUF:tijdstipRegistratie' ] = STRING
STUF_ATTRIBUTES_DEF[ 'stuf-geo:bronhouder' ] = STRING 
STUF_ATTRIBUTES_DEF[ 'stuf-geo:inOnderzoek' ] = STRING
STUF_ATTRIBUTES_DEF[ 'stuf-geo:relatieveHoogteligging' ] = STRING 
STUF_ATTRIBUTES_DEF[ 'stuf-geo:bgt-status' ] = STRING
STUF_ATTRIBUTES_DEF[ 'stuf-geo:plus-status' ] = STRING
STUF_ATTRIBUTES_DEF[ 'stuf-geo:bgt-fysiekVoorkomen' ] = STRING 
STUF_ATTRIBUTES_DEF[ 'stuf-geo:plus-fysiekVoorkomen' ] = STRING
STUF_ATTRIBUTES_DEF[ 'stuf-geo:begroeidTerreindeelOpTalud' ] = STRING 
STUF_ATTRIBUTES_DEF[ 'stuf-geo:kruinlijnBegroeidTerreindeel' ] = STRING


#########################################
#  Generic functions
#########################################

# Initialize logging to screen
def start_logging () :
    try: 
        logger = logging.getLogger(MODULE)
        logger.setLevel(level=logging.INFO)
        level_name = 'info'
        stream_hdlr = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        stream_hdlr.setFormatter(formatter)
        logger.addHandler(stream_hdlr)
        logger.info("Start")
        return logger
    except Exception, err:
        print "Start logging failed"
        raise

#########################################
#  Database Class
#########################################

# Oracle database connection
class DbConnectionClass:
    """Connection class to Oracle database"""

    def __init__(self, DbUser, DbPass, DbConnect, parent_module):

        try :
            # Build connection and get session_id
            self.logger = logging.getLogger( parent_module + '.DbConnection')
            self.logger.info("Setup database connection")
            self.oracle_connection = cx_Oracle.connect(DbUser, DbPass, DbConnect)
            self.oracle_cursor = self.oracle_connection.cursor()
            self.session_id = 1490782 # for testing only
        except Exception, err:
            self.logger.critical("Setup db connection failed: ERROR: " + str(err))
            raise
           

    def rollback_close( self ) :
        """Function to rollback and close connection"""
        self.oracle_connection.rollback()
        self.oracle_connection.close()

    def commit_close( self ) :
        """Function to commit and close connection"""
        self.oracle_connection.commit()
        self.oracle_connection.close()

##########################################
##  GUI Functions
##########################################

def gui_db_parameters() :
    # Db connection
    title = 'Database connection parameters'
    msg   = "Enter database connection parameters "
    field_names   = [ DB_TNS_SOURCE, DB_USER_SOURCE , DB_PASSWORD_SOURCE ]
    return_values = [ PARAMETER_LIST_VALUE [DB_TNS_SOURCE], PARAMETER_LIST_VALUE [DB_USER_SOURCE], PARAMETER_LIST_VALUE[DB_PASSWORD_SOURCE] ]
    return_values = multpasswordbox( msg,title, field_names, return_values)
    if return_values :
        PARAMETER_LIST_VALUE [DB_TNS_SOURCE]      = return_values[0]
        PARAMETER_LIST_VALUE [DB_USER_SOURCE]     = return_values[1]
        PARAMETER_LIST_VALUE [DB_PASSWORD_SOURCE] = return_values[2]      

# Function to build gui for file selection
def gui_file_selection ( box_title, file_parameter ) :
    title = box_title
    msg   = 'Select file'
    file  = fileopenbox(msg, title, str(PARAMETER_LIST_VALUE[file_parameter]))
    PARAMETER_LIST_VALUE[STUF_FILE] = str(file)

##########################################
##  GIS Functions
##########################################

#def plot_feature_attributes ( feature ) :

    ## Plot attributes and values of feature
    #for j in range( feature.GetFieldCount() ) :
        #if feature.IsFieldSet(j) :
            #field_def  = feature.GetFieldDefnRef(j)
            #field_name = field_def.GetName()
            #logger.info("Field name    = " + str(field_name) + ": " + str(feature.GetFieldAsString(field_name)))    
       

#def plot_geometry ( ogr_geom_in ) :
    
    ## Plot point
    #if ogr_geom_in.GetGeometryName() == 'POINT' :
        #x = []
        #y = []
        #x.append(ogr_geom_in.GetX())
        #y.append(ogr_geom_in.GetY())
        #pylab.plot(x,y,'o',color='y')    
    
    ## Plot linestring
    #if ogr_geom_in.GetGeometryName() == 'LINESTRING' :
        #x = []
        #y = []
        #for i in range(ogr_geom_in.GetPointCount()) :
            #x.append(ogr_geom_in.GetX(i))
            #y.append(ogr_geom_in.GetY(i))
        #pylab.plot(x,y,'-',color='g')
    
    ## Plot polygon
    #if ogr_geom_in.GetGeometryName() == 'POLYGON' :
        #for i_ring in range ( ogr_geom_in.GetGeometryCount() ):
            #ring        = ogr_geom_in.GetGeometryRef( i_ring )
            #x =[ring.GetX(i) for i in range(ring.GetPointCount()) ]
            #y =[ring.GetY(i) for i in range(ring.GetPointCount()) ]
            #if i_ring == 0 :
                #pylab.plot(x,y,'-',color='r', linewidth=2.0, hold=True)
            #else :
                #pylab.plot(x,y,'-',color='b', linewidth=2.0, hold=True)

    ## Plot multi geometry
    #if ogr_geom_in.GetGeometryName() in ('MULTIPOINT', 'MULTILINESTRING', 'MULTILINESTRING')  :
        #for i in range(ogr_geom_in.GetGeometryCount()):
            #ogr_geom_out = plot_geometry ( ogr_geom_in.GetGeometryRef( i ) )   

##########################################
##  Show S57 Functions
##########################################

#def show_s57_file ( file_name ) :
    
    ## Clear S57 options if set or our results will be messed up.
    #gdal.SetConfigOption( 'OGR_S57_OPTIONS', '' )
    ##gdal.SetConfigOption( 'OGR_S57_OPTIONS', 'RETURN_PRIMITIVES:ON' )
    #gdal.SetConfigOption( 'OGR_S57_OPTIONS', 'RETURN_LINKAGES:ON' )
    #print logger.info("GDAL options: " + str(gdal.GetConfigOption( 'OGR_S57_OPTIONS')))
    
    ## Open s57 FILE
    #ds = ogr.Open( PARAMETER_LIST_VALUE [ S57_FILE ] )

    ##
    #choice = choicebox('How do you want to select features','Feature selection',[ C_FEATURE_TYPE, C_RECORD_ID, C_SPATIAL ])

    #if choice == C_FEATURE_TYPE :

        ## Popup select box for feature types
        #msg               = "Select feature type"
        #title             = "Feature type"
        #feat_type_list    = [ ds.GetLayer(i).GetName() for i in xrange(ds.GetLayerCount()) ]
        #feature_type_list = multchoicebox(msg, title, feat_type_list)

        ## Get features from file
        #if len(feature_type_list) > 0 :
            #for feature_type in feature_type_list :
                #src_features   = ds.GetLayerByName( feature_type )
                #feature        = src_features.GetNextFeature()
                #nr_features    = 0
                #nr_points      = 0
                #while feature is not None:
                    #nr_features   = nr_features + 1
                    #ogr_geom      = feature.GetGeometryRef()
                    #if ogr_geom is not None :
                        #plot_geometry ( ogr_geom )
                    #plot_feature_attributes ( feature )
                    #feature = src_features.GetNextFeature()
                    #logger.info("=================================================")

    #if choice == C_RECORD_ID :

        ## Ask for record ID to look for
        #record_id = str(integerbox('Give record ID', 'Record ID input', 1, 0, 99999))        

        ## Loop over features
        #for feat_type in (ds.GetLayer(i).GetName() for i in xrange(ds.GetLayerCount())) :
            #src_features   = ds.GetLayerByName( feat_type )
            #feature        = src_features.GetNextFeature()
            #while feature is not None:
                #for j in range( feature.GetFieldCount() ) :
                    #if feature.IsFieldSet(j) :
                        #field_def  = feature.GetFieldDefnRef(j)
                        #field_name = field_def.GetName()
                        #if str(field_name) == 'RCID' and str(feature.GetFieldAsString(field_name)) == record_id :
                            #ogr_geom      = feature.GetGeometryRef()
                            #if ogr_geom is not None :
                                #plot_geometry ( ogr_geom )
                            #plot_feature_attributes ( feature )                                
                #feature = src_features.GetNextFeature()

    #if choice == C_SPATIAL :

        ## Ask for which type of spatial
        #spatial_type = choicebox('How do you want to select features','Feature selection',[ VI, VC, VE ])

        ## Ask for record ID to look for
        #record_id = str(integerbox('Give record ID', 'Record ID input', 1, 0, 99999))
        
        ## Find layer and feature
        #src_features   = ds.GetLayerByName( spatial_type )
        #feature        = src_features.GetNextFeature()
        #while feature is not None:
            #for j in range( feature.GetFieldCount() ) :
                #if feature.IsFieldSet(j) :
                    #field_def  = feature.GetFieldDefnRef(j)
                    #field_name = field_def.GetName()
                    #if str(field_name) == 'RCID' and ( str(feature.GetFieldAsString(field_name)) == record_id ) :
                        #ogr_geom      = feature.GetGeometryRef()
                        #if ogr_geom is not None :
                            #plot_geometry ( ogr_geom )
                        #plot_feature_attributes ( feature )                                
            #feature = src_features.GetNextFeature()        
        
    #ds.Destroy()
    
    ## Show to plotted objects
    #pylab.show()    

##########################################
##  Import S57 Functions
##########################################
    
#def import_s57_file ( file_name ) :
    
    ## Read S57 file options:
    ## RETURN_PRIMITIVES => VI, VE and VC layers as features
    ## RETURN_LINKAGES   => FS relations are included as attribute of feature
    ## LNAM_REF          => FF relations are included as sttribute of feature

    ## Open S57 file to read spatials with SS relations
    #logger.info("Open S57 file to read spatials with SS relations")
    #gdal.SetConfigOption( 'OGR_S57_OPTIONS', '' )
    #gdal.SetConfigOption( 'OGR_S57_OPTIONS', 'RETURN_PRIMITIVES:ON' )   
   
    ## Open s57 FILE
    #ds = ogr.Open( PARAMETER_LIST_VALUE [ S57_FILE ] )

    ## Write cell header to dictionary
    #logger.info("Write cell header to dictionary")
    #dsid_dict = write_cell_header_dict ( ds.GetLayerByName( DSID ) )

    ## Show cell charactertics
    #uuid_cell = uuid.uuid1()
    #logger.info("UUID of cell: " + str(uuid_cell))
    #logger.info("Name of cell to import: " + str(dsid_dict[CELL_NAME]))
    #logger.info("Number of isolated nodes in file: " + str(dsid_dict[NOIN])) 
    #logger.info("Number of connected nodes in file: " + str(dsid_dict[NOCN]))   
    #logger.info("Number of edges in file: " + str(dsid_dict[NOED]))
    
    ## Write VI to dictionary
    #logger.info("Read isolated nodes from file")
    #vi_dict = write_features_to_dict ( ds.GetLayerByName( VI ), RECORD_ID )

    ## Write VC to dictionary
    #logger.info("Read connected nodes from file")
    #vc_dict = write_features_to_dict ( ds.GetLayerByName( VC ), RECORD_ID )

    ## Write VE to dictionary
    #logger.info("Read edges from file")
    #ve_dict = write_features_to_dict ( ds.GetLayerByName( VE ), RECORD_ID )

    ## Test if dictionaries are correct 
    ##print "VI: " + str(vi_dict[1170])
    ##print "VC start: " + str(vc_dict[7054])
    ##print "VC end: " + str(vc_dict[7072])
    ##print "VE before: " + str(ve_dict[9700])

    ## Add connected nodes to edge
    #logger.info("Add start and end connected node to edge")
    #ve_dict = add_vc_to_ve ( ve_dict, vc_dict )

    ##print "VE updated: " + str(ve_dict[9700])    

    ## Store spatials in database
    #logger.info("Store spatials in db") 
    #OracleConnection.store_spatials ( vi_dict, VI )   
    #OracleConnection.store_spatials ( vc_dict, VC )   
    #OracleConnection.store_spatials ( ve_dict, VE )                                                 

    ## Store SS relations in database
    #logger.info("Store spatial-spatial relations in db")     
    #OracleConnection.store_spatial_spatial_relations ( ve_dict ) 
    
    ## Close file
    #ds.Destroy()

    #logger.info("Spatials and spatial-spatial relations stored in db") 

    ## Open S57 file to read features with FS relations
    #logger.info("Open S57 file to read features with FS relations")
    #gdal.SetConfigOption( 'OGR_S57_OPTIONS', '' )
    #gdal.SetConfigOption( 'OGR_S57_OPTIONS', 'RETURN_LINKAGES:ON'  )  

    ## Open s57 FILE
    #ds = ogr.Open( PARAMETER_LIST_VALUE [ S57_FILE ] )    

    ## Write features to list
    #logger.info("Read features from file")
    #fe_list = write_features_to_list ( ds )

    ## Write features to db
    #logger.info("Store features in db")
    #OracleConnection.store_features ( fe_list ) 
                         
    ## Close file
    #ds.Destroy()


#def write_features_to_list ( s57_file ) :

    #feature_type_list = []

    ## Loop over feature types in file
    #for i in xrange(s57_file.GetLayerCount()) :
        #src_features = s57_file.GetLayerByName( s57_file.GetLayer(i).GetName() )        
        #if str(s57_file.GetLayer(i).GetName())<> DSID : 
            #feature_type_list.append( write_features_to_dict( src_features, LONG_NAME )) 
    #logger.info(str(i-1) + " feature types read from file")
    #return feature_type_list     


#def write_cell_header_dict ( features ) :
    
    ## Write cll header fields to dictionary
    #feature  = features.GetNextFeature()
    #if feature is not None :
        #fields_dict = {}
        #for j in range( feature.GetFieldCount() ) :
            #if feature.IsFieldSet(j) :
                #field_def = feature.GetFieldDefnRef(j)
                #field_name = field_def.GetName()
                #fields_dict[str(field_name)] = str(feature.GetFieldAsString(field_name))
    #return fields_dict    

#def write_features_to_dict ( features, unique_identifier ) :

    ## Loop over features and write to dictionary
    #features_dict = {}
    #feature       = features.GetNextFeature()
    #while feature is not None:
        #fields_dict = {}
        #for j in range( feature.GetFieldCount() ) :
            #if feature.IsFieldSet(j) :
                #field_def = feature.GetFieldDefnRef(j)
                #field_name = field_def.GetName()
                #if str(field_name) == str(unique_identifier) :
                    #if str.isdigit(str(feature.GetFieldAsString(field_name))):
                        #record_id = int(feature.GetFieldAsString(field_name))
                    #else :
                        #record_id = str(feature.GetFieldAsString(field_name))
                #else :
                    #fields_dict[str(field_name)] = str(feature.GetFieldAsString(field_name))
        #if feature.GetGeometryRef() is not None :
            #fields_dict[GEOMETRY] = feature.GetGeometryRef().ExportToWkt()
        #features_dict[record_id] = fields_dict            
        #feature = features.GetNextFeature()
    #return features_dict

    
#def add_vc_to_ve ( ve_dict, vc_dict ) :

    ## Loop over ve, get start and end vc, update ve geometry and add to dictionary
    #for key in ve_dict :

        ## Get start and end vc and ve geometries
        #ve = ve_dict[key]
        #start_vc = vc_dict [ int(ve[START_VC]) ] 
        #end_vc = vc_dict [ int(ve[END_VC]) ] 
        #start_vc_geom = ogr.CreateGeometryFromWkt(start_vc[GEOMETRY])
        #end_vc_geom = ogr.CreateGeometryFromWkt(end_vc[GEOMETRY])
        #ve_geom = ogr.CreateGeometryFromWkt(ve[GEOMETRY])

        ## Init new ve and add vertices
        #new_ve_geom = ogr.Geometry(ogr.wkbLineString)
        #new_ve_geom.AddPoint(start_vc_geom.GetX(0),start_vc_geom.GetY(0))
        #for i in range(ve_geom.GetPointCount()) :
            #new_ve_geom.AddPoint(ve_geom.GetX(i),ve_geom.GetY(i))
        #new_ve_geom.AddPoint(end_vc_geom.GetX(0),end_vc_geom.GetY(0))

        ## Add updated ve to ve dictionanry
        #ve[GEOMETRY] = new_ve_geom.ExportToWkt() 
        #ve_dict[key] = ve

    ## Return ve dictionaty with updated ve geoemtries
    #return ve_dict

##############################################
# Write shapefile
##############################################

def write_stuf_to_shape_file ( shape_file, geo_object_dict ) :
    logger.info( "Write geometry to shape file" )
    
    is_polygon = False
    
    # Get driver
    driver     = ogr.GetDriverByName('ESRI Shapefile')
    
    # Set coordinate system
    source_srs       = osr.SpatialReference()
    source_srs.ImportFromEPSG(int(28992))    
    
    # Create shapfile
    if os.path.exists(shape_file) :
        driver.DeleteDataSource(shape_file)
    shapeData      = driver.CreateDataSource(shape_file)
    
    # Create layer and feature definition
    layer          = shapeData.CreateLayer("Individual model", source_srs, ogr.wkbPolygon)
    fieldDefn      = ogr.FieldDefn('id', ogr.OFTInteger)
    layer.CreateField(fieldDefn)
    fieldDefn      = ogr.FieldDefn(PRIMARY_KEY_ELEMENT, ogr.OFTString)
    layer.CreateField(fieldDefn)    
    for field in STUF_ATTRIBUTES_DEF :
        fieldDefn      = ogr.FieldDefn(str(field), ogr.OFTString)
        layer.CreateField(fieldDefn)        
    featureDefn    = layer.GetLayerDefn()
    
    # Create feature
    i = 0
    for lokaalID in geo_object_dict : 
        i = i + 1
        shape_feature = ogr.Feature(featureDefn)
        shape_feature.SetField('id', i )
        shape_feature.SetField(PRIMARY_KEY_ELEMENT, str(lokaalID))
        for attribute in geo_object_dict[ lokaalID ] :
            if attribute == 'gml:Polygon' :
                shape_feature.SetGeometry(ogr.CreateGeometryFromWkt((geo_object_dict[ lokaalID ][attribute]))) 
                is_polygon = True
            else :
                try :
                    shape_feature.SetField(attribute, str(geo_object_dict[ lokaalID ][attribute]))
                except Exception, err:
                    logger.warning("Not attribute defined")                    
    
        # Write feature to file
        if is_polygon :
            layer.CreateFeature(shape_feature)
            is_polygon = False
            shape_feature.Destroy()
    
    # Clean up    
    shapeData.Destroy()
    
    logger.info( "Creating shapefile completed" )

#########################################
# XML functions
#########################################

# SAX Parser
class stufGeoHandler(xml.sax.ContentHandler): 
    
    def __init__(self):
        xml.sax.ContentHandler.__init__(self)   
        self.processing_geo_object = False
        self.processing_gml = False
      
    def startElement(self, name, attrs): 
        if name == GEO_OBJECT_ELEMENT :
            self.attributes_dict = {}
            self.processing_geo_object = True
        if name in ('gml:Point' ) :
            self.point = ogr.Geometry(ogr.wkbPoint)
            self.processing_gml = True
        if name in ('gml:Polygon' ) :
            self.polygon = ogr.Geometry(ogr.wkbPolygon)      
            self.processing_gml = True
        self.start_element = name
        
    def endElement(self, name):
        
        # Process only geo-objects 
        if self.processing_geo_object :
            
            # Process attributes and get primary key
            if name == self.start_element : 
                # TO DO: Check on datatype
                value = u''.join((self.content)).encode('utf-8').strip()
                if name == PRIMARY_KEY_ELEMENT :
                    self.primary_key = value 
                elif not self.processing_gml :
                    self.attributes_dict[str(name)] = str(value)
                
            # Process geometry 
            if name in ('gml:Polygon' ) :
                self.attributes_dict[str(name)] = str(self.polygon.ExportToWkt())
                self.processing_gml = False
            if name == 'gml:exterior' :
                self.polygon.AddGeometry(self.ring)
            if name == 'gml:interior' :
                self.polygon.AddGeometry(self.ring)
            if name == 'gml:LinearRing' :
                self.ring.CloseRings()
            if name == 'gml:posList' :
                is_x = True
                self.ring = ogr.Geometry(ogr.wkbLinearRing)
                for ordinate in value.rsplit(' ') :
                    if is_x :
                        x = float(ordinate)
                        is_x = False
                    else :
                        y = float(ordinate) 
                        self.ring.AddPoint(x,y)
                        is_x = True
            if name == 'gml:pos' :
                if len( value.rsplit(' ') ) == 2 :
                    self.point.AddPoint_2D( float(value.rsplit(' ')[0]), float(value.rsplit(' ')[1]) )                
                    self.attributes_dict[str(name)] = str(self.point.ExportToWkt())  
                    self.processing_gml = False
            
            # Add geo-object to geo-dictionary
            if name == GEO_OBJECT_ELEMENT :
                GEO_OBJECT_DICT[self.primary_key] = self.attributes_dict 
                self.processing_geo_object = False
                
    def characters(self, content):
        self.content = content
        
    def endDocument(self):
        logger.info("endDocument")
      
def parse_stufgeo_sax ( file_name ) :
    logger.info("Parse StUF file")
    source = open( file_name )
    xml.sax.parse( source, stufGeoHandler() )    

# DOM parser
def parse_stuf_file ( file_name ) :
    try:
        logger.info("Parse StUF file")
        xmldom = xml.dom.minidom.parse( file_name )
        logger.info("StUF file parsed")
        element = "stuf-geo:wgdLk01T"
        for xml_imgeo_object in xmldom.getElementsByTagName(element) :
            lokaalID = xmldom.getElementsByTagName('lokaalID').childNodes[0].nodeValue
            print lokaalID
    except Exception, err:
        logger.critical("Query on database failed: ERROR: " + str(err))
        sys.exit("Execution stopped")
        
#########################################
# Start main program
#########################################
        
if __name__ == "__main__":
    try:
        # Start logging framework
        logger = start_logging()

        # TO DO: Set SYSDATE as GLOBAL
        
        # Get database connection parameters
        #logger.info("Get database connection parameters")
        #gui_db_parameters()
        
        # Build database connection
        #logger.info("Open database connection")
        #OracleConnection = DbConnectionClass ( PARAMETER_LIST_VALUE[ DB_USER_SOURCE ], PARAMETER_LIST_VALUE[ DB_PASSWORD_SOURCE ], PARAMETER_LIST_VALUE[ DB_TNS_SOURCE ], MODULE )       
        
        # Select StUF file
        #logger.info("Select StUF file")
        #gui_file_selection ( "Select StUF file", STUF_FILE )
        logger.info ( "StUF " + str(PARAMETER_LIST_VALUE [ STUF_FILE ]) + " selected")
        
        # Process StUF file
        logger.info ( "Process selected StUF file" )
        parse_stufgeo_sax ( PARAMETER_LIST_VALUE [ STUF_FILE ] )
        logger.info ( "Aantal geo-objecten: "  + str(len(GEO_OBJECT_DICT)))
        for key in GEO_OBJECT_DICT :
            print GEO_OBJECT_DICT[key]
        
        logger.info ( "Write StUF file to shape file" )
        #write_stuf_to_shape_file ( PARAMETER_LIST_VALUE [ SHAPE_FILE ], GEO_OBJECT_DICT )
        # Close database connection
        #logger.info ("Close database connection")
        #OracleConnection.rollback_close()
        
    except Exception, err:
        print "Installation failed: ERROR: %s\n" % str(err)
        sys.exit(1)

