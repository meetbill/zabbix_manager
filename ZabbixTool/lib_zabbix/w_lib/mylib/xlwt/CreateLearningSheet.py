#-------------------------------------------------------------------------------
# Name:        CreateLearningSheet
# Purpose:     Creates an Excel sheet of sample data.  This is then "Autofitted" using the real Excel function
#              and then read back in and processed to work out the character mappings to be used later.
#
# Author:      Warwick Prince  Mushroom Systems International Pty. Ltd.
#
# Created:     3/02/12 11:56 AM
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import xlwt
import sys

def ExportSampleSheet():
    """
    Create a sample sheet format and save it to the file supplied.  The user then must select all the sheets and using Excel,
    Autofit them and save the workbook.  Then, use GenerateAFFont to read the Excel formatted sheet back in and learn from it.
    """

    if len(sys.argv) != 2:
        print 'Usage: CreateLearningSheet [SampleSheet.xls]'
        sys.exit()

    # Get the workbook file name from the command line
    fileName = sys.argv[1]

    if not fileName.lower().endswith('.xls'):
        fileName = '%s.xls' % fileName

    xlWorkbook = xlwt.Workbook()

    s1 = xlWorkbook.add_sheet('Normal Sample UPPER')
    s2 = xlWorkbook.add_sheet('Normal Sample Lower')
    s3 = xlWorkbook.add_sheet('Normal Sample Other')
    s4 = xlWorkbook.add_sheet('Bold Sample UPPER')
    s5 = xlWorkbook.add_sheet('Bold Sample Lower')
    s6 = xlWorkbook.add_sheet('Bold Sample Other')

    # Normal UPPER
    for row in xrange(0, 2):
        letterValue = 65
        for col in range(0, 51, 2):
            letter = chr(letterValue)
            s1.write(row, col, letter*10)
            s1.write(row, col+1, letter*100)
            letterValue += 1

    # Normal lower
    for row in xrange(0, 2):
        letterValue = 97
        for col in range(0, 51, 2):
            letter = chr(letterValue)
            s2.write(row, col, letter*10)
            s2.write(row, col+1, letter*100)
            letterValue += 1

    # Normal Other
    for row in xrange(0, 2):
        letterValue = 32
        for col in range(0, 66, 2):
            letter = chr(letterValue)
            s3.write(row, col, letter*10)
            s3.write(row, col+1, letter*100)
            letterValue += 1

    style = xlwt.Style.XFStyle()
    style.font.bold = True

    # Bold UPPER
    for row in xrange(0, 2):
        letterValue = 65
        for col in range(0, 51, 2):
            letter = chr(letterValue)
            s4.write(row, col, letter*10, style)
            s4.write(row, col+1, letter*100, style)
            letterValue += 1

    # Bold lower
    for row in xrange(0, 2):
        letterValue = 97
        for col in range(0, 51, 2):
            letter = chr(letterValue)
            s5.write(row, col, letter*10, style)
            s5.write(row, col+1, letter*100, style)
            letterValue += 1

    # Bold Other
    for row in xrange(0, 2):
        letterValue = 32
        for col in range(0, 66, 2):
            letter = chr(letterValue)
            s6.write(row, col, letter*10, style)
            s6.write(row, col+1, letter*100, style)
            letterValue += 1

    try:
        xlWorkbook.save(fileName)
    except IOError:
        print 'Failed to save filename "%s"' % fileName

if __name__ == '__main__':
    ExportSampleSheet()
