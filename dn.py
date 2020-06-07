import os
import sys
import pdfplumber

from collections import OrderedDict
from PyPDF2 import PdfFileReader

def getfiles(filePath):
    pdfFilesToProcess = []
    
    for root,directoryNames, fileNames in os.walk(filePath):        
        for fileName in fileNames:
            if fileName.endswith('.pdf'):
                pdfFilesToProcess.append(root + "\\" + fileName)

    return pdfFilesToProcess

def readini(fname):
    # Instruction(s) to read an .ini file go here (and/or below)...
    return

def getformfields(obj, tree=None, retval=None, fileobj=None):
    """
    Extracts field data if this PDF contains interactive form fields.
    The *tree* and *retval* parameters are for recursive use.

    :param fileobj: A file object (usually a text file) to write
        a report to on all interactive form fields found.
    :return: A dictionary where each key is a field name, and each
        value is a :class:`Field<PyPDF2.generic.Field>` object. By
        default, the mapping name is used for keys.
    :rtype: dict, or ``None`` if form data could not be located.
    """
    fieldAttributes = { '/FT': 'Field Type', '/Parent': 'Parent', '/T': 'Field Name', '/TU': 'Alternate Field Name', '/TM': 'Mapping Name', '/Ff': 'Field Flags', '/V': 'Value', '/DV': 'Default Value' }
    
    if retval is None:
        retval = OrderedDict()
        catalog = obj.trailer["/Root"]
        # get the AcroForm tree
        if "/AcroForm" in catalog:
            tree = catalog["/AcroForm"]
        else:
            return None
    if tree is None:
        return retval

    obj._checkKids(tree, retval, fileobj)
    for attr in fieldAttributes:
        if attr in tree:
            # Tree is a field
            obj._buildField(tree, retval, fileobj, fieldAttributes)
            break

    if "/Fields" in tree:
        fields = tree["/Fields"]
        for f in fields:
            field = f.getObject()
            obj._buildField(field, retval, fileobj, fieldAttributes)

    return retval

def getfields(fn):
    infile = PdfFileReader(open(fn, 'rb'))
    fields = getformfields(infile)
    return OrderedDict((k, v.get('/V', '')) for k, v in fields.items())
    

def gettextfields(i1, i2, fn):
    # Instruction(s) to get the text fields goes here...
    return

def execute():

    resultsDict = {}

    try: 
        i1 = readini('l1.ini') # Read the 1st .ini file
        i2 = readini('l2.ini') # Read the 2nd .ini file
        # Read fields for each file (instructions are missing here)
        # Both getfields and gettextfields should be invoked
        pdfsToProces = getfiles("C:\\Projects\\python_rpa\\formats")

        for pdf in pdfsToProces:
            resultsDict[pdf] = getfields(pdf)
            
        print(resultsDict)

    except BaseException as msg:
        print('Error occured: ' + str(msg))

    
if __name__ == '__main__':
    execute()