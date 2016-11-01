#!/usr/bin/python
#coding=utf8
# xlswriter.py
"""
# Author: Bill
# Created Time : 2016年02月23日 星期二 16时34分11秒

# File Name: w.py
# Description:

"""
import mylib.xlwt as xlwt

class XLSWriter(object):
    """A XLS writer that produces XLS files from unicode data.
    """
    #{{{__init__
    def __init__(self, file, encoding='utf-8'):
        # must specify the encoding of the input data, utf-8 default.
        self.file = file
        self.encoding = encoding
        self.wbk = xlwt.Workbook()
        self.sheets = {}
    #}}}
    #{{{add_image
    def add_image(self,bmp_name='',x='',y='',length='',title_name='ceshi',sheet_name='sheet'):
        if sheet_name not in self.sheets:
            # Create if does not exist
            self.create_sheet(sheet_name)
        tall_style = xlwt.easyxf('font:height 820;')
        self.sheets[sheet_name]['sheet'].row(self.sheets[sheet_name]['rows']).set_style(tall_style)
        self.sheets[sheet_name]['sheet'].insert_bitmap('logo.bmp',\
                                                       x,y,0,0,scale_x=0.40,\
                                                       scale_y=0.60)
        if length:
            style = xlwt.XFStyle() # Create Style
            font = xlwt.Font()
            font.bold = True
            font.height = 0x00FD
            style.font = font
            alignment = xlwt.Alignment() # Create Alignment
            alignment.horz = xlwt.Alignment.HORZ_CENTER 
            # May be: HORZ_GENERAL,HORZ_LEFT, HORZ_CENTER, HORZ_RIGHT, HORZ_FILLED, HORZ_JUSTIFIED,HORZ_CENTER_ACROSS_SEL, HORZ_DISTRIBUTED
            alignment.vert = xlwt.Alignment.VERT_CENTER 
            # May be: VERT_TOP,VERT_CENTER, VERT_BOTTOM, VERT_JUSTIFIED, VERT_DISTRIBUTED
            style.alignment = alignment # Add Alignment to Style
            self.sheets[sheet_name]['sheet'].write_merge(self.sheets[sheet_name]['rows'],self.sheets[sheet_name]['rows'],\
                                                        1,length-1,\
                                                        title_name,style)
        self.sheets[sheet_name]['rows'] += 1
    #}}}
    #{{{add_image2
    def add_image2(self,bmp_name='',x='',y='',length='',title_name='ceshi',sheet_name='sheet'):
        if sheet_name not in self.sheets:
            # Create if does not exist
            self.create_sheet(sheet_name)
        tall_style = xlwt.easyxf('font:height 820;')
        self.sheets[sheet_name]['sheet'].row(self.sheets[sheet_name]['rows']).set_style(tall_style)
        self.sheets[sheet_name]['sheet'].insert_bitmap('logo.bmp',\
                                                       x,y,0,0,scale_x=0.50,\
                                                       scale_y=0.60)
        if length:
            style = xlwt.XFStyle() # Create Style
            font = xlwt.Font()
            font.bold = True
            font.height = 0x00FD
            style.font = font
            alignment = xlwt.Alignment() # Create Alignment
            alignment.horz = xlwt.Alignment.HORZ_CENTER 
            # May be: HORZ_GENERAL,HORZ_LEFT, HORZ_CENTER, HORZ_RIGHT, HORZ_FILLED, HORZ_JUSTIFIED,HORZ_CENTER_ACROSS_SEL, HORZ_DISTRIBUTED
            alignment.vert = xlwt.Alignment.VERT_CENTER 
            # May be: VERT_TOP,VERT_CENTER, VERT_BOTTOM, VERT_JUSTIFIED, VERT_DISTRIBUTED
            style.alignment = alignment # Add Alignment to Style
            self.sheets[sheet_name]['sheet'].write_merge(self.sheets[sheet_name]['rows'],self.sheets[sheet_name]['rows'],\
                                                        1,length-1,\
                                                        title_name,style)
        self.sheets[sheet_name]['rows'] += 1
    #}}}
    #{{{add_header
    def add_header(self,header_name,length,sheet_name='sheet'):
        if sheet_name not in self.sheets:
            # Create if does not exist
            self.create_sheet(sheet_name)
        style = xlwt.XFStyle() # Create Style
        font = xlwt.Font()
        font.bold = True
        font.height = 0x00FB
        style.font = font
        alignment = xlwt.Alignment() # Create Alignment
        alignment.horz = xlwt.Alignment.HORZ_CENTER 
        # May be: HORZ_GENERAL,HORZ_LEFT, HORZ_CENTER, HORZ_RIGHT, HORZ_FILLED, HORZ_JUSTIFIED,HORZ_CENTER_ACROSS_SEL, HORZ_DISTRIBUTED
        alignment.vert = xlwt.Alignment.VERT_CENTER 
        # May be: VERT_TOP,VERT_CENTER, VERT_BOTTOM, VERT_JUSTIFIED, VERT_DISTRIBUTED
        style.alignment = alignment # Add Alignment to Style
        self.sheets[sheet_name]['sheet'].write_merge(self.sheets[sheet_name]['rows'],self.sheets[sheet_name]['rows'],\
                                                    0,length-1,\
                                                    header_name,style)
        self.sheets[sheet_name]['rows'] += 1
    #}}}
    #{{{add_remark
    def add_remark(self,remark_name,length,sheet_name='sheet'):
        if sheet_name not in self.sheets:
            # Create if does not exist
            self.create_sheet(sheet_name)
        style = xlwt.XFStyle() # Create Style
        font = xlwt.Font()
        font.bold = False
        #font.height = 0x00EB
        font.height = 0x00FD
        style.font = font
        #style.alignment.wrap = xlwt.Alignment.WRAP_AT_RIGHT
        alignment = xlwt.Alignment() # Create Alignment
        alignment.horz = xlwt.Alignment.HORZ_LEFT
        # May be: HORZ_GENERAL,HORZ_LEFT, HORZ_CENTER, HORZ_RIGHT, HORZ_FILLED, HORZ_JUSTIFIED,HORZ_CENTER_ACROSS_SEL, HORZ_DISTRIBUTED
        alignment.vert = xlwt.Alignment.VERT_CENTER 
        # May be: VERT_TOP,VERT_CENTER, VERT_BOTTOM, VERT_JUSTIFIED, VERT_DISTRIBUTED
        alignment.wrap = xlwt.Alignment.WRAP_AT_RIGHT
        style.alignment = alignment # Add Alignment to Style
        self.sheets[sheet_name]['sheet'].write_merge(self.sheets[sheet_name]['rows'],self.sheets[sheet_name]['rows'],\
                                                    0,length-1,\
                                                    remark_name,style)
        tall_style = xlwt.easyxf('font:height 820;')
        self.sheets[sheet_name]['sheet'].row(self.sheets[sheet_name]['rows']).set_style(tall_style)
        self.sheets[sheet_name]['rows'] += 1
    #}}}
    #{{{write_title
    def write_title(self,sheet_name='sheet',border=False,pattern_n=0):
        style = xlwt.XFStyle()
        if border:
            borders = xlwt.Borders()
            borders.left = 1
            borders.right = 1
            borders.top = 1
            borders.bottom = 1
            borders.bottom_colour=0x3A    
         
            style.borders = borders 
        if pattern_n:
            pattern = xlwt.Pattern() # Create the Pattern
            pattern.pattern = xlwt.Pattern.SOLID_PATTERN 
            # May be: NO_PATTERN,SOLID_PATTERN, or 0x00 through 0x12
            pattern.pattern_fore_colour = pattern_n
            # May be: 8 through 63. 0 = Black, 1 = White, 2 = Red, 3 = Green, 4 = Blue, 
            # 5 = Yellow, 6 = Magenta, 7 = Cyan, 16 = Maroon, 17 = Dark Green, 18 = Dark Blue, 19 = Dark Yellow , 
            # almost brown), 20 = Dark Magenta, 21 = Teal, 22 = Light Gray, 23 = Dark Gray,
            alignment = xlwt.Alignment() # Create Alignment
            alignment.horz = xlwt.Alignment.HORZ_CENTER 
            # May be: HORZ_GENERAL,HORZ_LEFT, HORZ_CENTER, HORZ_RIGHT, HORZ_FILLED, HORZ_JUSTIFIED,HORZ_CENTER_ACROSS_SEL, HORZ_DISTRIBUTED
            alignment.vert = xlwt.Alignment.VERT_CENTER 
            # May be: VERT_TOP,VERT_CENTER, VERT_BOTTOM, VERT_JUSTIFIED, VERT_DISTRIBUTED
            style.alignment = alignment # Add Alignment to Style
            style.pattern = pattern # Add Pattern to Style
          
        #sheet.write(0, 0, 'Firstname',style)
        if sheet_name not in self.sheets:
            # Create if does not exist
            self.create_sheet(sheet_name)
    
        if self.sheets[sheet_name]['rows'] == 0:
            self.sheets[sheet_name]['header'] = row

        if self.sheets[sheet_name]['rows'] >= 65534:
            self.save()
            # create new sheet to avoid being greater than 65535 lines
            self.create_sheet(sheet_name)
            if self.sheets[sheet_name]['header']:
                self.writerow(self.sheets[sheet_name]['header'], sheet_name)
        if border:
            self.sheets[sheet_name]['sheet'].write_merge(self.sheets[sheet_name]['rows'],\
                                                         self.sheets[sheet_name]['rows']+1,\
                                                         0,\
                                                         0,\
                                                         u"序号",\
                                                         style)
            self.sheets[sheet_name]['sheet'].write_merge(self.sheets[sheet_name]['rows'],\
                                                         self.sheets[sheet_name]['rows']+1,\
                                                         1,\
                                                         1,\
                                                         u"摘要",\
                                                         style)
            self.sheets[sheet_name]['sheet'].write_merge(self.sheets[sheet_name]['rows'],\
                                                         self.sheets[sheet_name]['rows']+1,\
                                                         2,\
                                                         2,\
                                                         u"资源名称",\
                                                         style)
            self.sheets[sheet_name]['sheet'].write_merge(self.sheets[sheet_name]['rows'],\
                                                         self.sheets[sheet_name]['rows']+1,\
                                                         3,\
                                                         3,\
                                                         u"端口",\
                                                         style)
            self.sheets[sheet_name]['sheet'].write_merge(self.sheets[sheet_name]['rows'],\
                                                         self.sheets[sheet_name]['rows']+1,\
                                                         4,\
                                                         4,\
                                                         u"speed",\
                                                         style)
            ### 接收速率(Mbps)
            self.sheets[sheet_name]['sheet'].write_merge(self.sheets[sheet_name]['rows'],\
                                                         self.sheets[sheet_name]['rows'],\
                                                         5,\
                                                         7,\
                                                         u"接收速率(Mbps)",\
                                                         style)
            self.sheets[sheet_name]['sheet'].write(self.sheets[sheet_name]['rows']+1,\
                                                         5,\
                                                         u"最大值",\
                                                         style)
            self.sheets[sheet_name]['sheet'].write(self.sheets[sheet_name]['rows']+1,\
                                                         6,\
                                                         u"平均值",\
                                                         style)
            self.sheets[sheet_name]['sheet'].write(self.sheets[sheet_name]['rows']+1,\
                                                         7,\
                                                         u"最小值",\
                                                         style)
            ### 接收利用率(%)
            self.sheets[sheet_name]['sheet'].write_merge(self.sheets[sheet_name]['rows'],\
                                                         self.sheets[sheet_name]['rows'],\
                                                         8,\
                                                         10,\
                                                         u"接收利用率(%)",\
                                                         style)
            self.sheets[sheet_name]['sheet'].write(self.sheets[sheet_name]['rows']+1,\
                                                         8,\
                                                         u"最大值",\
                                                         style)
            self.sheets[sheet_name]['sheet'].write(self.sheets[sheet_name]['rows']+1,\
                                                         9,\
                                                         u"平均值",\
                                                         style)
            self.sheets[sheet_name]['sheet'].write(self.sheets[sheet_name]['rows']+1,\
                                                         10,\
                                                         u"最小值",\
                                                         style)
            ### 发送速率(Mbps)
            self.sheets[sheet_name]['sheet'].write_merge(self.sheets[sheet_name]['rows'],\
                                                         self.sheets[sheet_name]['rows'],\
                                                         11,\
                                                         13,\
                                                         u"发送速率(Mbps)",\
                                                         style)
            self.sheets[sheet_name]['sheet'].write(self.sheets[sheet_name]['rows']+1,\
                                                         11,\
                                                         u"最大值",\
                                                         style)
            self.sheets[sheet_name]['sheet'].write(self.sheets[sheet_name]['rows']+1,\
                                                         12,\
                                                         u"平均值",\
                                                         style)
            self.sheets[sheet_name]['sheet'].write(self.sheets[sheet_name]['rows']+1,\
                                                         13,\
                                                         u"最小值",\
                                                         style)
            ### 发送利用率(%)
            self.sheets[sheet_name]['sheet'].write_merge(self.sheets[sheet_name]['rows'],\
                                                         self.sheets[sheet_name]['rows'],\
                                                         14,\
                                                         16,\
                                                         u"发送利用率(%)",\
                                                         style)
            self.sheets[sheet_name]['sheet'].write(self.sheets[sheet_name]['rows']+1,\
                                                         14,\
                                                         u"最大值",\
                                                         style)
            self.sheets[sheet_name]['sheet'].write(self.sheets[sheet_name]['rows']+1,\
                                                         15,\
                                                         u"平均值",\
                                                         style)
            self.sheets[sheet_name]['sheet'].write(self.sheets[sheet_name]['rows']+1,\
                                                         16,\
                                                         u"最小值",\
                                                         style)
            ### 带宽利用率
            self.sheets[sheet_name]['sheet'].write_merge(self.sheets[sheet_name]['rows'],\
                                                         self.sheets[sheet_name]['rows']+1,\
                                                         17,\
                                                         17,\
                                                         u"带宽利用率(%)",\
                                                         style)
            #print self.sheets[sheet_name]['rows'],ci, self.cell(col) if type(col) != lib.xlwt.ExcelFormula.Formula else col
        self.sheets[sheet_name]['rows'] += 2
    #}}}
    #{{{create_sheet
    def create_sheet(self, sheet_name='sheet'):
        """Create new sheet
        """
        if sheet_name in self.sheets:
            sheet_index = self.sheets[sheet_name]['index'] + 1
        else:
            sheet_index = 0
            self.sheets[sheet_name] = {'header': []}
        self.sheets[sheet_name]['index'] = sheet_index
        self.sheets[sheet_name]['sheet'] = self.wbk.add_sheet('%s%s' % (sheet_name, sheet_index if sheet_index else ''), cell_overwrite_ok=True)
        self.sheets[sheet_name]['rows'] = 0
    #}}}
    #{{{cell
    def cell(self, s):
        if isinstance(s, basestring):
            if not isinstance(s, unicode):
                s = s.decode(self.encoding)
        elif s is None:
            s = ''
        else:
            s = str(s)
        return s
    #}}}
    #{{{setcol_width
    def setcol_width(self, row, sheet_name='sheet'):
        if sheet_name not in self.sheets:
            # Create if does not exist
            self.create_sheet(sheet_name)
    
        if self.sheets[sheet_name]['rows'] == 0:
            self.sheets[sheet_name]['header'] = row

        if self.sheets[sheet_name]['rows'] >= 65534:
            self.save()
            # create new sheet to avoid being greater than 65535 lines
            self.create_sheet(sheet_name)
            if self.sheets[sheet_name]['header']:
                self.writerow(self.sheets[sheet_name]['header'], sheet_name)
        for ci, width in enumerate(row):
            self.sheets[sheet_name]['sheet'].col(ci).width=256*width
    #}}}
    #{{{writerow
    def writerow(self, row, sheet_name='sheet',border=False,pattern_n=0):
        style = xlwt.XFStyle()
        if border:
            borders = xlwt.Borders()
            borders.left = 1
            borders.right = 1
            borders.top = 1
            borders.bottom = 1
            borders.bottom_colour=0x3A    
         
            style.borders = borders 
        if pattern_n:
            pattern = xlwt.Pattern() # Create the Pattern
            pattern.pattern = xlwt.Pattern.SOLID_PATTERN 
            # May be: NO_PATTERN,SOLID_PATTERN, or 0x00 through 0x12
            pattern.pattern_fore_colour = pattern_n
            # May be: 8 through 63. 0 = Black, 1 = White, 2 = Red, 3 = Green, 4 = Blue, 
            # 5 = Yellow, 6 = Magenta, 7 = Cyan, 16 = Maroon, 17 = Dark Green, 18 = Dark Blue, 19 = Dark Yellow , 
            # almost brown), 20 = Dark Magenta, 21 = Teal, 22 = Light Gray, 23 = Dark Gray,
            style.pattern = pattern # Add Pattern to Style
          
        #sheet.write(0, 0, 'Firstname',style)
        if sheet_name not in self.sheets:
            # Create if does not exist
            self.create_sheet(sheet_name)
    
        if self.sheets[sheet_name]['rows'] == 0:
            self.sheets[sheet_name]['header'] = row

        if self.sheets[sheet_name]['rows'] >= 65534:
            self.save()
            # create new sheet to avoid being greater than 65535 lines
            self.create_sheet(sheet_name)
            if self.sheets[sheet_name]['header']:
                self.writerow(self.sheets[sheet_name]['header'], sheet_name)
        for ci, col in enumerate(row):
            if border:
                self.sheets[sheet_name]['sheet'].write(self.sheets[sheet_name]['rows'],ci,\
                                                   self.cell(col) if type(col) != xlwt.ExcelFormula.Formula else col,\
                                                   style)
            else:
                self.sheets[sheet_name]['sheet'].write(self.sheets[sheet_name]['rows'],ci,\
                                                   self.cell(col) if type(col) != xlwt.ExcelFormula.Formula else col)
            #print self.sheets[sheet_name]['rows'],ci, self.cell(col) if type(col) != lib.xlwt.ExcelFormula.Formula else col
        self.sheets[sheet_name]['rows'] += 1
    #}}}
    #{{{writerows
    def writerows(self, rows, sheet_name='sheet'):
        for row in rows:
            self.writerow(row, sheet_name)
    #}}}
    #{{{save
    def save(self):
        self.wbk.save(self.file)
    #}}}
if __name__ == '__main__':
    # test
    xlswriter = XLSWriter('ceshi.xls')
    xlswriter.add_image("logo.bmg",0,0,4,title_name=u"测试",sheet_name=u"基本信息")
    xlswriter.add_header(u"信息登记表",4,sheet_name=u"基本信息")
    xlswriter.add_remark(u"信息登记表jkfdadaddddddddd\nddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",4,sheet_name=u"基本信息")
    xlswriter.setcol_width([20, 40],sheet_name=u'基本信息')

    xlswriter.write_title(sheet_name=u'基本信息',border=True,pattern_n=22)
    #xlswriter.writerow(['姓名','年龄','电话','QQ'],sheet_name=u'基本信息',border=True,pattern_n=22)
    xlswriter.writerow(['张三', '30', '12345678910', '123456789'], sheet_name=u'基本信息',border=True)
    xlswriter.writerow(['王五', '30', '13512345678', '123456789'],sheet_name=u'基本信息',border=True,pattern_n=2)
    
    xlswriter.writerow(['检测项', '检测命令', '值','基准','状态'],sheet_name=u'服务器器状态')
    xlswriter.writerow(["磁盘空间", "df -lP | grep -e '/$' | awk '{print $5}'","20%","%85","OK"], sheet_name=u'服务器器状态')
    # don't forget to save data to disk
    xlswriter.save()
    print 'finished.'
