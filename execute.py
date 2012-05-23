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

class ExecuteRequest(object):
      def wrapParam(self, identifier, datainputs, responseform, version="1.0.0", lang='en-CA' , service="Wps"):
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
        requestXML = "<wps:Execute service=\"{s}\" version=\"{v}\" xml:lang=\"{lg}\"> \
        <ows:Identifier>{id}</ows:Identifier>\n".format(s=service, v=version, 
                                                      lg=lang, id=identifier)
        requestXML += "<wps:DataInputs>\n"
        for input in datainputs:
                requestXML += "<wps:Input>\n"
                requestXML += "<ows:Identifier>"+ input['identifier'] +"</ows:Identifier>\n"
                requestXML += "<wps:Data>\n"
                if input['type'] == 1:
                    # ComplexData
                    if input['value'] == '':
                        requestXML += "<wps:Reference"
                    else:
                        requestXML += "<wps:ComplexData"
                    for key in ['mimeTypt', 'encoding', 'schema']:
                        try:
                            requestXML += " {attr}=\"{val}\" ".format(attr = key, 
                                        val = input[key.lower()])
                        except:
                            continue
                    if input['value']=='':
                        # Reference
                        requestXML += " xlink:href=\"{val}\" </wps:Reference>".format(
                                        val = input['xlink:href'])
                    else:
                        if isinstance(input['value'],dict):
                            requestXML += " >\n {val} </wps:ComplexData> ".format(val = 
                                    self.wrapParam(input['value']['identifier'], 
                                                   input['value']['datainputs'],
                                                   input['value']['responseform']))
                        else:
                            requestXML += ">\n {val} </wps:ComplexData>".format(val = input['value'])
                elif input['type'] == 2:
                    # LiteralData
                    requestXML += "<wps:LiteralData"
                    for key in ['dataType', 'uom']: 
                        try:
                            requestXML += " {attr}=\"{val}\" ".format(attr=key, val = input[key.lower()])
                        except:
                            continue
                    requestXML += ">\n"
                    requestXML += input['value'] + "</wps:LiteralData>"
                else:
                    # BoundingBoxData
                    requestXMl += "<wps:BoundingBoxData> {val} </wps:BoundingBoxData}\n".format(
                                    val = input['value'])
                requestXML += "</wps:Data>\n</wps:Input>"
        requestXML += "</wps:DataInputs>"
        requestXML += "<wps:ResponseForm>\n"
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
            requestXML += ">\n"
            for output in responseform['responsedocument']['output']:
                requestXML += "<wps:Output "
                if output['asreference'] == True:
                    requestXML += " asReference=\"{val}\" ".format(val='true')
                else:
                    requestXML += " asReference=\"{val}\" ".format(val='false')
                requestXML += ">\n"
                requestXML += "<ows:Identifier"
                for attr in ['encoding', 'mimeType', 'schema', 'uom']:
                    try:
                        requestXML += " {attr}=\"{val}\" ".format(attr=key, val = output[key.lower()])
                    except:
                        continue
                requestXML += ">{val}</ows:Identifier>".format(val=output['identifier'])
                for elem in ['Title','Abstract']:
                    try:
                        requestXML += "<ows:{e}>{val}</ows:{e}>".format(e=elem, 
                                    val=output[elem.lower()])
                    except:
                        continue
            requestXML += "</wps:ResponseDocument>\n<wps:ResponseForm>"
        requestXML += "</wps:Execute>"
        return requestXML           
#    def _wrapOutputParam(self,param, *argv, **kwargs):
#        pass