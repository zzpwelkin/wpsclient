#!/usr/bin/env python
#-*-coding:utf-8-*-

"""
/***************************************************************************
wpsclient.py Wps客户端库  
-------------------------------------------------------------------
 Date                 : 2012.5.13 9:50
 Copyright            : (C) 2012 by 张祖鹏
 email                : zhangzupeng19871203@126.com

 Authors              : 张祖鹏

  ***************************************************************************
  *                                                                         *
  *   This program is free library; you can redistribute it and/or modify   *
  *   it under the terms of the GNU General Public License as published by  *
  *   the Free Software Foundation; either version 2 of the License, or     *
  *   (at your option) any later version.                                   *
  *                                                                         *
  ***************************************************************************/
"""
from xml.dom.xmlbuilder import DOMBuilder
import urllib2
import logging
from httplib import HTTPConnection

from OGCCommon import *
from description import processDescribe
from description import strProcessDescribe

class WpsClient(object):
    """
    访问wps服务的富客户端接口
    """
    theOGCservice = "WPS"
    theVersion = "1.0.0"
    
    def __init__(self, serverurl, proxy=None, logfile=None):
        """
        设置要访问的wps服务的url及其代理
        
        @param servername: wps服务url路径
        """
    
        self.theProcessesSupported = {}
        self.theServeUrl = serverurl
        
        # TODO: 添加代理功能
        
        # TODO: 判断服务是否可用,待修改
        urllib2.urlopen(serverurl+"?version=1.0.0&service=WPS&request=GetCapabilities", timeout=5)
        
        # 设置日志文件
        if logfile:
            logging.basicConfig(filename = logfile)
        
    def _getWPSServiceXML(self, request, identifier=''):
        requesturl = '{0}?version={1}&service={2}&request={3}'.format(self.theServeUrl, 
                       self.theVersion, self.theOGCservice, request)
        
        if identifier != '':
            requesturl = '{0}&identifier={1}'.format(requesturl, identifier) 
            
        try:
            return DOMBuilder().parseURI(requesturl)
        except:
            logging.exception(exc_info())
            raise Exception(exc_info()[2])
     
    def GetCapabilities(self, isVerbose=False):
        """
        得到wps服务站点提供的处理服务
        
        @param  isVerbose: True则返回概述、元数据等详细信息，否则只得到处理标识符
        """
        procList = []
        
        processElems = self._getWPSServiceXML('GetCapabilities').getElementsByTagNameNS(
                OGCNamespaceURI['wps1.0.0'], 'Process')
        if not isVerbose:
            for elem in processElems:
                if elem:
                    identifier = elem.getElementsByTagNameNS(OGCNamespaceURI['ows1.1'],
                            'Identifier')[0].firstChild.nodeValue
                    version = elem.attributes.getNamedItemNS(OGCNamespaceURI['wps1.0.0'],
                            'processVersion').nodeValue
                            
                    procList.append([identifier,version])
        else:
            for elem in processElems:
                if elem:
                    procList.append(ProcessBrief().getProcessBrief(elem))
                    
        return procList
            
    def ProcessDescribe(self, identifier):
        """
        得到此标识符处理服务详细信息，格式为[identifier, abstract，{inputs},{outputs}]
        
        如果wps服务中没有对应的标识符，则返回异常
        """
        if not self.theProcessesSupported.has_key(identifier):
            self.theProcessesSupported[identifier] = processDescribe(self._getWPSServiceXML(
                'DescribeProcess',identifier))
            return self.theProcessesSupported[identifier]

    def ReadableProcessDescribe(self,identifier):
        return strProcessDescribe(self.ProcessDescribe(identifier))
        
    def Execute(self, identifier, *argv, **kwargs):
        #获得描诉信息
        desc = self.theProcessesSupported[identifier]
        
        if not desc:
            try:
                desc = self.ProcessDescribe(identifier)
            except:
                raise
            
        # Wrap input parameter
        inputxml = self._wrapInputParam(desc[1], *argv, **kwargs)
        outputxml = self._wrapOutputParam(desc[1], *argv, **kwargs)
        
        # 创建XML格式文档
        postString = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n"
        postString += "<wps:Execute service=\""+ self.theOGCservice +"\" version=\""+ self.theVersion + "\"" + \
                       " xmlns:wps=\"http://www.opengis.net/wps/1.0.0\"" + \
                       " xmlns:ows=\"http://www.opengis.net/ows/1.1\"" +\
                       " xmlns:xlink=\"http://www.w3.org/1999/xlink\"" +\
                       " xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\""\
                       " xsi:schemaLocation=\"http://www.opengis.net/wps/1.0.0" +\
                       " http://schemas.opengis.net/wps/1.0.0/wpsExecute_request.xsd\">"
                       
        postString += "<ows:Identifier>"+identifier+"</ows:Identifier>\n"
        postString += "<wps:DataInputs>"
        
        # 发送请求
        
    
if __name__ == "__main__":
    wps = WpsClient("http://localhost/cgi-bin/pywps.cgi")
#    for brief in wps.GetCapabilities(False):
#        print brief[0] + " v." + brief[1]+"\n"
#        
#    for brief in wps.GetCapabilities(True):
#        print str(brief)+"\n"
        
#    for brief in wps.GetCapabilities():
#        print wps.strProcessDescribe(wps.ProcessDescribe(brief[0]))
    print wps.ReadableProcessDescribe('v.buffer')
    print wps.ReadableProcessDescribe('v.to.points')
