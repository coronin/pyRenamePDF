import re

input = "asdf ddd.rm.docy.jpeg.gz"

knownFileList = ['\.dmg$','\.iso$','\.toast$','\.bz2$','\.tar$','\.t?gz$','\.pkg$','\.mov$','\.avi$','\.rm(vb)?$','\.kmv$','\.mp4$','\.mp3$','\.zip$','\.rar$','\.exe$','\.docx?$','\.xlsx?$','\.pptx?$','\.jpe?g$','\.gif$','\.png$','\.ps$','\.ai$','\.eps$']
knownFileCheck = 1
for knownFile in knownFileList :
    if re.search(knownFile,input.lower()) :
        knownFileCheck = knownFileCheck * 0
        break
if not knownFileCheck :
    print 'known not PDF format, skip'
    # continue    
