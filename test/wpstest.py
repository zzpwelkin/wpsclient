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

from unittest import TestCase
from unittest import TestSuite
from unittest import TextTestRunner
from unittest import main
from xml.dom import minidom
import os
import wpsclient
from description import strProcessDescribe,processDescribe
from cmdinterprete import ExecuteRequestStruct

class ExecuteTest(TestCase):
    
    def setUp(self):
        TestCase.setUp(self)
        self.serveUrl = "http://localhost/cgi-bin/pywps.cgi"
        self.testFileDirect = os.path.abspath("test/testxmlfile")
        self.theXmlDoc = minidom.parse(os.path.join(self.testFileDirect, "v_buffer.xml"))
        
    def tearDown(self):
        pass
    
    def testWrapInputParam(self):
        # LiteralData
        # ComplexData
        complex = {}
        # BoundingBox
        boundingbox = {}
        
        wpsassess = wpsclient.WpsClient(self.serveUrl)
        
        inputxml = wpsassess._wrapInputParam(wpsassess.ProcessDescribe('v.buffer')[1],distance={'value':2}, type={'value':'area'})
        
        assertvalue = ""
        
        '''
        http://localhost/cgi-bin/pywps.cgi?version=1.0.0&service=WPS&request=Execute&DataInputs=distance=20;type='area';input=@format=
        
        http://localhost/cgi-bin/pywps.cgi?version=1.0.0&service=WPS&request=Execute&identifier=v.buffer&DataInputs=input=ftp%3A%2f%2fzzpwelkin%3A2191307%2flocalhost%2fstreams.gml@mimetype=text/xml@encoding=utf-8@schema=http%3A%2F%2Fschemas.opengis.net%2Fgml%2F3.1.1%2Fbase/gml.xsd;distance=20&lineage=true
        '''
        
        self.assertEqual(inputxml, assertvalue, msg)
        pass
        
class CmdInterpreteTest(TestCase): 
    """
    命令行解释器测试用例
    """     
    def testSimpleCmd(self):
        """
        测试简单命令解析
        """
        cmd = "v.buffer --l input=http://foo.map@mimetype=text/xml@encoding=utf-8 distance=20@datatype=float output=@mimetype=text/xml"
        request = ExecuteRequestStruct("http://localhost/cgi-bin/pywps.cgi")
        struct = request.getRequestStruct(cmd)
        cmpstruct = {'identifier': 'v.buffer', 
                      'datainputs': [{'mimetype': 'text/xml', 'identifier': 'input', 'value': 'http://foo.map', 'encoding': 'utf-8'}, 
                                     {'datatype': 'float', 'identifier': 'distance', 'value': '20'}],
                      'responseform':
                        {'responsedocument': 
                         {'status': False, 'output': [{'identifier':'output','mimetype':'text/xml', 'asreference': False}], 'lineage': True, 'storeexecuteresponse': False}}}
        print struct
        print cmpstruct
        self.assertEqual(struct, cmpstruct, "简单命令解析")
        
    def testChainRequestCmd(self):
        """
        链请求命令解析
        """
        cmd = "v.buffer --l input=[v.to.points -n input=http://foo.map@mimetype=text/xml]@mimetype=text/xml@encoding=utf-8 distance=20 output=@mimetype=text/xml"
        request = ExecuteRequestStruct("http://localhost/cgi-bin/pywps.cgi")
        struct = request.getRequestStruct(cmd)
        cmpstruct = {'responseform': 
                     {'responsedocument': 
                      {'status': False, 'output': [{'identifier':'output','mimetype':'text/xml','asreference': False}], 'lineage': True, 'storeexecuteresponse': False}}, 
                     'identifier': 'v.buffer', 
                     'datainputs': [{'mimetype': 'text/xml', 'identifier': 'input', 'value': 
                                     {'responseform':
                                      {'responsedocument':
                                       {'status': False, 'output': [], 'lineage': False, 'storeexecuteresponse': False}}, 
                                      'identifier': 'v.to.points', 
                                      'datainputs': [{'mimetype': 'text/xml', 'identifier': 'input', 'value': 'http://foo.map'}]
                                      }, 
                                     'encoding': 'utf-8'}, 
                                    {'identifier': 'distance', 'value': '20'}
                                    ]
                     }
        print struct
        print cmpstruct
        self.assertEqual(struct, cmpstruct, "链请求解析")
    
if __name__=="__main__":
    testsuite = TestSuite((CmdInterpreteTest))
    
    TextTestRunner().run(testsuite)
