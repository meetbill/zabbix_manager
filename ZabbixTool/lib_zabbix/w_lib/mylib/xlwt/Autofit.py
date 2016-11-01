# -*- coding: windows-1252 -*-

#-------------------------------------------------------------------------------
# Name:        Autofit
# Purpose:     Emulates the render-time function to 'Autofit Selection' the column width to the data it contains
#
# Author:      Warwick Prince  warwickp@mushroomsys.com
#
# Created:     30/01/12 9:15 AM
# Copyright:   (c) 2012 Mushroom Systems International Pty. Ltd.
# Licence:     You are free to use this code in any way you see fit - but you must retain this license message
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import xlwt.Formatting as Formatting
from xlwt.Worksheet import Worksheet

class TempWorkbook(object):
    """
    Used as a holder for some copies of critical dicts that we need to reverse key for our needs
    """

    def locateAFFont(self, font):
        """
        Using the Formatting.Font supplied, look up an appropriate AFFont (AutoFit Font) handler
        """

        fontName = 'AFFont%s' % font.name.replace(' ', '_')

        # Look in font cache
        if fontName not in self.fontCache:
            # Do we support this font?  If not, use the base handler
            cachedFont = globals().get(fontName, AFFont)

            # Add to cache
            self.fontCache[fontName] = cachedFont()

        return self.fontCache[fontName]

class AFFont(object):
    """
    Base Autofit Font class (Arial).  Extend this for each specific Font supported
    """

    # Gutter width to add on the end of the content - treat as "right hand padding'
    AUTOFIT_GUTTER = 255
    # Adjust this to factor the width against Arial.  i.e. 50 means that this font is half the width of Arial at the same font size
    # This is only used when the new font is a direct relationship to Arial. For others, a new AUTOFIT_CHAR_MAP is required - this can
    # be generated using CreateLearningSheet and GenerateAFFont.
    AUTOFIT_FONT_FACTOR = 100.00

    # Paste in the character mapping created by 'GenerateAFFont' here
    AUTOFIT_CHAR_MAP = {' ': [(134.6, 0.2724), (134.6, 0.2724)],
                        '!': [(134.6, 0.2724), (155.9, 0.2292)],
                        '"': [(164.4, 0.2114), (215.6, 0.2114)],
                        '#': [(249.8, 0.1872), (249.8, 0.1872)],
                        '$': [(249.8, 0.1872), (249.8, 0.1872)],
                        '%': [(394.8, 0.22), (394.8, 0.2284)],
                        '&': [(301.0, 0.2554), (322.3, 0.212)],
                        "'": [(96.2, 0.2554), (113.2, 0.1944)],
                        '(': [(155.9, 0.2292), (155.9, 0.2292)],
                        ')': [(155.9, 0.2292), (155.9, 0.2292)],
                        '*': [(181.5, 0.2548), (181.5, 0.2548)],
                        '+': [(266.8, 0.2882), (266.8, 0.2882)],
                        ',': [(134.6, 0.2724), (134.6, 0.2724)],
                        '-': [(155.9, 0.2292), (155.9, 0.2292)],
                        '.': [(134.6, 0.2724), (134.6, 0.2724)],
                        '/': [(134.6, 0.2724), (134.6, 0.2724)],
                        '0': [(249.8, 0.1872), (249.8, 0.1872)],
                        '1': [(224.2, 0.3066), (228.4, 0.2284)],
                        '2': [(249.8, 0.1872), (249.8, 0.1872)],
                        '3': [(249.8, 0.1872), (249.8, 0.1872)],
                        '4': [(249.8, 0.1872), (249.8, 0.1872)],
                        '5': [(249.8, 0.1872), (249.8, 0.1872)],
                        '6': [(249.8, 0.1872), (249.8, 0.1872)],
                        '7': [(249.8, 0.1872), (249.8, 0.1872)],
                        '8': [(249.8, 0.1872), (249.8, 0.1872)],
                        '9': [(249.8, 0.1872), (249.8, 0.1872)],
                        ':': [(134.6, 0.2724), (155.9, 0.2292)],
                        ';': [(134.6, 0.2724), (155.9, 0.2292)],
                        '<': [(266.8, 0.2882), (266.8, 0.2882)],
                        '=': [(266.8, 0.2882), (266.8, 0.2882)],
                        '>': [(266.8, 0.2882), (266.8, 0.2882)],
                        '?': [(249.8, 0.1872), (275.4, 0.2298)],
                        '@': [(450.3, 0.2462), (433.2, 0.254)],
                        'A': [(301.0, 0.2554), (322.3, 0.212)],
                        'B': [(301.0, 0.2554), (322.3, 0.212)],
                        'C': [(322.3, 0.212), (322.3, 0.212)],
                        'D': [(322.3, 0.212), (322.3, 0.212)],
                        'E': [(301.0, 0.2554), (301.0, 0.2554)],
                        'F': [(275.4, 0.2298), (275.4, 0.2298)],
                        'G': [(347.9, 0.2376), (347.9, 0.2376)],
                        'H': [(322.3, 0.212), (322.3, 0.212)],
                        'I': [(134.6, 0.2724), (134.6, 0.2724)],
                        'J': [(228.4, 0.2456), (249.8, 0.1872)],
                        'K': [(301.0, 0.2554), (322.3, 0.212)],
                        'L': [(249.8, 0.1872), (275.4, 0.2298)],
                        'M': [(369.2, 0.1944), (369.2, 0.1944)],
                        'N': [(322.3, 0.212), (322.3, 0.212)],
                        'O': [(347.9, 0.2376), (347.9, 0.2376)],
                        'P': [(301.0, 0.2554), (301.0, 0.2554)],
                        'Q': [(347.9, 0.2376), (347.9, 0.2376)],
                        'R': [(322.3, 0.212), (322.3, 0.212)],
                        'S': [(301.0, 0.2554), (301.0, 0.2554)],
                        'T': [(275.4, 0.2298), (275.4, 0.2212)],
                        'U': [(322.3, 0.212), (322.3, 0.212)],
                        'V': [(301.0, 0.2554), (301.0, 0.2554)],
                        'W': [(420.4, 0.254), (420.4, 0.2626)],
                        'X': [(296.7, 0.178), (301.0, 0.2554)],
                        'Y': [(301.0, 0.2554), (301.0, 0.2554)],
                        'Z': [(275.4, 0.2298), (275.4, 0.2298)],
                        'a': [(249.8, 0.1872), (249.8, 0.1872)],
                        'b': [(249.8, 0.1872), (275.4, 0.2298)],
                        'c': [(228.4, 0.2456), (249.8, 0.1872)],
                        'd': [(249.8, 0.1872), (275.4, 0.2298)],
                        'e': [(249.8, 0.1872), (249.8, 0.1872)],
                        'f': [(126.0, 0.254), (155.9, 0.2292)],
                        'g': [(249.8, 0.1872), (275.4, 0.2298)],
                        'h': [(249.8, 0.1872), (275.4, 0.2298)],
                        'i': [(109.0, 0.2384), (134.6, 0.2724)],
                        'j': [(109.0, 0.2384), (134.6, 0.2724)],
                        'k': [(228.4, 0.2456), (249.8, 0.1872)],
                        'l': [(109.0, 0.2384), (134.6, 0.2724)],
                        'm': [(373.5, 0.2804), (394.8, 0.22)],
                        'n': [(249.8, 0.1872), (275.4, 0.2298)],
                        'o': [(249.8, 0.1872), (275.4, 0.2298)],
                        'p': [(249.8, 0.1872), (275.4, 0.2298)],
                        'q': [(249.8, 0.1872), (275.4, 0.2298)],
                        'r': [(155.9, 0.2292), (181.5, 0.2548)],
                        's': [(228.4, 0.2456), (249.8, 0.1872)],
                        't': [(134.6, 0.2724), (155.9, 0.2292)],
                        'u': [(249.8, 0.1872), (275.4, 0.2298)],
                        'v': [(228.4, 0.237), (249.8, 0.1872)],
                        'w': [(322.3, 0.212), (347.9, 0.2376)],
                        'x': [(228.4, 0.237), (249.8, 0.1872)],
                        'y': [(228.4, 0.2456), (249.8, 0.1872)],
                        'z': [(228.4, 0.2456), (228.4, 0.2456)]}

    def measureText(self, text, xlwtFont):
        """
        Returns the best estimate at the actual width of the text supplied, given the font and size etc.
        """

        # How does it work?
        # Using the sample sheet of every supported char, measurements were taken of 10 chars and 100 char samples
        # in both normal and bolded text.  Then, various factors were calculated and stored in a character map for the
        # given font.  Excel has some strange rendering behaviour..  The width is not directly proportional to the number
        # of letters in a given string.  e.g. The width of 100 'A's is not equal to 10 x the width of 10 'A's. This makes things a
        # little more complicated.  I calculated a general "creep factor' which is the amount the apparent letter size
        # changes given the number of them there are in a string.  This is calculated by comparisons of 10 and 100 of the same
        # letter.  The creep factor is then included in the calc for each letter in the text being measured.  Not perfect, but
        # pretty damn close! :-)

        width = 0

        # Map to use the 0th or 1st element of the widths list, based on bold True or False bold attribute of font
        useWidth = {False:0, True:1}.get(xlwtFont.bold, 0)

        # Iterate over the text, looking up it's width and adjusting for it's position in the overall length (creep)
        for count, letter in enumerate(text):
            width10, creepFactor = self.AUTOFIT_CHAR_MAP.get(letter, self.AUTOFIT_CHAR_MAP['W'])[useWidth]
            widthThisLetter = width10 - (count * creepFactor)
            width += widthThisLetter

        # Factoring for "Arial" -> "MyFont" transforms
        width *= (self.AUTOFIT_FONT_FACTOR / 100.00)

        # Height adjustment factor is the base font size of 10 (stored as 200) So if it's 20 (400) its 400/200 times the size i.e. 2
        width *= (xlwtFont.height / 200.00)

        # Finally, add the gutter width on the end
        width += self.AUTOFIT_GUTTER

        return round(width, 0)

class AFFontArial(AFFont):
    """
    Specific support for Arial Font
    """

    # Note - All the values in the base font are set for Arial, so I don't need to do anything here.  Simply overload the values
    # that you need to change here
    pass

def Autofit(sheet, fromRowx=0, toRowx=-1, fromColx=0, toColx=-1, emptyCellsAreZero=True):

    """
    Performs a best-efforts auto fit on the column(s) and row(s) provided.

    emptyCellsAreZero tells the autofit logic to treat empty as 0 width.  Set to false to treat empty as default to standard column width

    Row and column ranges can be supplied, however, leaving them all as default will autofit the entire sheet.

    """

    assert isinstance(sheet, Worksheet), 'Sheet must be a Workbook.Worksheet instance!'

    # Set some defaults if open ranges supplied
    if toRowx == -1:
        toRowx = sheet.last_used_row
    if toColx == -1:
        toColx = sheet.last_used_col

    assert 0 <= fromColx <= sheet.last_used_col, 'FromColX out of bounds. 0 - %d' % sheet.last_used_col
    assert 0 <= toColx <= sheet.last_used_col, 'ToColX out of bounds. 0 - %d' % sheet.last_used_col
    assert 0 <= fromRowx <= sheet.last_used_row, 'FromRowX out of bounds. 0 - %d' % sheet.last_used_row
    assert 0 <= toRowx <= sheet.last_used_row, 'ToRowX out of bounds. 0 - %d' % sheet.last_used_row
    assert fromColx <= toColx, 'ToColx must be <= FromColx'
    assert fromRowx <= toRowx, 'ToRowx must be <= FromRowx'

    workBook = sheet._Worksheet__parent
    styles = workBook._Workbook__styles

    # As we need to search a number of dicts that are keyed in the *wrong way* for our needs, we will create copies here temporarily to
    # speed things up.  They are stored 'A':1 when I need to locate key 1 - so they are transformed to 1:'A'
    # Note: If this causes memory issues on very large sheets, then it could be changed to search on the original dicts - it would
    #       just be a LOT slower.

    tempWB = TempWorkbook()

    tempWB.styles = styles
    tempWB.style_xfByID = {value:key for key, value in styles._xf_id2x.items()}
    tempWB.style_fontsByID = {value:key for key, value in styles._font_id2x.items()}
    tempWB.str_indexesByID = {value:key for key, value in workBook._Workbook__sst._str_indexes.items()}
    tempWB.style_numberFormats = {value:key for key, value in styles._num_formats.items()}
    tempWB.sheet = sheet
    tempWB.fontCache = {'Arial':AFFontArial()}
    tempWB.emptyCellsAreZero = emptyCellsAreZero

    # For performance, I'm moving all the row objects in range into a specific selected rows list to iterate over,
    # as it's possibly done a number of times.
    rowRange = [sheet.rows[idx] for idx in xrange(fromRowx, toRowx+1)]

    for colx in xrange(fromColx, toColx+1):
        autofitWidth = 0
        # Loop over all the rows
        for row in rowRange:
            # Get the width of the cell
            cellWidth = GetCellWidth(tempWB, row, colx)

            if cellWidth > autofitWidth:
                autofitWidth = cellWidth

        # Set the column to the calculated width
        sheet.col(colx).width = autofitWidth

def GetCellWidth(workBook, row, colx):
    """
    By looking into the cell class type, we can determine how to get the original value of the cell back.  In the case of numbers, times
    and dates, we are forced to then format them as per the formatting settings..  We then pass that value to the font specific
    handler for estimating the width of the string value
    """

    try:
        # The cell may be out of bounds on this row
        cell = row._Row__cells[colx]
    except KeyError:
        # Return the default width of the column or zero
        if workBook.emptyCellsAreZero:
            return 0
        return workBook.sheet.col(colx).width

    cellClass = 'Handle%s' % cell.__class__.__name__

    Handler = globals().get(cellClass, HandleDefaultCell)

    return Handler(workBook, row, cell)

def HandleDefaultCell(workBook, row, cell):
    """
    Process general or string type cells, extracting the value from the central repository of all string values in the workbook.

    If the cell class does not support shared string array logic, then no processing can occur and a default width will be returned.
    """

    # Get the sheet main column record
    sheetCol = workBook.sheet.col(cell.colx)

    # Set the default answer to be the current column width
    width = sheetCol.width

    if not hasattr(cell, 'sst_idx'):
        # We can not work out what the width of this is - just return the columns width
        return width

    # Get the cell contents
    cellValue = workBook.str_indexesByID[cell.sst_idx]

    if cellValue:
        # Get the xf formatting index from either this cell this row, or the sheet column default
        if cell.xf_idx > 15:
            xf_idx = cell.xf_idx
        elif row._Row__xf_index > 15:
            xf_idx = row._Row__xf_index
        else:
            xf_idx = sheetCol._xf_idx

        # Look up the xf formatting record by index
        xf_rec = workBook.style_xfByID.get(xf_idx, None)
        # If we found our style, then get the font index from it
        if xf_rec:
            fontID = xf_rec[0]
            font = workBook.style_fontsByID.get(fontID, None)

            if font:
                # Get an Autofit Font manager from the cache
                fontManager = workBook.locateAFFont(font)
                # We have a font, so now use its details to process the text
                width = fontManager.measureText(cellValue, font)

    return width

def HandleStrCell(workBook, row, cell):
    """
    Will handle string like cell data using the default handler
    """

    return HandleDefaultCell(workBook, row, cell)

def HandleBlankCell(workBook, row, cell):
    """
    Will handle blank cells using the default handler
    """

    if workBook.emptyCellsAreZero:
        return 0

    return HandleDefaultCell(workBook, row, cell)

def HandleMulBlankCell(workBook, row, cell):
    """
    Will handle multi blank cells using the default handler
    """

    if workBook.emptyCellsAreZero:
        return 0

    return HandleDefaultCell(workBook, row, cell)

def HandleNumberCell(workBook, row, cell):
    """
    Will handle number like cells.  This is actually one of the hardest (date is the other) because of the various format options
    """

    # Get the sheet main column record
    sheetCol = workBook.sheet.col(cell.colx)

    # Default to the columns width
    width = sheetCol.width

    # Get the xf formatting index from either this cell this row, or the sheet column default

    if cell.xf_idx > 15:
        xf_idx = cell.xf_idx
    elif row._Row__xf_index > 15:
        xf_idx = row._Row__xf_index
    else:
        xf_idx = sheetCol._xf_index

    # Look up the xf formatting record by index
    xf_rec = workBook.style_xfByID.get(xf_idx, None)
    # If we found our style, then get the number format index from it

    if xf_rec:
        formatID = xf_rec[1]
        format = workBook.style_numberFormats.get(formatID, None)

        if format:
            # We have a format string, work out if possible the final format of our number as if rendered in Excel..
            if format == '0':
                cellValue = str(int(cell.number))
            elif format == '0.00':
                cellValue = '%0.2f' % cell.number
            elif format == '#,##0':
                cellValue = '{:,}'.format(int(cell.number))
            elif format == '#,##0.00':
                # I feel quite sure this can be done better than this..
                cellValue = '{,f}'.format(cell.number)
                cellValue = cellValue.split('.')
                cellValue[1] = cellValue[1][:2]
                cellValue = '.'.join(cellValue)
            elif format == '"$"#,##0_);("$"#,##' or format == '"$"#,##0_);[Red]("$"#,##':
                cellValue = '${:,}'.format(int(cell.number))
            elif format == '"$"#,##0.00_);("$"#,##' or format == '"$"#,##0.00_);[Red]("$"#,##':
                # I feel quite sure this can be done better than this..
                cellValue = '${,f}'.format(cell.number)
                cellValue = cellValue.split('.')
                cellValue[1] = cellValue[1][:2]
                cellValue = '.'.join(cellValue)
            elif format == '0%':
                cellValue = '%d%%' % int(cell.number)
            elif format == '0.00%':
                cellValue = '%0.2f%%' % cell.number
            elif format == '0.00E+00':
                cellValue = '%0.02E' % cell.number
            elif format == '# ?/?':
                cellValue = '9 9/9'
            elif format == '# ??/??':
                cellValue = '9 99/99'
            elif format == 'M/D/YY':
                cellValue = '99/99/99'
            elif format == 'D-MMM-YY':
                cellValue = '99-WWW-99'
            elif format == 'MMM-YY':
                cellValue = 'WWW-99'
            elif format == 'h:mm AM/PM':
                cellValue = '99:99 pm'
            elif format == 'h:mm:ss AM/PM':
                cellValue = '99:99:99 pm'
            elif format.lower() == 'h:mm':
                cellValue = '99:99'
            elif format.lower() == 'h:mm:ss':
                cellValue = '99:99:99'
            elif format == 'M/D/YY h:mm':
                cellValue = '99/99/99 99:99'
            elif format == '_(#,##0_);(#,##0)' or format == '_(#,##0_);[Red](#,##0)':
                if cell.number < 0.00:
                    cellValue = '({:,})'.format(-cell.number)
                else:
                    cellValue = '{:,}'.format(cell.number)
            elif format == '_(#,##0.00_);(#,##0.00)' or format == '_(#,##0.00_);[Red](#,##0.00)':
                if cell.number < 0.00:
                    cellValue = '${,f}'.format(-cell.number)
                    cellValue = cellValue.split('.')
                    cellValue[1] = cellValue[1][:2]
                    cellValue = '.'.join(cellValue)
                    cellValue = '(%s)' % cellValue
                else:
                    cellValue = '${,f}'.format(cell.number)
                    cellValue = cellValue.split('.')
                    cellValue[1] = cellValue[1][:2]
                    cellValue = '.'.join(cellValue)
            elif format == '_("$"* #,##0_);_("$"* (#,##0);_("$"* "-"_);_(@_)' or format == '_(* #,##0_);_(* (#,##0);_(* "-"_);_(@_)':
                if cell.number < 0.00:
                    cellValue = '(${:,})'.format(-cell.number)
                else:
                    cellValue = '${:,}'.format(cell.number)
            elif format == '_("$"* #,##0.00_);_("$"* (#,##0.00);_("$"* "-"??_);_(@_)' or format == '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)':
                if cell.number < 0.00:
                    cellValue = '${,f}'.format(-cell.number)
                    cellValue = cellValue.split('.')
                    cellValue[1] = cellValue[1][:2]
                    cellValue = '.'.join(cellValue)
                    cellValue = '(%s)' % cellValue
                else:
                    cellValue = '${,f}'.format(cell.number)
                    cellValue = cellValue.split('.')
                    cellValue[1] = cellValue[1][:2]
                    cellValue = '.'.join(cellValue)
            elif format == 'mm:ss':
                cellValue = '99:99'
            elif format == '[h]:mm:ss':
                cellValue = '99:99:99'
            elif format == 'mm:ss.0':
                cellValue = '99:99.9999999'
            elif format == '##0.0E+0':
                cellValue = '%03.1E' % cell.number
            elif format.lower() == 'general':
                # General/general
                cellValue = '%s' % cell.number
            elif format == 'DD/MM/YYYY' or format == 'MM/DD/YYYY' or format == 'DD-MM-YYYY' or format == 'MM-DD-YYYY':
                # Non standard yet common format
                cellValue = '99/99/9999'
            elif format == 'DD/MM/YY' or format == 'MM/DD/YY' or format == 'DD-MM-YY' or format == 'MM-DD-YY':
                # Non standard yet common format
                cellValue = '99/99/99'
            else:
                # Hmm, not a standard format, so just use the length of the format string itself.  Ideas anyone?
                cellValue = format

            # Minor adjustment just to make sure.
            cellValue += " "

            # See if we can locate the xlwt font now
            fontID = xf_rec[0]
            font = workBook.style_fontsByID.get(fontID, None)

            if font:
                # Get an Autofit Font manager from the cache
                fontManager = workBook.locateAFFont(font)
                # We have a font, so now use its details to process the text
                width = fontManager.measureText(cellValue, font)

    return width
