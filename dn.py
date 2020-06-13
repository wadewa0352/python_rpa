import os
import sys
import pdfplumber

from collections import OrderedDict
from PyPDF2 import PdfFileReader

def getfiles():
    fls = []
    for d, sd, fl in os.walk('.'):
        for f in fl:
            fls.append(os.path.join(d, f))
    return list(filter(lambda f: '.pdf' in f, fls))

def readini(fname):
    lst = []
    with open(fname, 'r') as fh:  
        for l in fh:
            lst.append(l.rstrip(os.linesep))
    return lst

def getformfields(obj, tree=None, retval=None, fileobj=None):
    fieldAttributes = {
        '/FT': 'Field Type', 
        '/Parent': 'Parent', 
        '/T': 'Field Name', 
        '/TU': 'Alternate Field Name',
        '/TM': 'Mapping Name', 
        '/Ff': 'Field Flags', 
        '/V': 'Value', 
        '/DV': 'Default Value'
    }
    
    if retval is None:
        retval = OrderedDict()
        catalog = obj.trailer["/Root"]
        if "/AcroForm" in catalog:
            tree = catalog["/AcroForm"]
        else:
            return None
    if tree is None:
        return retval

    obj._checkKids(tree, retval, fileobj)
    for attr in fieldAttributes:
        if attr in tree:
            obj._buildField(tree, retval, fileobj, fieldAttributes)
            break

    if "/Fields" in tree:
        fields = tree["/Fields"]
        for f in fields:
            field = f.getObject()
            obj._buildField(field, retval, fileobj, fieldAttributes)

    return retval

def getfields(fn):
    pdf = None
    f = open(fn, 'rb')
    pdf = PdfFileReader(f)
    fields = getformfields(pdf)
    f.close()
    return OrderedDict((k, v.get('/V', '')) for k, v in fields.items())

def removeff(lst):
    r = []
    for l in lst:
        if not '|' in l:
            r.append(l)
    return r

def findtextfields(flds, l, nl):
    res = []
    for fld in flds:
        fieldn = fld.split('=')[0]
        fieldkw = fld.split('=')[1]
        words = l.split(' ')
        nwords = nl.split(' ')
        for i, w in enumerate(words):
            if fieldkw.lower() in w.lower():
                res.append(fieldn + '|' + nwords[i])
                break
    return res

def flatlst(lst):
    return [item for sl in lst for item in sl]

def dict(lst):
    dic = OrderedDict()
    items = flatlst(lst)
    for itm in items:
        k = itm.split('|')[0]
        v = itm.split('|')[1]
        dic[k] = v
    return dic

def gettextfields(kw, i1, i2, fn):
    res = []
    pdf = pdfplumber.open(fn)
    page = pdf.pages[0]
    pgtxt = page.extract_text()
    usei1 = False

    if kw.lower() in pgtxt.lower():
        usei1 = True
        txt = pgtxt.split('\n')
        flds = removeff(list(set(i1 + i2)))
        for i, l in enumerate(txt):
            if len(l) > 100:
                continue
            r = findtextfields(flds, l, txt[i+1])
            if len(r) > 0:
                res.append(r)
            if i == len(txt) - 2:
                break
            flt = flatlst(res)
            if len(flt) == len(flds):
                break
        pdf.close()

    return dict(res), usei1

def selectlist():
    return '''
    function selectedIdx(s, v) {
        for (var i = 0; i < s.options.length; i++) {
            if (s.options[i].text == v) {
            s.options[i].selected = true;
            return; 
            }
        }
    }
    '''

def createscript(usei1, i1, i2, fields, txtfields, fn):
    # todo...
    # the function selectlist must be called from here...
    jsScript = ""

    # add the function to handle working with select elements
    jsScript += selectlist()
    
    if usei1:
        for line in i1:
            jsScript += getFieldJavaScript(line, fields, txtfields)
    else:
        for line in i2:
            jsScript += getFieldJavaScript(line, fields, txtfields)

    return jsScript 

def getFieldJavaScript(line, fields, txtfields):
    if line.__contains__("="):
        lineParts = line.split("=")
        fieldName = lineParts[0]
        value = txtfields[fieldName]

        return f"document.getElementById('{fieldName}').value = '{value}';\r\n"
    elif line.__contains__("|"):
        lineParts = line.split("|")
        fieldName = lineParts[0]
        fieldType = lineParts[1]
        value = fields[fieldName]

        if fieldType == "e":
            return f"document.getElementById('{fieldName}').value = '{value}';\r\n"
        else:
            return f"selectedIdx(document.getElementById('{fieldName}'), '{value}');\r\n"  

    # If we got here, assume a bad line and just return an empty string
    return ""                 

def execute():
    try: 
        i1 = readini('i1.ini')
        i2 = readini('i2.ini')
        files = getfiles()
        for fn in files:
            fields = getfields(fn)            
            txtfields, usei1 = gettextfields('ALBARAN Nº', i1, i2, fn)

            fileNameWithExtension = os.path.basename(fn)
            fileName = fileNameWithExtension.split(".")[0]
            script_file = open(f"{fileName}.txt", "w")
            script_file.write(createscript(usei1, i1, i2, fields, txtfields, fn))
            script_file.close()

    except BaseException as msg:
        print('Error occured: ' + str(msg))

if __name__ == '__main__':
    execute()
