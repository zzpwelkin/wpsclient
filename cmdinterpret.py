#!/usr/bin/env python
#-*-coding:utf-8-*-

"""
/***************************************************************************
cmdinterprete.py Wps富客户端命令行解释器 
-------------------------------------------------------------------
 Date                 : 2012.5.21 9:50
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
import re

class CmdParamToken(object):
    """
    解析输入的命令行
    
    输入命令格式文义如下:
        Command := Identifier*(--l|--m|--s)*(“ “)DataInputs*(“ “)ResponseForm
        Identifier := [identifier of process from process description]
        DataInputs := Input *(*(“ “)Input)
        Input := BoundingBox | Literal | Complex | Reference

        Complex := InputId “=” ComplexValue * ( “@”ComplexAttribute ) 
        ComplexValue = Value | “[“Command”]”
        ComplexAttribute := ComplexAttributeName “=” Value
        ComplexAttribute := “mimetype” | “encoding” | “schema”

        Literal := InputId “=” Value * ( “@”LiteralAttribute ) 
        LiteralAttribute := LiteralAttribute “=” Value
        LiteralAttribute := “datatype” | “uom”

        BoundingBox := InputId “=” BoundingBoxValue
        BoundingBoxValue := <As defined in OGC #06-121r3 Subclase 10.2.3>

        ReferenceAttribute := ReferenceAttributeName “=” Value
        ReferenceAttributeName := “href” | ComplexAttributeName
        
        ResponseForm := *(identifier=OutputAttr)
        
        OutputAttr := [(@mimetype=Value)(@encoding=Value)(@schema=Value)(@uom=Value)(@title=Value)(@abstract=Value)]+
        (注:[]+表示OutputAttr至少有一个以上(@key=value)格式的属性)
        
        InputId := [Identifier of the input from the process description]
        Value := [URL Encoded value being set]
        
        如:v.buffer --l input=http://foo.map@mimetype=text/xml@encoding=utf-8 distance=20@datatype=float output=@mimetype=text/xml
    """
    def __init__(self, cmd):
          self.theCmd = cmd
          
    def getIdentifier(self):
        if self.theCmd == '':
            return None
        identifier = self.theCmd.split()[0]
        
        for sz in ['-', '=', '/', ':']:
            if sz in identifier:
                return None
        else:
            return identifier
    
    def getParamPair(self):
        """
        迭代的依次获取参数对:{key,value}
        
        Example: --l: --[a-z]+         
                input=http://foo.map@mimetype=text/xml: [a-z]+=[\w/:.@=]+
                input=@xlin:href=http://foo.map@mimetype=text/xml: [a-z]+=[\w/:.@=]+
                input=[v.convert input=http://foo.map@mimetype=text/xml output=text/xml]: [a-z]+=\[.*\][\w/:.@=]*
        """
        for parampair in re.findall("--[a-z]|[a-z]+=\[.*\][\w/:.@=-]*|[a-z]+=[\w/:.@=-]+",
                                    self.theCmd):
            param = ['', '', {}]
            
            if '[' in parampair and ']' in parampair:
                keyvalue = parampair.split('[')
                param[0] = keyvalue[0].rstrip('=')
                attrkeyvalue = keyvalue[1].split(']')
                param[1]= attrkeyvalue[0]
                
                if attrkeyvalue[1] == '':
                    param[2] = {}
                else:
                    attr = {}
                    for  attrkvp in attrkeyvalue[1].split('@'):
                        if attrkvp != "": 
                            kvp = attrkvp.split('=')  
                            attr[kvp[0]] = kvp[1]
                    param[2]= attr
            else:
                keyvalue = parampair.split('@')
                if '=' not in keyvalue[0]:
                    param[0] = keyvalue[0]
                    param[1] = ''
                    param[2] = {}
                else:
                    kvp = keyvalue[0].split('=')
                    param[0] = kvp[0]
                    param[1] = kvp[1]
                    
                    keyvalue.remove(keyvalue[0])
                    attr = {}
                    for  attrkvp in keyvalue:
                        if attrkvp != "":
                            kvp = attrkvp.split('=')  
                            attr[kvp[0]] = kvp[1]
                    param[2] = attr
                        
            yield param[0], param[1], param[2]
        