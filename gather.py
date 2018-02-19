import os
import subprocess
import traceback
from importlib import import_module

def _set_value(node, path, value):
    ''' Sets a value inside a complex data dictionary.
        The path Array must have at least one element.
    '''
    key = path[0]
    if len(path) == 1:
        node[key] = value
    elif key in node:
        _set_value(node[key], path[1:], value)
    else:
        node[path[0]] = {}
        _set_value(node[key], path[1:], value)


def _compile_file(fname):
    with open(fname) as file:
        return compile(file.read(), os.path.abspath(fname), 'eval')

class Source():
    @classmethod
    def from_file(cls, fname, providerdir):
        srcname = os.path.relpath(fname, providerdir)
        return Source(srcname.rsplit(os.sep), _compile_file(fname))

    def __init__(self, path, code):
        self.path = path
        self.code = code

    def get_path(self):
        return self.path

    def exec(self, env):
        def call(cmdnargs):
            output = subprocess.check_output(cmdnargs)
            lines = output.splitlines()
            lines = [line.decode("utf-8") for line in lines]
            return lines

        real_env = dict(env)
        real_env.update({
           'call': call,
           'import_module': import_module
        })

        # ensure that files are opened as UTF-8
        import locale
        encoding_backup = locale.getpreferredencoding
        locale.getpreferredencoding = lambda _=None: 'UTF-8'
        try:
            ret = eval(self.code, real_env)
        finally:
            locale.getpreferredencoding = encoding_backup
        return ret

class Provider():
     @classmethod
     def from_directory(cls, dir):
        dirname = os.path.basename(dir)

        providernameparts = dirname.split('.')
        if len(providernameparts) != 2:
            raise ValueError("'{}' is not a valid provider directory".format(providerdir))

        provider = Provider(providernameparts[0])
        for path, _, files in os.walk(dir):
             for file in files:
                 srcfile = os.path.join(path, file)
                 src = Source.from_file(srcfile, dir)
                 provider.add_source(src)

        return provider


     def __init__(self, name):
         self.name = name
         self.sources = []

     def add_source(self, source):
         self.sources.append(source)

     def exec(self, env):
         ret = {}
         for source in self.sources:
             try:
                 _set_value(ret, source.get_path(), source.exec(env))
             except:
                traceback.print_exc()

         return ret

     def get_name(self):
         return self.name

def gather_providers(directory):
    providers = {}

    if not os.path.isdir(directory):
        raise FileNotFoundError("The path '{}' is not a valid directory\n".format(directory))

    for dir in next(os.walk(directory))[1]:
        provider = Provider.from_directory(os.path.abspath(os.path.join(directory, dir)))

        providers[provider.get_name()] = provider

    return providers
        

def gather_data(provider, env={}):
    return provider.exec(env)
