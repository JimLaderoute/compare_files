import threading, os, re
from time import sleep

#
# given two root directories
# root1, root2
#
# find all the files under root1 that match a filter (like .jpg, .png, etc...) we don't want to compare hidden files
# do the same for root2; store them in a table
#
# each file class will contain the path, filename, filesize, modified-date
#
# now compare the files (we are using a hashtable so comparisons should be quick)
# 
F_SAMENAME=1
F_SAMESIZE=2
MAXSEARCH=0  # setting this to 0 means look at all files; you can limit it for testing by setting it to some number
knownExtensions = ['.jpg', '.png', '.dng', '.bmp', '.mp4', '.mov', '.psd', '.gif']
ignorePatterns = ['AlbumArt_']

class FileElem ():
    def __init__(self, _path, _filename):
        self.path = _path
        self.filename = _filename
        self.filesize = os.stat( _path + '\\' + _filename).st_size
        # print('{} size is {}'.format(_filename, self.filesize))
        self.modifiedDate = ''
        self.flags = 0
    def flagsString(self):
        # return a list of names based on the flags
        retstring = []
        if self.flags == F_SAMENAME:
            retstring.append("SameName")
        return retstring

    def compare(self,file2):
        if self.path == file2.path and self.filename == file2.filename:
            # we are comparing the exact two files.. .skip
            return
        if self.filename == file2.filename:
            self.flags |= F_SAMENAME
            file2.flags |= F_SAMENAME
            if self.filesize == file2.filesize:
                self.flags |= F_SAMESIZE
                file2.flags |= F_SAMESIZE

def hasExtension(fname, extensions):
    name, ext = os.path.splitext(fname)
    for knownext in extensions:
        if knownext.lower() == ext.lower():
            return True
    return False

def ignoreThis(fname, ignorePatterns):
    for p in ignorePatterns:
        if re.match(p, fname, re.I):
            return True
    return False

def gatherAllFiles( rootFolder, resultValue ):
    gathered = []
    searchCount=0
    for r,dirs, files in os.walk(rootFolder):
        if MAXSEARCH>0 and searchCount > MAXSEARCH:
            break
        for fname in files:
            #filePath = os.path.join(r,fname)
            if hasExtension(fname, knownExtensions) and not ignoreThis(fname, ignorePatterns):
                afile = FileElem(r, fname)
                gathered.append( afile )
                searchCount += 1
    resultValue[0] = gathered;

def compareFileLists( root1list, root2list ):
    for f1 in root1list:
        for f2 in root2list:
            f1.compare(f2)

def showDuplicates(rootlist, fid):
    for fo in rootlist:
        if fo.flags&F_SAMESIZE and fo.flags&F_SAMENAME:
            fid.write("%s\\%s\n" % (fo.path, fo.filename))

def showUnique(rootlist, fid):
    for fo in rootlist:
        if fo.flags == 0:
            fid.write("%s\\%s\n" % (fo.path, fo.filename))

def main():
    root1 = "G:\\backups\\scotty\\C__\\Users\\Kirk\\Pictures"
    root2 = "F:\\Pictures"
    result1 = [0]
    result2 = [0]
    print( "Root Folder 1: %s" % root1)
    print( "Root Folder 2: %s" % root2)
    x = threading.Thread(target=gatherAllFiles, args=(root2, result2))
    x.start()
    root1list = gatherAllFiles( root1, result1) # list of FileElem objects
    x.join()
    root1list = result1[0]
    root2list = result2[0]
    # root2list = gatherAllFiles( root2)
    compareFileLists(root1list, root2list)

    d1 = open('duplicates1.txt', 'w')
    showDuplicates(root1list, d1)
    d1.close()

    d2 = open('duplicates2.txt', 'w')
    showDuplicates(root2list, d2)
    d2.close()

    f1 = open('root1.txt', 'w')
    f2 = open('root2.txt', 'w')

    print("\n*****************\nThese files in %s are not in %s." % (root2, root1))
    showUnique(root2list, f2)
    print("\n*****************\nThese files in %s are not in %s." % (root1, root2))
    showUnique(root1list, f1)

    f1.close()
    f2.close()


if __name__ == "__main__":
    main()


