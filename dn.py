import os
import sys

def getfiles(filePath):
    pdfFilesToProcess = []
    
    for root,directoryNames, fileNames in os.walk(filePath):        
        for fileName in fileNames:
            if fileName.endswith('.pdf'):
                pdfFilesToProcess.append(root + "\\" + fileName)

    return pdfFilesToProcess
    
print(getfiles("C:\\Projects\\python_rpa\\formats"))
