#!/usr/bin/env python
#-*- coding:utf-8 -*-
import logging

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
                'wps1.0.0':'http://www.opengis.net/wps/1.0.0',
                'gml3':'http://schemas.opengis.net/gml/3.1.1/base/gml.xsd'}
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


def RastertoBase64Coding(srcfile, desfile):
    """
    将栅格影像文件转换为Base64编码的文件
    
    @param srcfile: 源影像文件名称
    @param desfile: 编码的结果文件名称
    """
    import base64
    try:
        inf = open(srcfile)
        outf = open(desfile,'w')
        base64.encode(inf, outf)
        inf.close()
        outf.close()
    except Exception,e:
        raise e

def Base64toRasterCoding(srcfile, desfile):
    """
    将Base64编码的文件转换为栅格影像文件
    
    @param srcfile: 源base64编码的文件名称
    @param desfile: 栅格影像结果名称
    """
    import base64
    try:
        inf = open(srcfile)
        outf = open(desfile,'w')
        base64.decode(inf, outf)
        inf.close()
        outf.close()
    except Exception,e:
        raise e
    
def VectFormatTransfer(srcfile, dstfile, dstft):
    """
    将源矢量文件{srcfile}转换为{dstfile}矢量文件
    
    源矢量文件和转换的目标矢量文件格式根据文件的后缀名称确定
    
    @param srcfile: 源矢量文件名称
    @param dstfile: 目标矢量文件名称
    @param dstft: 目标文件的格式驱动名称
    """
    try:
        from osgeo import ogr
    except:
        import ogr
        
    ds = ogr.Open(srcfile)
    
    if not ds:
        logging.error(srcfile + "打开失败")
        raise Exception(srcfile + "打开失败")
    
    odr = ogr.GetDriverByName(dstft)
    
    if not odr:
        logging.error("没有对应格式的ogr驱动："+dstft)
        raise Exception("没有对应格式的ogr驱动："+dstft)
    
    dstds = odr.CopyDataSource(ds, dstfile)
    
    if not dstds:
        logging.error("源矢量文档{s}转换为目标矢量文档{d}失败".format(s=srcfile,d=dstfile))
        raise Exception("文档转换失败")
    
    dstds = None
    ds = None

def WpsInputFileWrap(srcfile):
    """
    封装从命令行输入的本地或ftp服务站上的数据
    
    如果输入的是栅格文件，则将输入文件用base64编码；
    如果输入的是矢量文件，则将其转换为GML3格式
    注意: 源文件的格式是通过文件后缀确定的，所以必须确保文件后缀与
        文件的格式相符
    
    @param srcfile: 要封装的源文件名称
    
    @return: 
        [dstfile, mimetype, encoding]:封装后的文件名称,MIMETYPE,编码；
        None: 如果输入的文件不是本地或ftp服务器上的数据 
    """ 
    import urlparse
    import tempfile
    urlinfo = urlparse.urlparse(srcfile)
    
    tmpfile = ''
    if urlinfo[0].lower() == 'ftp':
        import ftplib
        # 链接ftp服务
        ftpsv = None
        netconn = urlinfo[1].split('@')
        if len(netconn) == 1:
            ftpsv = ftplib.FTP(netconn)
        elif len(netconn[0]) == 2:
            pwd = netconn.split(':')
            if len(pwd) !=2 :
                errormsg = "用户名和密码格式{p}错误, 应为:user:pwd".format(p=netconn[0])
                logging.error(errormsg)
                raise Exception(errormsg)
            ftpsv = ftplib.FTP(netconn[0], usr,pwd)
        # 下载文件写入到临时文件中
        tmpfile = tempfile.mkstemp(srcfile, urlinfo[2].split('.')[-1])[1]
        tmpfobj = open(tmpfile,'wb')
        def writestream(block):
            global tmpfobj
            tmpfobj.write(block)
        ftpsv.retrbinary('RETR '+ urlinfo[2].lstrip('/'), writestream)
        tmpfobj.close()
        
    elif urlinfo[0].lower()== 'file':
        tmpfile = srcfile.split('://')[1]
    
    logging.info(tmpfile)
    if tmpfile == '':
        return None
    else:
        # TODO: 需要更改如何更好的确定文件的MIMETYPE和编码, 查看 mimetypes 模块是否有用
        restmpfile = ''
        fmt = (tmpfile.split('.')[-1]).lower()
        if fmt.lower() == 'gml':
            return [tmpfile, 'text/xml', 'utf-8']
        # 如果为栅格文件
        restmpfile = tempfile.mkstemp(fmt)[1]
        for format in RASTER_MIMETYPES:
            if format['GDALID'].lower().find(fmt) >= 0:
                RastertoBase64Coding(tmpfile, restmpfile)
                return [restmpfile, format['MIMETYPE'].lower(), 'base64']
        # 如果为矢量文件
        if restmpfile:
            for format in VECTOR_MIMETYPES:
                if format['DATATYPE'].lower().find(fmt) >= 0:
                    VectFormatTransfer(tmpfile, restmpfile, 'GML')
                    #return [restmpfile, format['MIMETYPE'], 'utf-8']text/xml
                    return [restmpfile, 'text/xml', 'utf-8']
        raise Exception('不支持的本地或ftp文件格式')
        