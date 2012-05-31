#!/usr/bin/env python
#-*-coding:utf-8-*-

"""
/***************************************************************************
doctest.py docstring方法单元测试 
-------------------------------------------------------------------
 Date                 : 2012.5.29 11:40
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
import unittest
import doctest

suite = unittest.TestSuite()

suite.addTest(doctest.DocFileSuite('docstringtest/Eexcute请求命名格式解析.docstr',module_relative=True))
suite.addTest(doctest.DocFileTest('docstringtest/Execute请求XML封装.py',module_relative=True))

unittest.TextTestRunner().run(suite)