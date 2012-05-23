#!/usr/bin/env python
#-*-coding:utf-8-*-

"""
/***************************************************************************
description.py Wps描述请求结果解析
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
from OGCCommon import *

"""
该模块中的数据类型定义，详细参考[05-007r7OGC WPS]
"""
class ProcessBrief(WpsDescription):
    
    def __init__(self):
        WpsDescription.__init__(self)
        self.theProcessVersion = None
        self.theStoreSupported = False
        self.theStatusSupported = False
        self.theProfile = None 
    
    def __str__(self):
        brief = "{identifier} v.{version}\n\tTitle:{title}\n\tAbstract:{abstract}".format(
                identifier=self.theIdentifier, version=self.theProcessVersion, 
                title=self.theTitle, abstract=self.theAbstract)
        
    def getProcessBrief(self, elem):
        self.getWpsDescription(elem)
        self.theProcessVersion =elem.attributes.getNamedItemNS(OGCNamespaceURI['wps1.0.0'],
                                                                  'processVersion').nodeValue
                                                                  
        if elem.attributes.getNamedItem('storeSupported') and elem.attributes.getNamedItem(
            'storeSupported').nodeValue == "true":
            self.theStoreSupported = True
            
        if elem.attributes.getNamedItem('statusSupported') and elem.attributes.getNamedItem(
            'statusSupported').nodeValue == "true":
            self.theStoreSupported = True
        
        profile = elem.getElementsByTagNameNS(OGCNamespaceURI['ows1.1'],"Profile")
        if profile:
            self.theProfile = profile[0].firstChild.nodeValue  
            
        return self
    
class LiteralOutputDef(object):
    #theDataType = {}
    #theSupportUoMs = {'default':"", 'supported':[]}
    def __init__(self):
            self.theDataType = {}
            self.theSupportUoMs = {'default':"", 'supported':[]}
            
    def __str__(self):
        pass
    
    def getLiteralOutputDef(self, elem):
        # DataType
        datatype = elem.getElementsByTagNameNS(OGCNamespaceURI['ows1.1'],
                            'DataType')[0]
        if datatype:
            self.theDataType['value'] = datatype.firstChild.nodeValue
            self.theDataType['reference'] = datatype.attributes.getNamedItemNS(
                    OGCNamespaceURI['ows1.1'],'reference').nodeValue
                    
        # SupportUoMs
        Uoms = elem.getElementsByTagName('UOMs')
        if Uoms:
            self.theSupportUoMs['default'] = Uoms.getElementsByTagName('default').getElementsByTagNameNS(
                OGCNamespaceURI['ows1.1'], 'UOM')[0].firtNode.nodeValue
            supportedUoms = Uoms.getElementsByTagName('Supported').getElementsByTagNameNS(
                OGCNamespaceURI['ows1.1'], 'UOM')
            for uom in supportedUoms:
                self.theSupportUoMs['supported'].append(uom.firstNode.nodeValue)
                
        return self

class LiteralInputDef(LiteralOutputDef):
    """
    如果theLitaralValue为空，则表示为任意值(AnyValue)
    """
    
    def __init__(self):
        LiteralOutputDef.__init__(self)
        self.theDefaultValue = None
        self.theLiteralValue = None
    
    def __str__(self):
        res = ""
        isCR = ""
        if self.theLiteralValue :
            res = res + "options:{opt}".format(opt = str(self.theLiteralValue))    
            isCR = "\n"       
        if self.theDefaultValue:
            res  = res + isCR + "default:{default}".format(default = self.theDefaultValue)
    
        return res 
    
    def getLiteralInputDef(self, elem):
        self.getLiteralOutputDef(elem)
        # DefaultValue
        if elem.getElementsByTagName('DefaultValue'):
            self.theDefaultValue = elem.getElementsByTagName('DefaultValue')[0].firstChild.nodeValue
            
        # LiteralValue
        if elem.getElementsByTagNameNS(OGCNamespaceURI['ows1.1'], 'AllowedValues'):
            self.theLiteralValue = AllowedValuesDef().getAllowedValuesDef(
                elem.getElementsByTagNameNS(OGCNamespaceURI['ows1.1'], 'AllowedValues'))
            
        elif elem.getElementsByTagNameNS(OGCNamespaceURI['ows1.1'], 'ValuesReference'):
            valueref = elem.getElementsByTagNameNS(OGCNamespaceURI['ows1.1'], 'ValuesReference')
            self.theLiteralValue = {'reference':valueref.attributes.getNamedItemNS(
                OGCNamespaceURI['wps1.0.0'],'reference').nodeValue, 'valuesForm':
                valueref.attributes.getNamedItem('valuesForm').nodeValue}
            
        return self
            
class ComplexDataDef(object):
    
    def __init__(self):
        self.theMaxMetabytes = None
        self.theDefault = None
        self.theSupport = []
    
    def __str__(self):
        res = ""
#        for spt in self.theSupport:
#            res = str(spt)+"\n"
        res = "\n".join(map(str, self.theSupport))
        return "supported:{spt}\ndefault:{dft}".format(spt=res, dft=self.theDefault)
    
    def _getFormatDef(self, elem):
        # format
        res = {'mimetype':"", 'encoding':"", 'schema':""}
        res['mimetype'] = elem.getElementsByTagName('MimeType')[0].firstChild.nodeValue
        if elem.getElementsByTagName('Encoding'):
            res['encoding'] = elem.getElementsByTagName('Encoding')[0].firstChild.nodeValue
        if elem.getElementsByTagName('Schema'):
            res['schema'] = elem.getElementsByTagName('Schema')[0].firstChild.nodeValue
        return res
        
    def getComplexDataDef(self, elem):
        #  {maximumMegabytes} attribute
        minmaxbytes = elem.attributes.getNamedItem('maximumMegabytes')
        if minmaxbytes:
            self.theMaxMetabytes = minmaxbytes.nodeValue
        
        # default and supported formats    
        self.theDefault = self._getFormatDef(elem.getElementsByTagName('Default')[0])
        for fmtelem in elem.getElementsByTagName('Supported')[0].getElementsByTagName('Format'):
            self.theSupport.append(self._getFormatDef(fmtelem))
            
        return self

class BoundingDataDef(object):
    def getBoundingDataDef(self, elem):
        pass

class InputDescription(WpsDescription):
    
    def __init__(self):
        self.theMinOccurs = 0
        self.theMaxOccurs = 0
        self.theInputForm = None
    
    def __str__(self):
        indentnum = len(self.theIdentifier) + 5
        inputform = (" "*indentnum).join(("\n"+str(self.theInputForm)).splitlines(True))
        inputform.strip("\n")
        return "{idt}    {title}{abt}".format(idt=self.theIdentifier, title=self.theTitle, 
                                                   abt = inputform)
    
    def getInputDescription(self, elem):
        self.getWpsDescription(elem)
        
        self.theMinOccurs = int(elem.attributes.getNamedItem('minOccurs').nodeValue)
        self.theMaxOccurs = int(elem.attributes.getNamedItem('maxOccurs').nodeValue)
        
        if elem.getElementsByTagName('LiteralData'):
            self.theInputForm = LiteralInputDef().getLiteralInputDef(elem.getElementsByTagName('LiteralData')[0])
        elif elem.getElementsByTagName('ComplexData'):
            self.theInputForm = ComplexDataDef().getComplexDataDef(elem.getElementsByTagName('ComplexData')[0])
        else:
            self.theInputForm = BoundingDataDef().getBoundingDataDef(elem.getElementsByTagName('BoundingBoxData')[0])
            
        return self
        
class OuputDescription(WpsDescription):
    
    def __init__(self):
        self.theOutputForm = None
    
    def __str__(self):
        indentnum = len(self.theIdentifier) + 5
        outputform = (" "*indentnum).join(("\n"+str(self.theOutputForm)).splitlines(True))
        outputform.strip("\n")
        return "{idt}    {title}{abt}".format(idt=self.theIdentifier, title=self.theTitle, 
                                                   abt = outputform)
        
    def getOuputDescription(self, elem):
        self.getWpsDescription(elem)
        
        if elem.getElementsByTagName('LiteralOutput'):
            self.theOutputForm = LiteralOutputDef().getLiteralOutputDef(elem.getElementsByTagName('LiteralOutput')[0])
        elif elem.getElementsByTagName('ComplexOutput'):
            self.theOutputForm = ComplexDataDef().getComplexDataDef(elem.getElementsByTagName('ComplexOutput')[0])
        else:
            self.theOutputForm = BoundingDataDef().getBoundingDataDef(elem.getElementsByTagName('BoundingBoxOutput')[0])
            
        return self
    
def processDescribe(xmldoc):
    """
    从XML文档对象中获取处理描诉信息,格式为[identifier, abstract，{inputs},{outputs}]
    
    @param xmldoc: xml文档对象
    """
    inputs = []
    outputs = []
    try:
        processElem = xmldoc.getElementsByTagName('ProcessDescription')[0]
    except:
        excep = xmldoc.getElementsByTagName('Exception')[0].attributes.getNamedItem('exceptionCode').nodeValue
        
        loc = xmldoc.getElementsByTagName('Exception')[0].attributes.getNamedItem('locator').nodeValue
        raise Exception(excep + ' at ' + loc)
    else:
        if not processElem:
            raise 
        else:   
            # 头描诉信息
            processbrief = ProcessBrief().getProcessBrief(processElem)
                
            # 输入参数列表
            for input in processElem.getElementsByTagName('Input'):
                inputs.append(InputDescription().getInputDescription(input))
                    
            # 输出参数列表
            for output in processElem.getElementsByTagName('Output'):
                outputs.append(OuputDescription().getOuputDescription(output))
                
            # 添加到处理描诉列表中
                
        return [processbrief, inputs, outputs]

def strProcessDescribe(process):
    """
    以可读的方式描诉{process}
    
    @param  process: processDescribe()方法返回的描诉结构体
    """
    ident = "Identifier: " + process[0].theIdentifier + "\n\n"
    
    desp = "Description:\n  " + process[0].theTitle + "\n\n"
        
    abt = "Abstract:\n  " + process[0].theAbstract + "\n\n"
        
    usage = "usage:\n  " + process[0].theIdentifier + " "
    
    flags = "Flag:\n"
        
    inputs = "Inputs:\n"
        
    outputs = "Outputs:\n"
    
    # flags
    if process[0].theStoreSupported:
        flags = flags + "  --m   Output as stored"
    if process[0].theStatusSupported:
        flags = flags + "  --s   Respond as asynchronization with status report"
        
    # inputs param
    for input in process[1]:
        # usage set
        valuetype = ""
        valueft = ""
        if isinstance(input.theInputForm, ComplexDataDef):
            valuetype = "name[@mimetype=v][@encoding=v][@schema=v]"
        elif isinstance(input.theInputForm, LiteralInputDef):
            valuetype = input.theInputForm.theDataType['value']+"[@datatype=v][@uom=v]"
        else:
            valuetype = "bound"
                
        ft = " {idt} "
        if input.theMinOccurs == 0 and input.theMaxOccurs == 1:
            ft = " [{idt}={type}]"
        elif input.theMinOccurs == 0 and input.theMaxOccurs > 1:
            ft = " [{idt}={type}[,{type},...]]"
        elif input.theMinOccurs == 1 and input.theMaxOccurs == 1:
            ft = " {idt}={type}"
        elif input.theMinOccurs == 1 and input.theMaxOccurs > 1:
            ft = " {idt}={type}[,{type},...]"
            
        usage = usage + ft.format(idt=input.theIdentifier, type=valuetype)
            
        # input list set
        inputs = inputs + ((" "*8).join(("\n"+str(input)).splitlines(True))).strip("\n") + "\n"
    
    # outputs param
    for output in process[2]:
        # usage set
        valuetype = ""
        valueft = ""
        if isinstance(output.theOutputForm, ComplexDataDef):
            valuetype = "name"
        elif isinstance(output.theOutputForm, LiteralOutputDef):
            valuetype = output.theOutputForm.theDataType['value']
        else:
            valuetype = "bound"
            
        usage = usage + " {idt}={type}".format(idt=output.theIdentifier, type=valuetype)
        outputs = outputs + " "*8 + (" "*8).join(str(output).splitlines(True)) + "\n"
        
    return desp + abt + usage + "\n\n" + flags + "\n\n" + inputs + "\n" + outputs
