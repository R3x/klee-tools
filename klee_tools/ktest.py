import struct
import logging
import binascii

class KTest(object):
    def __init__(self, version, path, args, symArgvs, symArgvLen, objects):
        self.version = version
        self.path = path
        self.symArgvs = symArgvs
        self.symArgvLen = symArgvLen
        self.args = args
        self.objects = objects

    def __format__(self, format_spec):
        sio = io.StringIO()
        width = str(len(str(max(1, len(self.objects) - 1))))

        # print ktest info
        logging.info('ktest file : %r' % self.path)
        logging.info('args       : %r' % self.args)
        logging.info('num objects: %r' % len(self.objects))

        # format strings
        fmt = dict()
        fmt['name'] = "object {0:" + width + "d}: name: '{1}'"
        fmt['size'] = "object {0:" + width + "d}: size: {1}"
        fmt['int' ] = "object {0:" + width + "d}: int : {1}"
        fmt['uint'] = "object {0:" + width + "d}: uint: {1}"
        fmt['data'] = "object {0:" + width + "d}: data: {1}"
        fmt['hex' ] = "object {0:" + width + "d}: hex : 0x{1}"
        fmt['text'] = "object {0:" + width + "d}: text: {1}"

        # print objects
        for i, (name, data) in enumerate(self.objects):
            def p(key, arg): print(fmt[key].format(i, arg), file=sio)

            blob = data.rstrip(b'\x00') if format_spec.endswith('trimzeros') else data
            txt = ''.join(c if c in self.valid_chars else '.' for c in blob.decode('ascii', errors='replace').replace('�', '.'))
            size = len(data)

            p('name', name)
            p('size', size)
            p('data', blob)
            p('hex', binascii.hexlify(blob).decode('ascii'))
            for n, m in [(1, 'b'), (2, 'h'), (4, 'i'), (8, 'q')]:
                if size == n:
                    p('int', struct.unpack(m, data)[0])
                    p('uint', struct.unpack(m.upper(), data)[0])
                    break
            p('text', txt)

        return sio.getvalue()

    def get_object(self, object_name: str):
        for name, data in self.objects:
            if name == object_name:
                return data
        return b""

    def extract(self, filename):
        f = open(filename, 'wb')
        append_objects = ["stdin", "stdin-stat", "model_version"]
        for name, data in self.objects:
            if name not in append_objects:
                f.write(data)
        
        # for object_name in append_objects:
        #     # Get the data of the object with the name object_name
        # Append only STDIN at the end
        f.write(self.get_object("stdin"))
        
        f.close()
    
    @property
    def object_names(self):
        return set([name for name, data in self.objects])

    def update_object(self, name, data):
        for i, (n, d) in enumerate(self.objects):
            if n == name:
                # decode the hex string data after removing the 0x and new line
                data = binascii.unhexlify(data.strip().replace('0x', ''))
                # make sure the size is the same
                assert len(data) == len(d), "Size of data is not the same"
                self.objects[i] = (name, data)
                return

    def __str__(self):
        ret = ""
        ret += "ktest file : " + self.path + "\n"
        ret += "args       : " + str(self.args) + "\n"
        ret += "num objects: " + str(len(self.objects)) + "\n"
        ret += "total size : " + str(sum([len(data) for name, data in self.objects])) + "\n"
        return ret