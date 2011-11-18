import pyPdf, re, urllib

# http://code.activestate.com/recipes/511465/

def getPDFContent(path):
    content = ""
    # Load PDF into pyPDF
    pdf = pyPdf.PdfFileReader(file(path, "rb"))
    for i in range(0, pdf.getNumPages()):
        # Extract text from page and add to content
        content += pdf.getPage(i).extractText() + "\n"
    # Collapse whitespace
    content = " ".join(content.replace(u"\xa0", " ").strip().split())
    return content

extractfull = getPDFContent("..\jcb.pdf").encode("ascii", "xmlcharrefreplace")

extractDOI = re.search('doi:\s?[a-zA-Z0-9\.]+/[a-zA-Z0-9\.]*[0-9]', extractfull.lower())
print extractDOI.group(0)

params = {
    'db':'pubmed',
    'tool':'PdfExtractDoi',
    'email':'i@cail.cn',
    'term':extractDOI.group(0),
    'usehistory':'y',
    'retmax':1
}
url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?' + urllib.urlencode(params)
print url
