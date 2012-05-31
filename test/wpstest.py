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
import os,sys
sys.path += [os.path.abspath('../')]
from unittest import TestCase
from unittest import TestSuite
from unittest import TextTestRunner
from unittest import main
from xml.dom import minidom
import logging

import wpsclient
from description import strProcessDescribe,processDescribe
from execute import *
        
logging.basicConfig(stream=sys.stdout, 
                    level=logging.DEBUG)

class CmdInterpreteTest(TestCase): 
    """
    命令行解释器测试用例
    """     
    def testSimpleCmd(self):
        """测试简单命令解析
        """
        cmd = "v.buffer --l input=http://foo.map@mimetype=text/xml@encoding=utf-8 distance=20@datatype=float output=@mimetype=text/xml"
        request = ExecuteRequest("http://localhost/cgi-bin/pywps.cgi")
        struct = request.getRequestStruct(cmd)
        struct = request.getRequestStruct(cmd)
        cmpstruct = {'identifier': 'v.buffer', 
                      'datainputs': [{'mimetype': 'text/xml', 'identifier': 'input', 'value': 'http://foo.map', 'type': 1, 'encoding': 'utf-8'}, 
                                     {'datatype': 'float', 'identifier': 'distance', 'type': 2, 'value': '20'}],
                      'responseform':
                        {'responsedocument': 
                         {'status': False, 'output': [{'identifier':'output','mimetype':'text/xml', 'asreference': False}], 'lineage': True, 'storeexecuteresponse': False}}}
#        if __debug__:
#            print struct
#            print cmpstruct
        self.assertEqual(struct, cmpstruct, "简单命令解析")
        
    def testChainRequestCmd(self):
        """链请求命令解析
        """
        cmd = "v.buffer --l input=[v.to.points -n input=http://foo.map@mimetype=text/xml]@mimetype=text/xml@encoding=utf-8 distance=20 output=@mimetype=text/xml"
        request = ExecuteRequest("http://localhost/cgi-bin/pywps.cgi")
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
#        if __debug__:
#            print struct
#            print cmpstruct
        self.assertEqual(struct, cmpstruct, "链请求解析")

class ExecuteTest(TestCase):
    """
    Execute执行请求测试
    """
    def setUp(self):
        self.request = ExecuteRequest("http://localhost/cgi-bin/pywps.cgi")
        
    def tearDown(self):
        pass
    
    def _assertWrapXMLEqualtoFile(self, cmd, file): 
        from xml.dom import minidom
        wrapxml = minidom.parseString(self.request.wrapParam(cmd['identifier'], 
                cmd['datainputs'], cmd['responseform'])).toprettyxml(newl='\n', encoding='utf-8')
        logging.info(wrapxml)
#        cmpxmlfile = open(file)
#        self.assertEqual(cmpxmlfile.read(), wrapxml)
        
    def testWrapParam1(self):
        """ Test1: ComplexData输入格式可访问的站点的数据. 如，WMS和WFS服务站点中的数据
        """
        cmd = {'datainputs': [{'encoding': 'utf-8',
                         'identifier': 'input',
                         'mimetype': 'text/xml',
                         'type': 1,
                         'value': 'http://foo.map'},
                        {'datatype': 'float',
                         'identifier': 'distance',
                         'type': 2,
                         'value': '20'}],
         'identifier': 'v.buffer', 
         'responseform': {'responsedocument': {'lineage': True,
                                               'output': [{'asreference': False,
                                                           'identifier': 'output',
                                                           'mimetype': 'text/xml'}],
                                               'status': False,
                                               'storeexecuteresponse': False}}}
        
        self._assertWrapXMLEqualtoFile(cmd, 'ComplexData输入格式可访问的站点的数据.xml')
        
    def testWrapParam2(self):
        """ Test2: ComplexData输入格式为另一个Execute请求(即 请求链测试)
        """
        cmd = {'datainputs': [{'encoding': 'utf-8',
                 'identifier': 'input',
                 'mimetype': 'text/xml',
                 'type': 1,
                 'value': {'datainputs': [{'identifier': 'input',
                                           'mimetype': 'text/xml',
                                           'type': 1,
                                           'value': 'http://foo.map'}],
                           'identifier': 'v.to.points',
                           'responseform': {'responsedocument': {'lineage': False,
                                                                 'output': [],
                                                                 'status': False,
                                                                 'storeexecuteresponse': False}}}},
                {'identifier': 'distance', 'type': 2, 'value': '20'}],
 				'identifier': 'v.buffer',
 				'responseform': {'responsedocument': {'lineage': True,
                                       'output': [{'asreference': False,
                                                   'identifier': 'output',
                                                   'mimetype': 'text/xml'}],
                                        'status': False,
                                        'storeexecuteresponse': False}}}
        
        self._assertWrapXMLEqualtoFile(cmd, 'ComplexData输入格式为另一个Execute请求.xml')
        
    def testWrapParam3(self):
        """ Test3: Reference输入格式
        """
        cmd = {'datainputs': [{'encoding': 'utf-8',
                 'identifier': 'input',
                 'mimetype': 'text/xml',
                 'type': 1,
                 'value': '',
                 'xlink:href': 'http://foo.map'},
                {'datatype': 'float',
                 'identifier': 'distance',
                 'type': 2,
                 'value': '20'}],
 				'identifier': 'v.buffer',
 				'responseform': {'responsedocument': {'lineage': True,
                                       'output': [{'asreference': False,
                                                   'identifier': 'output',
                                                   'mimetype': 'text/xml'}],
                                       'status': False,
                                       'storeexecuteresponse': False}}}
        
        self._assertWrapXMLEqualtoFile(cmd, 'Reference输入格式.xml')
        
    def testWrapParam4(self):
        """ Test4: ComplexData输入格式为本地矢量数据
        """
        datapath = os.path.abspath('testdata/streams_split/streams_cat__40120.shp')
        cmd = {'datainputs': [{'identifier': 'input',
                 'type': 1,
                 'value': 'file://' + datapath},
                {'datatype': 'float',
                 'identifier': 'distance',
                 'type': 2,
                 'value': '20'}],
 				'identifier': 'v.buffer',
 				'responseform': {'responsedocument': {'lineage': True,
                                       'output': [{'asreference': False,
                                                   'identifier': 'output',
                                                   'mimetype': 'text/xml'}],
                                       'status': False,
                                       'storeexecuteresponse': False}}}
        self._assertWrapXMLEqualtoFile(cmd, 'ComplexData输入格式为本地矢量数据.xml')
        
    def testWrapParam5(self):
        """ Test5: ComplexData输入格式为本地栅格数据
        """
        datapath = os.path.abspath('testdata/landcover.tiff')
        cmd = {'datainputs': [{'identifier': 'input',
                 'type': 1,
                 'value': 'file://' + datapath},
                {'datatype': 'float',
                 'identifier': 'distance',
                 'type': 2,
                 'value': '20'}],
                 'identifier': 'v.buffer',
                 'responseform': {'responsedocument': {'lineage': True,
                                       'output': [{'asreference': False,
                                                   'identifier': 'output',
                                                   'mimetype': 'text/xml'}],
                                       'status': False,
                                       'storeexecuteresponse': False}}}
        self._assertWrapXMLEqualtoFile(cmd, 'ComplexData输入格式为本地栅格数据.xml')

    
if __name__=="__main__":
    #main()
    testsuite1 = TestSuite()
    testsuite1.addTest(CmdInterpreteTest("testSimpleCmd"))
    testsuite1.addTest(CmdInterpreteTest("testChainRequestCmd"))
    
    testsuite2 = TestSuite()
    testsuite2.addTest(ExecuteTest('testWrapParam1'))
    testsuite2.addTest(ExecuteTest('testWrapParam2'))
    testsuite2.addTest(ExecuteTest('testWrapParam3'))
    testsuite2.addTest(ExecuteTest('testWrapParam4'))
    testsuite2.addTest(ExecuteTest('testWrapParam5'))
    
    TextTestRunner().run(testsuite2)

