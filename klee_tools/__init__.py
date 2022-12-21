import struct
import logging

from .ktest import KTest
from .repack import KTestRepack

VERSION_NO = 3

def parse_ktest_file(f):
    """ Parses a klee file and returns a KTestObject

    Args:
        path (str): path to file

    Returns:
        KTest: KTest Object for the file
    """
    if isinstance(f, str):
        try:
            f = open(f, 'rb')
        except IOError:
            print('ERROR: file %s not found' % f)
            return None
    else:
        f.seek(0)

    hdr = f.read(5)
    if len(hdr) != 5 or (hdr != b'KTEST' and hdr != b'BOUT\n'):
        logging.critical('unrecognized file')
        return None
    version, = struct.unpack('>i', f.read(4))
    if version > VERSION_NO:
        logging.critical('unrecognized version')
        return None
    numArgs, = struct.unpack('>i', f.read(4))
    args = []
    for i in range(numArgs):
        size, = struct.unpack('>i', f.read(4))
        args.append(str(f.read(size).decode(encoding='ascii')))

    if version >= 2:
        symArgvs, = struct.unpack('>i', f.read(4))
        symArgvLen, = struct.unpack('>i', f.read(4))
    else:
        symArgvs = 0
        symArgvLen = 0

    numObjects, = struct.unpack('>i', f.read(4))
    objects = []
    for i in range(numObjects):
        size, = struct.unpack('>i', f.read(4))
        name = f.read(size).decode('utf-8')
        size, = struct.unpack('>i', f.read(4))
        f_bytes = f.read(size)
        objects.append((name, f_bytes))

    # Create an instance
    ktest_object = KTest(version, f.name, args, symArgvs, symArgvLen, objects)
    return ktest_object

def write_ktest_file(f, ktest_object):
    """ Writes a KTest object to a file
    """
    header = b"KTEST"
    version = struct.pack(">i", 2)
    numArgs = struct.pack(">i", 1)
    symArgvs = struct.pack(">i", 0)
    symArgvLen = struct.pack(">i", 0)

    f.write(header)
    # write the version
    f.write(version)
    # Num Args
    f.write(numArgs)
    # File name
    f.write(struct.pack(">i", len(ktest_object.path)))
    f.write(ktest_object.path.encode())
    # symArgs
    f.write(symArgvs)
    f.write(symArgvLen)
    # Object
    f.write(struct.pack(">i", len(ktest_object.objects)))
    for name, data in ktest_object.objects:
        # Name
        f.write(struct.pack(">i", len(name)))
        f.write(name.encode())
        f.write(struct.pack(">i", len(data)))
        f.write(data)
    
    # we are done
    f.close()

def create_ktest_from_grammar(grammar, output_fp):
    ktest_obj = KTestRepack(grammar.split("\n"))
    ktest_obj.write_to_file(output_fp)