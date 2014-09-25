import os, os.path, shutil, re, glob
import pyPdf

# inspired from pyPdf/pdf.py line 607
def readNextEndLine(stream):
    line = ""
    while True:
        x = stream.read(1)
        stream.seek(-2, 1)
        if x == '\n' or x == '\r':
            while x == '\n' or x == '\r':
                x = stream.read(1)
                stream.seek(-2, 1)
            stream.seek(1, 1)
            break
        else:
            line = x + line
    return line

# http://www.velocityreviews.com/forums/t320964-p2-determine-file-type-binary-or-text.html
def is_binary(buff):
    """Return true if the given filename is binary"""
    non_text = 0
    all_text = 0
    for i in range(len(buff)):
        a = ord(buff[i])
        all_text = all_text + 1
        if (a < 8) or (a > 13 and a < 32) or (a > 126):
            non_text = non_text + 1
        if all_text == 4096:
            break
    print non_text, all_text
    if non_text > all_text * 0.01:
        return 1
    else:
        return 0


for input in glob.glob(os.path.join('./','*')):
    if os.path.isdir(input):
        continue
    print input, "1"

    # doc = pyPdf.PdfFileReader(file(input, "rb"))

    ffile = open(input, 'rb')
    if is_binary(ffile.read()):
        ffile.seek(-1, 2)
        line = ''
        while not line:
            line = readNextEndLine(ffile)
        if line[:5] != '%%EOF':
            # print "pyPdf EOF marker not found"
            continue

    print input, "2"


