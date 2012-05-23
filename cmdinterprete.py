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
from description import *
from wpsclient import WpsClient
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
        
class ExecuteRequestStruct(object):
    """
    将输入的命令转换为pywps中的存储结构
    
    Example:  
        输入:"v.buffer --l input=http://foo.map@mimetype=text/xml@encoding=utf-8 distance=20@datatype=float output=@mimetype=text/xml"
        输出:{'identifier': 'v.buffer', 
                'datainputs': [{'mimetype': 'text/xml', 'identifier': 'input', 'value': 'http://foo.map', 'encoding': 'utf-8'}, 
                                {'datatype': 'float', 'identifier': 'distance', 'value': '20'}],
                'responseform':
                    {'responsedocument': 
                     {'status': False, 'output': [{'identifier':'output','mimetype':'text/xml', 'asreference': False}], 'lineage': True, 'storeexecuteresponse': False}}}
        具体详细参数设置看处理描诉部分，用法可参考 CmdInterpreteTest 测试用例            
    @return: 
        返回数据结构为:{'identifier':(value), 
              'datainputs':([{values},...])}
              'responseform':{'responsedocument':{'status':False/True,'lineage': True/False, 'storeexecuteresponse': True/False, 'output':[{value,...}]}
    
    @note: 
    """ 
    def __init__(self, serveurl ):
        self.theWpsclient = WpsClient(serveurl)
    def getRequestStruct(self, cmd):
        """
        目前命令解译后，只支持{responsedocument}返回格式
        """
        def getInParams(params, paramId):
            for param in params:
                if param.theIdentifier == paramId:
                    return param
            return None
        res = {'identifier':"", 'datainputs':[], 'responseform':{}}
        res['responseform']['responsedocument'] = {}
        res['responseform']['responsedocument']['output'] = []
        res['responseform']['responsedocument']['status'] = False
        res['responseform']['responsedocument']['storeexecuteresponse'] = False
        res['responseform']['responsedocument']['lineage'] = False       
        
        cmdtoken = CmdParamToken(cmd)
        res['identifier'] = cmdtoken.getIdentifier()
        descstruct = self.theWpsclient.ProcessDescribe(res['identifier'])
        
        for paramId, value,attrpair in cmdtoken.getParamPair():
            if paramId == "--m":
                res['responseform']['storeexecuteresponse'] = True
            elif paramId == "--s":
                res['responseform']['status'] = True
            elif paramId == "--l" :
                res['responseform']['responsedocument']['lineage'] = True
            elif getInParams(descstruct[1], paramId):
                # 如果为输入参数
                input = {}
                input['identifier'] = paramId
                inputparam = getInParams(descstruct[1], paramId)
                if isinstance(inputparam.theInputForm,ComplexDataDef):
                    # set value
                    input['type'] = 1
                    if not CmdParamToken(value).getIdentifier():
                        input['value'] = value
                    else:
                        input['value'] = self.getRequestStruct(value)
                    #set other attributes
                    for key in ['encoding', 'mimetype', 'schema']:
                        try:
                            input[key] = attrpair[key]
                        except:
                                continue   
                elif isinstance(inputparam.theInputForm, LiteralInputDef):
                    input['type'] = 2
                    input['identifier'] = paramId
                    input['value'] = value
                    try:
                        input['datatype'] = attrpair['datatype']
                    except:
                        pass
                    try:
                        input['uom'] = attrpair['uom']
                    except:
                        pass
                elif isinstance(inputparam, BoundingDataDef):
                    input['type'] = 3
                    input['value'] = value
                res['datainputs'] += [input]
            elif getInParams(descstruct[2], paramId):
                # 如果为输入参数
                output = {}
                output['identifier'] = paramId
                try:
                    if attrpair['asreference'] and res['responseform']['storeexecuteresponse']:
                        ouput['asreference'] = True
                except:
                    output['asreference'] = False
                for key in ['encoding', 'mimetype', 'schema', 'uom', 'title', 'abstract']:
                    try:
                        output[key] = attrpair[key]
                    except:
                        continue
                res['responseform']['responsedocument']['output'] += [output]
        return res
