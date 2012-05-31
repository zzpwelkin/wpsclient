#!/usr/bin/env python
#-*-coding:utf-8-*-

"""
/***************************************************************************
execute.py Wps富客户端执行请求编码和执行结果解码 
-------------------------------------------------------------------
 Date                 : 2012.5.23 9:30
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
import urllib2
from OGCCommon import WpsInputFileWrap 
from cmdinterpret import CmdParamToken

from description import *
from wpsclient import WpsClient

class ExecuteRequest(object):
    def __init__(self, serveurl ):
        self.theWpsclient = WpsClient(serveurl)
        
    def getRequestStruct(self, cmd):
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
        
        @note: 目前命令解译后，只支持{responsedocument}返回格式
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
                    for key in ['encoding', 'mimetype', 'schema', 'xlink:href']:
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

    def wrapParam(self, identifier, datainputs, responseform, version="1.0.0", lang='en-CA' , service="WPS"):
            """
            封装输入参数为 POST 方式的Execute操作请求
            
            目前只支持 <DataInputs> 下的 <Data>类型, 没有考虑 <Reference> 数据类型的情况
            
            @param identifier: 执行请求的标识符
            @param datainputs: 输入参数字典列表
                格式为: datainputs = [{'value':val, 'type'=1/2/3, (,attr:val)},...]]
                type类型中(1/2/3)代表数据类型，1: ComplexData 2:LiteralData 3:BoundingBoxData
            @param  responseform: 请求的回复格式定义
                格式为:responseform = {'responsedocument':{'status':False/True,'lineage': True/False, 'storeexecuteresponse': True/False, 'output':[{'identifier'=val,'asreference'=True/False(,value,...)}]}
                目前只支持responsedocument格式的回复请求参数设置
            """
            def AttrWrap(keylist, values):
                res = " "
                for key in keylist:
                    try:
                        res += " {attr}=\"{val}\" ".format(attr = key, val = values[key.lower()])
                    except:
                        continue
                return res
        
            requestXML = "<wps:Execute service=\"{s}\" version=\"{v}\" xml:lang=\"{lg}\" ".format(
                            s=service, v=version, lg=lang)
            requestXML += "xmlns:wps=\"http://www.opengis.net/wps/1.0.0\" "
            requestXML += "xmlns:ows=\"http://www.opengis.net/ows/1.1\" "
            requestXML += "xmlns:xlink=\"http://www.w3.org/1999/xlink\" "
            requestXML += "xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" "
            requestXML += "xsi:schemaLocation=\"http://www.opengis.net/wps/1.0.0../wpsExecute_request.xsd\">"
            requestXML += "<ows:Identifier>{id}</ows:Identifier>".format(id=identifier)
            requestXML += "<wps:DataInputs>"
            for input in datainputs:
                    requestXML += "<wps:Input>"
                    requestXML += "<ows:Identifier>"+ input['identifier'] +"</ows:Identifier>"
                    requestXML += "<wps:Data>"
                    if input['type'] == 1:
                        # ComplexData or Reference
                        if input['value'] == '':
                            # Reference
                            requestXML += "<wps:Reference" + AttrWrap(['mimeType', 'encoding', 'schema'],input)
                            requestXML += " xlink:href=\"{val}\"> </wps:Reference>".format(
                                            val = input['xlink:href'])
                        else:
                            # ComplexDataType
                            if isinstance(input['value'],dict):
                                # ComplexData is another resource request, e.g. other wps execute(i.e. request chain)
                                requestXML += "<wps:ComplexData" + AttrWrap(['mimeType', 'encoding', 'schema'],input)
                                requestXML += " > {val} </wps:ComplexData> ".format(val = 
                                        self.wrapParam(input['value']['identifier'], 
                                                       input['value']['datainputs'],
                                                       input['value']['responseform']))
                            else:
                                logging.info(input['value'])
                                wrap = WpsInputFileWrap(input['value'])
                                if wrap:
                                    # Value inputting from local file or ftp service
                                    requestXML += '<wps:ComplexData mimeType=\"{mt}\" encoding=\"{cod}\" '.format(mt=wrap[1],cod=wrap[2])
                                    fobj = open(wrap[0],'rb')
                                    requestXML += "> {val} </wps:ComplexData>".format(val = ''.join([line.rstrip('\n') for line in fobj.readlines() if line.find('<?xml')<0]))
                                else:
                                    # Text Value or can be getted from http service
                                     requestXML += "<wps:ComplexData" + AttrWrap(['mimeType', 'encoding', 'schema'],input)
                                     requestXML += "> {val} </wps:ComplexData>".format(val = input['value'])
                                     
                    elif input['type'] == 2:
                        # LiteralData
                        requestXML += "<wps:LiteralData"
                        for key in ['dataType', 'uom']: 
                            try:
                                requestXML += " {attr}=\"{val}\" ".format(attr=key, val = input[key.lower()])
                            except:
                                continue
                        requestXML += ">"
                        requestXML += input['value'] + "</wps:LiteralData>"
                    else:
                        # BoundingBoxData
                        requestXMl += "<wps:BoundingBoxData> {val} </wps:BoundingBoxData}".format(
                                        val = input['value'])
                    requestXML += "</wps:Data></wps:Input>"
            requestXML += "</wps:DataInputs>"
            requestXML += "<wps:ResponseForm>"
            
            # 确认输出格式
            try:
                responseform['responsedocument']
            except:
                raise Exception("目前p只支持responsedocument格式的回复请求参数设置")
            else: 
                requestXML += "<wps:ResponseDocument"
                for attr in ['storeExecuteResponse', 'lineage', 'status']:
                    if responseform['responsedocument'][attr.lower()] == True:
                        requestXML += " {a}=\"{val}\" ".format(a=attr, val='true')
                    else:
                        requestXML += " {a}=\"{val}\" ".format(a=attr, val='false')
                requestXML += ">"
                for output in responseform['responsedocument']['output']:
                    requestXML += "<wps:Output "
                    if output['asreference'] == True:
                        requestXML += " asReference=\"{val}\" ".format(val='true')
                    else:
                        requestXML += " asReference=\"{val}\" ".format(val='false')
                    requestXML += ">"
                    requestXML += "<ows:Identifier {attrs} >{val}</ows:Identifier>".format(
                                    attrs=AttrWrap(['encoding', 'mimeType', 'schema', 'uom'],output), 
                                    val=output['identifier'])
                    for elem in ['Title','Abstract']:
                        try:
                            requestXML += "<ows:{e}>{val}</ows:{e}>".format(e=elem, 
                                        val=output[elem.lower()])
                        except:
                            continue
                    requestXML += "</wps:Output>"
                requestXML += "</wps:ResponseDocument></wps:ResponseForm>"
            requestXML += "</wps:Execute>"
            return requestXML           
#    def _wrapOutputParam(self,param, *argv, **kwargs):
#        pass

    def request(self, identifier, datainputs, responseform , lang='en-CA'):
        f = urllib2.urlopen(self.theWpsclient.theServeUrl, self.wrapParam(identifier, datainputs, responseform, lang=lang))
        return f.read()
    
if __name__ == "__main__":
    import os
    datapath = os.path.abspath('test/testdata/landcover.tiff')
    cmd = {'datainputs': [{'identifier': 'indata',
         'type': 1,
         'value': 'file://' + datapath}],
         'identifier': 'complexRaster',
         'responseform': {'responsedocument': {'lineage': False,
                               'output': [{'asreference': False,
                                           'identifier': 'outdata'}],
                               'status': False,
                               'storeexecuteresponse': False}}}
    request = ExecuteRequest("http://localhost/cgi-bin/pywps_test.cgi")
    print request.request(cmd['identifier'], cmd['datainputs'], cmd['responseform'])