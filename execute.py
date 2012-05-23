#!/usr/bin/env python
#-*-coding:utf-8-*-

"""
/***************************************************************************
ExecuteRequest.py Wps富客户端执行请求编码和执行结果解码 
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
  
      def _wrapInputParam(self, param, *argv, **kwargs):
        """
        封装输入的参数为xml文本格式
        
        目前只支持 <DataInputs> 下的 <Data>类型, 没有考虑 <Reference> 数据类型的情况
        
        @param param: 描诉文档中(DescribeProcess)获取的输入参数列表信息
        @param kwargs: 输入参数字典列表
            identifier={'value':val[,attr:val]}
            不同类型可有的属性值分别如下:
                LiteralInput: {'Uom':""}
                ComplexData: {'MimeType':"",'Schema':"", 'Encoding':""}
                BoundingData: {None}
        """
        for key, value in kwargs.iteritems:
            if not param[key]:
                logging.error(key + "is not a input param")
                raise 
            else:
                input += "<wps:Input>\n"
                input += "<ows:Identifier>"+key+"</ows:Identifier>\n"
                input += "<ows:Title>"+key+"</ows:Title>\n"
                input += "<wps:Data>\n"
                data = ""
                if  isinstance(param[key], LiteralInputDef):
                    data = "<wps:LiteralData>{v}</wps:LiteralData>".format(v=value['value'])
                    if value['Uom']:
                        # 不支持的单位
                        if value['Uom'] not in param[key].theSupportUoMs['supported']:
                            logging.warn("Unit " + value['Uom'] + "dosn't supported and\
                             used the default uom")
                        else:
                            data = "<wps:LiteralData uom={uom}>{val}</wps:LiteralData>\
                            ".format(uom=value['Uom'], v=value['value'])
                elif isinstance(param[key], ComplexDataDef):
                    pass
                elif isinstance(param[key], BoundingDataDef):
                    data = "<wps:BoundingBoxData>{v}</wps:BoundingBoxData>".format(v=value['value'])
                    
                input += data + "\n"
                input += "</wps:Data>"
    
    def _wrapOutputParam(self,param, *argv, **kwargs):
        pass