#!/usr/bin/env python

# Rename all PDF files in the folder, basded on DOI info ; v0.13
# (c) Liang Cai, 2014
# http://about.me/cail


import os, os.path, shutil, re, unicodedata, PyPDF2
from time import gmtime, strftime, sleep

# change the following to False if you want to copy renamed files
moveMode = True

# inspired by pythonquery.py
# Simple script to query pubmed for a DOI
# (c) Simon Greenhill, 2007
# http://simon.net.nz/
import urllib
from xml.dom import minidom

# http://www.istihza.com/makale_pypdf.html
import warnings
warnings.simplefilter("ignore", DeprecationWarning)


# inspired by pyPdf/pdf.py line 607
def readNextEndLine(stream):
    line = ''
    while True:
        x = stream.read(1)
        stream.seek(-2, 1)
        if x == '\n' or x == '\r' :
            while x == '\n' or x == '\r' :
                x = stream.read(1)
                stream.seek(-2, 1)
            stream.seek(1, 1)
            break
        else:
            line = x + line
    return line


# inspired by http://www.velocityreviews.com/forums/t320964-p2-determine-file-type-binary-or-text.html
def is_binary(buff):
    """Return true if the given filename is binary"""
    non_text = 0
    all_text = 0
    for i in range(len(buff)):
        a = ord(buff[i])
        all_text = all_text + 1
        if (a < 8) or (a > 13 and a < 32) or (a > 126) :
            non_text = non_text + 1
        if all_text == 4096 :
            break
    # print non_text, all_text # enable for debug
    if non_text > all_text * 0.0009 : # 0.0009 is very arbitrary
        return 1
    else:
        return 0


# inspired by http://code.activestate.com/recipes/511465/
def getPDFContent(path):
    content = ''
    # Load PDF into pyPDF
    fileStream = file(path, 'rb')
    pdf = PyPDF2.PdfFileReader(fileStream)
    for i in range(0, pdf.getNumPages()):
        # Extract text from page and add to content
        content += pdf.getPage(i).extractText() + ' '
    # close the stream, required for windows
    fileStream.close()
    # Collapse whitespace
    content = ' '.join(content.replace(u'\xa0', ' ').strip().split())
    return content


def get_citation_from_doi(query, email='i@cail.cn', tool='pyRenamePdf.py', database='pubmed'):
    params = {
        'db':database,
        'tool':tool,
        'email':email,
        'term':query,
        'usehistory':'y',
        'retmax':1
    }
# try to resolve the PubMed ID of the DOI
    url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?' + urllib.urlencode(params)
    # print url # enable for debug
    data = urllib.urlopen(url).read()

# parse XML output from PubMed...
    xmldoc = minidom.parseString(data)
    ids = xmldoc.getElementsByTagName('Id')

# nothing found, exit
    if len(ids) == 0 :
        raise Exception, 'DoiNotFound'

# get ID
    id = ids[0].childNodes[0].data

# remove unwanted parameters
    params.pop('term')
    params.pop('usehistory')
    params.pop('retmax')
# and add new ones...
    params['id'] = id

    params['retmode'] = 'xml'

# get citation info:
    url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?' + urllib.urlencode(params)
    # print url # enable for debug
    data = urllib.urlopen(url).read()

    return data


def text_output(xml):
    """Makes a simple text output from the XML returned from efetch"""

    xmldoc = minidom.parseString(xml)

    title = xmldoc.getElementsByTagName('ArticleTitle')[0]
    title = title.childNodes[0].data[:-1].encode('ascii','ignore')
    LOGFILE.writelines(title + '\r\n')

    authors = xmldoc.getElementsByTagName('AuthorList')[0]
    authors = authors.getElementsByTagName('Author')
    authorlist = []

    for author in authors:
        # inspired http://www.peterbe.com/plog/unicode-to-ascii
        try:
            LastName = author.getElementsByTagName('LastName')[0].childNodes[0].data.encode('ascii','ignore')
            try:
                Initials = author.getElementsByTagName('Initials')[0].childNodes[0].data.encode('ascii','ignore')
            except:
                Initials = ''
            authorLong = '%s %s' % (LastName, Initials)
            author = LastName
        except:
            authorLong = author.getElementsByTagName('CollectiveName')[0].childNodes[0].data.encode('ascii','ignore')
            author = authorLong
        authorlist.append(authorLong)
    LOGFILE.writelines(', '.join(authorlist) + '\r\n')

    journalinfo = xmldoc.getElementsByTagName('Journal')[0]
    if journalinfo.getElementsByTagName('ISOAbbreviation') :
        journal = journalinfo.getElementsByTagName('ISOAbbreviation')[0].childNodes[0].data
    else:
        journal = journalinfo.getElementsByTagName('Title')[0].childNodes[0].data

    journalinfo = journalinfo.getElementsByTagName('JournalIssue')[0]
    try:
        year = journalinfo.getElementsByTagName('Year')[0].childNodes[0].data
    except:
        year = journalinfo.getElementsByTagName('MedlineDate')[0].childNodes[0].data.replace(' ','')
    try:
        month = journalinfo.getElementsByTagName('Month')[0].childNodes[0].data
    except:
        month = 'na'
    LOGFILE.writelines('%s %s, %s\r\n' % (year, month, journal))

    if xmldoc.getElementsByTagName('AbstractText') :
        abstract = xmldoc.getElementsByTagName('AbstractText')[0]
        abstract = abstract.childNodes[0].data.encode('ascii','ignore')
        LOGFILE.writelines(abstract + '\r\n')

    pmid = xmldoc.getElementsByTagName('PMID')[0]
    pmid = pmid.childNodes[0].data[:-1]
    LOGFILE.writelines('PMID:' + pmid + '\r\n')

    print title
    print authorlist[0], ',', authorlist[-1]
    print journal, year
    print ''

    # output = author.replace(' ','') + '_' + journal.replace('.','').replace(' ','') + '-' + year + '_' + title[:140].replace(' ','-').replace('/','')
    if len(authors) > 1 :
        try:
            output = author.replace(' ','') + '_' + authors[0].getElementsByTagName('LastName')[0].childNodes[0].data.encode('ascii','ignore').replace(' ','') + '-' + journal.replace('.','').replace(' ','') + '_' + year
        except:
            output = author.replace(' ','') + '_' + authors[0].getElementsByTagName('CollectiveName')[0].childNodes[0].data.encode('ascii','ignore').replace(' ','') + '-' + journal.replace('.','').replace(' ','') + '_' + year
    else:
        output = author.replace(' ','') + '-' + journal.replace('.','').replace(' ','') + '_' + year

    return output


def replace_all(text, dic):
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text


if __name__ == '__main__' :
    from sys import argv, exit
if len(argv) == 1 :
    print 'Usage: %s <folder>' % argv[0]
    print '  e.g. %s ./' % argv[0]
    exit()

if os.path.exists(os.path.join(argv[1],'renamed/')) == 0 :
    os.mkdir(os.path.join(argv[1],'renamed/'))
if os.path.exists(os.path.join(argv[1],'untouched/')) == 0 :
    os.mkdir(os.path.join(argv[1],'untouched/'))

today = strftime('%d%b%Y', gmtime())
LOGFILE = open(os.path.join(argv[1],'log-' + today + '.txt'), 'ab')
FileCounter = 0

for fileindir in os.listdir(argv[1]) :
    file_name = os.path.join(argv[1], fileindir)
    # print file_name # enable for debug

    if os.path.isdir(file_name) :
        continue

    knownFileList = ['\.dmg$','\.bin$','\.cue$','\.iso$','\.toast$','\.bz2$','\.tar$','\.t?gz$','\.pkg$','\.mov$','\.avi$','\.rm(vb)?$','\.kmv$','\.mp4$','\.mp3$','\.zip$','\.rar$','\.exe$','\.docx?$','\.xlsx?$','\.pptx?$','\.jpe?g$','\.gif$','\.png$','\.ps$','\.ai$','\.eps$','\.xpi$','\.qt$','\.tiff?$','\.torrent$']
    knownFileCheck = 1
    for knownFile in knownFileList :
        if re.search(knownFile, file_name.lower()) :
            knownFileCheck = knownFileCheck * 0
            break
    if not knownFileCheck :
        print '  skip a known non-PDF file'
        continue

    FileCounter = FileCounter + 1

    testfile = open(file_name, 'rb')
    if is_binary(testfile.read()) :
        testfile.seek(-1, 2)
        line = ''
        while not line:
            line = readNextEndLine(testfile)
        if line[:5] != '%%EOF' :
            # print '  PyPDF2 EOF marker not found'
            continue
    else:
        # print '  not a binary file'
        continue
    testfile.close()
    print file_name

    try:
        extractfull = getPDFContent(file_name).encode('ascii', 'xmlcharrefreplace')
        # print extractfull[:6999] # enable for debug
    except:
        print '  PyPDF2 Error'
        newFilename = os.path.join(argv[1], 'untouched/', fileindir)
        if moveMode :
            shutil.move(file_name, '%s' % newFilename)
        else:
            shutil.copy2(file_name, '%s' % newFilename)
        continue # break

    extractDOI = re.search('(?<=doi)/?:?\s?\d{2}\.\d{4}/\S*[0-9]', extractfull.lower().replace('&#338;','-').replace('&#169;','')) # @@@@ \d{2}\.\d{4}/\S*[0-9a-zA-Z]
    if not extractDOI :
        extractDOI = re.search('(?<=http://dx.doi.org/)\d{2}\.\d{4}/\S*[0-9]', extractfull.lower())
    if not extractDOI :
        extractDOI = re.search('(?<=doi).?10.1073/pnas\.\d+', extractfull.lower().replace('pnas','/pnas')) # PNAS fix
    if not extractDOI :
        extractDOI = re.search('10\.1083/jcb\.\d{9}', extractfull.lower()) # JCB fix
    # print extractDOI # enable for debug

    if extractDOI :
        cleanDOI = extractDOI.group(0).replace(':','').replace(' ','')
        if cleanDOI.startswith('/'):
            cleanDOI = cleanDOI[1:]

        if cleanDOI.startswith('10.1096'): # FABSE J fix
            cleanDOI = cleanDOI[:20]
        if cleanDOI.startswith('10.1083'): # JCB second fix
            cleanDOI = cleanDOI[:21]
        if cleanDOI.startswith('10.1038') and cleanDOI.endswith('nature'): # Nature series fix
            cleanDOI = cleanDOI[:-6]


        if len(cleanDOI) > 40 :
            cleanDOItemp = re.sub(r'\d\.\d', '000', cleanDOI)
            reps = {'.':'A', '-':'0'}
            cleanDOItemp = replace_all(cleanDOItemp[8:], reps)
            digitStart = 0
            for i in range(len(cleanDOItemp)) :
                if cleanDOItemp[i].isdigit() :
                    digitStart = 1
                if cleanDOItemp[i].isalpha() and digitStart :
                    break
            cleanDOI = cleanDOI[0:(8+i)]

    else:
        print '  fail to extract DOI'
        newFilename = os.path.join(argv[1], 'untouched/', fileindir)
        if moveMode:
            shutil.move(file_name, '%s' % newFilename)
        else:
            shutil.copy2(file_name, '%s' % newFilename)
        continue # break

    print cleanDOI
    LOGFILE.writelines('dox:' + cleanDOI + '\r\n')

    getDOI = 1
    trimCycle = 0
    while getDOI and trimCycle < 5:
        getDOI = 0
        try:
            citation = get_citation_from_doi(cleanDOI)
        except:
            getDOI = 1
            trimCycle = trimCycle + 1
            cleanDOI = cleanDOI[0:-1] # most nature articles
            sleep(2)
    if trimCycle > 4 :
        print '  fail to confirm DOI'
        newFilename = os.path.join(argv[1], 'untouched/', fileindir)
        if moveMode:
            shutil.move(file_name, '%s' % newFilename)
        else:
            shutil.copy2(file_name, '%s' % newFilename)
        continue # break

    while not citation :
        print '  No internet? will try in 10 seconds'
        sleep(10)
        citation = get_citation_from_doi(cleanDOI)

    try:
        doi_data = text_output(citation)
    except:
        print '  ignore due to missing DOI info'
        continue

    newFilename = os.path.join(argv[1], 'renamed/', '%s.pdf' % doi_data)
    if os.path.isfile(newFilename) :
        if moveMode :
            shutil.move(file_name, os.path.join(argv[1], 'renamed/', '%s_%s.pdf' % (doi_data, FileCounter)))
        else:
            shutil.copy2(file_name, os.path.join(argv[1], 'renamed/', '%s_%s.pdf' % (doi_data, FileCounter)))
    else:
        if moveMode :
            shutil.move(file_name, '%s' % newFilename)
        else:
            shutil.copy2(file_name, '%s' % newFilename)

    LOGFILE.writelines('\r\n\r\n')
