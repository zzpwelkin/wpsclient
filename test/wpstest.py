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
from execute import *
        
class CmdInterpreteTest(TestCase): 
    
    def runTest(self):
        self.testSimpleCmd()
        self.testChainRequestCmd()
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
                      'datainputs': [{'mimetype': 'text/xml', 'identifier': 'input', 'value': 'http://foo.map', 'type': 1, 'encoding': 'utf-8'}, 
                                     {'datatype': 'float', 'identifier': 'distance', 'type': 2, 'value': '20'}],
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
                     'datainputs': [{'mimetype': 'text/xml', 'type': 1, 'identifier': 'input', 'value': 
                                     {'responseform':
                                      {'responsedocument':
                                       {'status': False, 'output': [], 'lineage': False, 'storeexecuteresponse': False}}, 
                                      'identifier': 'v.to.points', 
                                      'datainputs': [{'mimetype': 'text/xml', 'identifier': 'input', 'type': 1, 'value': 'http://foo.map'}]
                                      }, 
                                     'type': 1, 'encoding': 'utf-8'}, 
                                    {'identifier': 'distance', 'type': 2, 'value': '20'}
                                    ]
                     }
        print struct
        print cmpstruct
        self.assertEqual(struct, cmpstruct, "链请求解析")

class ExecuteTest(TestCase):
    """
    Execute执行请求测试
    """
    def setUp(self):
        self.theCmdInt = ExecuteRequestStruct("http://localhost/cgi-bin/pywps.cgi")
        self.theExecuteResqObj = ExecuteRequest()
        
    def tearDown(self):
        pass
    
    def testWrapParam1(self):
        """
        简单的测试ComplexData和LiteralData格式的输入数据
        """
        cmd = "v.buffer --l input=http://foo.map@mimetype=text/xml@encoding=utf-8 distance=20@datatype=float output=@mimetype=text/xml"
        ResqStruct = self.theCmdInt.getRequestStruct(cmd)
        comparaXML = ""
        resqxml = self.theExecuteResqObj.wrapParam(ResqStruct['identifier'], 
            ResqStruct['datainputs'], ResqStruct['responseform'])
        print resqxml
        self.assertEqual(resqxml, 
            comparaXML, "")
    def testWrapParam2(self):
        """
        测试输入为Reference类型的情况
        """
        cmd = "v.buffer --l input=@http://foo.map@mimetype=text/xml@encoding=utf-8 distance=20@datatype=float output=@mimetype=text/xml"
        ResqStruct = self.theCmdInt.getRequestStruct(cmd)
        comparaXML = ""
        resqxml = self.theExecuteResqObj.wrapParam(ResqStruct['identifier'], 
            ResqStruct['datainputs'], ResqStruct['responseform'])
        print resqxml
        self.assertEqual(resqxml, 
            comparaXML, "")
    
    def testWrapChainParam(self):
        """
        测试请求链XML文档封装的结果
        """
        cmd = "v.buffer --l input=[v.to.points -n input=http://foo.map@mimetype=text/xml]@mimetype=text/xml@encoding=utf-8 distance=20 output=@mimetype=text/xml"
        ResqStruct = self.theCmdInt.getRequestStruct(cmd)
        comparaXML = ""
        resqxml = self.theExecuteResqObj.wrapParam(ResqStruct['identifier'], 
            ResqStruct['datainputs'], ResqStruct['responseform'])
        print resqxml
        self.assertEqual(resqxml, comparaXML, "")

if __name__=="__main__":
    main()
