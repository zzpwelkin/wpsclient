#!/usr/bin/env python
#-*- coding:utf-8 -*-

# All supported import raster formats
RASTER_MIMETYPES =        [{"MIMETYPE":"IMAGE/TIFF", "GDALID":"GTiff"},
                           {"MIMETYPE":"IMAGE/PNG", "GDALID":"PNG"}, \
                           {"MIMETYPE":"IMAGE/GIF", "GDALID":"GIF"}, \
                           {"MIMETYPE":"IMAGE/JPEG", "GDALID":"JPEG"}, \
                           {"MIMETYPE":"IMAGE/GEOTIFF", "GDALID":"GTiff"}, \
                           {"MIMETYPE":"APPLICATION/X-ERDAS-HFA", "GDALID":"HFA"}, \
                           {"MIMETYPE":"APPLICATION/NETCDF", "GDALID":"netCDF"}, \
                           {"MIMETYPE":"APPLICATION/X-NETCDF", "GDALID":"netCDF"}, \
                           {"MIMETYPE":"APPLICATION/GEOTIFF", "GDALID":"GTiff"}, \
                           {"MIMETYPE":"APPLICATION/X-GEOTIFF", "GDALID":"GTiff"}, \
                           {"MIMETYPE":"APPLICATION/X-ESRI-ASCII-GRID", "GDALID":"AAIGrid"}, \
                           {"MIMETYPE":"APPLICATION/IMAGE-ASCII-GRASS", "GDALID":"GRASSASCIIGrid"}]
# All supported input vector formats [mime type, schema]
VECTOR_MIMETYPES =        [{"MIMETYPE":"application/x-zipped-shp", "SCHEMA":"", "GDALID":"ESRI Shapefile", "DATATYPE":"SHP"}, \
                           {"MIMETYPE":"application/vnd.google-earth.kml+xml", "SCHEMA":"KML", "GDALID":"KML", "DATATYPE":"KML"}, \
                           {"MIMETYPE":"text/xml", "SCHEMA":"GML", "GDALID":"GML", "DATATYPE":"GML"}, \
                           {"MIMETYPE":"text/xml; subtype=gml/2.", "SCHEMA":"GML2", "GDALID":"GML", "DATATYPE":"GML2"}, \
                           {"MIMETYPE":"text/xml; subtype=gml/3.", "SCHEMA":"GML3", "GDALID":"GML", "DATATYPE":"GML3"}, \
                           {"MIMETYPE":"application/json", "SCHEMA":"JSON", "GDALID":"GEOJSON", "DATATYPE":"JSON"}, \
                           {"MIMETYPE":"application/geojson", "SCHEMA":"GEOJSON", "GDALID":"GEOJSON", "DATATYPE":"GEOJSON"}]


# the namespace 
OGCNamespaceURI = {'ows1.1':'http://www.opengis.net/ows/1.1', 
                'wps1.0.0':'http://www.opengis.net/wps/1.0.0'}
W3NamespaceURI = {'xlink':'http://www.w3.org/1999/xlink'}

class AllowedValuesDef(object):
    # TODO: implement
    def getAllowedValuesDef(self, elem):
        return self

class WpsDescription(object):
    """
    wps common description
    
    Note: the Metadata attribute is a list of disc
    """
    def __init__(self):
        self.theIdentifier = None
        self.theTitle = None
        self.theAbstract = None
        self.theMetadata = [{}]
    
    def __str__(self):
        # TODO: 添加metadata的描诉
        return "{identifier}\n\tTitle:{title}\n\tAbstract:{abstract}".format(
                identifier=self.theIdentifier, title=self.theTitle, 
                abstract=self.theAbstract)
    
    def getWpsDescription(self, elem):
        """
        从xml配置文件的节点中获取定义的描诉
        """     
        self.theIdentifier = elem.getElementsByTagNameNS(OGCNamespaceURI['ows1.1'],
                            'Identifier')[0].firstChild.nodeValue
        
        self.theTitle = elem.getElementsByTagNameNS(OGCNamespaceURI['ows1.1'],
                            "Title")[0].firstChild.nodeValue
        
        abstract = elem.getElementsByTagNameNS(OGCNamespaceURI['ows1.1'],"Abstract")
        if abstract:
            self.theAbstract = abstract[0].firstChild.nodeValue 
                                
        # Get Metadata that zero oe more be included
        if len(elem.getElementsByTagNameNS(OGCNamespaceURI['ows1.1'], "Metadata")):
            for mdelem in elem.getElementsByTagName("ows:Metadata"):
                key = mdelem.attributes.getNamedItemNS(W3NamespaceURI['xlink'], "title").nodeValue
                value = mdelem.attributes.getNamedItemNS(W3NamespaceURI['xlink'], "href").nodeValue
                self.theMetadata.append({key:value})
                
        return self
