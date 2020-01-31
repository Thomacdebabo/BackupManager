import os

class CTError(Exception):
    def __init__(self, errors):
        self.errors = errors

try:
    O_BINARY = os.O_BINARY
except:
    O_BINARY = 0
READ_FLAGS = os.O_RDONLY | O_BINARY
WRITE_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | O_BINARY
BUFFER_SIZE = 128*1024

def copyfile(src, dst):
    try:
        fin = os.open(src, READ_FLAGS)
        stat = os.fstat(fin)
        fout = os.open(dst, WRITE_FLAGS, stat.st_mode)
        for x in iter(lambda: os.read(fin, BUFFER_SIZE), ""):
            os.write(fout, x)
    finally:
        try: os.close(fin)
        except: pass
        try: os.close(fout)
        except: pass

def copytree(src, dst, dsti, symlinks=False, ignore=[]):
    names = os.listdir(src)
    #ignore = Openignorelist(dsti)

    if not os.path.exists(dst):
        os.makedirs(dst)
    errors = []
    for name in names:
        if name in ignore:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                copyfile(srcname, dstname)
            # XXX What about devices, sockets etc.?
        except (IOError, os.error):
            errors.append((srcname, dstname))
        except (CTError):
            ignore

    if errors:
        raise CTError(errors)
    #AlreadyCopied(names, dsti)

def AlreadyCopied(names, dst):
    f = open(dst+"//ignorelist.txt", 'w')
    for name in names:
        f.write("%s\n" % name)
    f.close()
def Openignorelist(dst):
    ignore = []
    try:
        f = open(dst + "//ignorelist.txt", 'w')
        for line in f.readlines():
            ignore.append(line)
        f.close()
    except: print("didnt find ignorelist.txt")
    return ignore
