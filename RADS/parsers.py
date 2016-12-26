import os
import struct
import zlib

class ParseException(Exception): pass

def parse_version(v):
  return '.'.join(str(x) for x in reversed(struct.unpack('BBBB', v)))

class ConfigurationManifest:
  def __init__(self, file_path = None):
    self.file_version = None
    self.projects = None
    self.locale = None

    if file_path != None:
      self.parse(file_path)

  def parse(self, f):
    fp = open(f)

    # Header
    c = fp.readline()
    if 'RADS Configuration Manifest\n' != c:
      raise ParseException('Header mismatch, got [{}]'.format(c))

    c = fp.readline()
    if '1.0.0.0\n' != c:
      raise ParseException('Version mismatch, got [{}]'.format(c))
    self.file_version = c.strip()

    c = fp.readline()
    if 'en_gb\n' != c:
      raise ParseException('Locale mismatch, got [{}]'.format(c))
    self.locale = c.strip()

    c = fp.readline().strip()
    if 0 == len(c) or not c.isdigit():
      raise ParseException('Number of items format error, got [{}]'.format(c))
    nb_projects = int(c)

    self.projects = []
    for i in range(nb_projects):
      c = fp.readline().strip()
      if 0 == len(c):
        raise ParseException('Empty item at iteration {}'.format(i))
      self.projects.append(c)

class Project:
  def __init__(self):
    self.name = None
    self.version = None
    self.priority = None
    self.flags = None

  def __repr__(self):
    return repr(self.__dict__)

class Configuration:
  def __init__(self):
    self.name = None
    self.flags = None
    self.projects = None

  def __repr__(self):
    return repr(self.__dict__)

class SolutionManifest:
  def __init__(self, file_path = None):
    self.projects = None
    self.name = None
    self.file_version = None
    self.version = None
    self.projects = None

    if file_path != None:
      self.parse(file_path)

  def parse(self, f):
    fp = open(f)

    # Header
    c = fp.readline()
    if 'RADS Solution Manifest\n' != c:
      raise ParseException('Header mismatch, got [{}]'.format(c))

    c = fp.readline()
    if '1.0.0.0\n' != c:
      raise ParseException('Version mismatch, got [{}]'.format(c))
    self.file_version = c.strip()

    c = fp.readline().strip()
    if len(c) == 0:
      raise ParseException('Empty solution name')
    self.name = c

    c = fp.readline().strip()
    if len(c) == 0:
      raise ParseException('Empty solution version')
    self.version = c

    # Projects
    c = fp.readline().strip()
    if 0 == len(c) or not c.isdigit():
      raise ParseException('Number of projects format error, got [{}]'.format(c))
    nb_projects = int(c)

    self.projects = []
    for i in range(nb_projects):
      project = Project()

      # Name
      c = fp.readline().strip()
      if len(c) == 0:
        raise ParseException('Empty project name')
      project.name = c

      # Version
      c = fp.readline().strip()
      if len(c) == 0:
        raise ParseException('Empty project version')
      project.version = c.strip()

      # Priority
      c = fp.readline().strip()
      if 0 == len(c) or not c.isdigit():
        raise ParseException('Priority format error, got [{}]'.format(c))
      project.priority = int(c)

      # Flags
      c = fp.readline().strip()
      if 0 == len(c) or not c.isdigit():
        raise ParseException('Flags format error, got [{}]'.format(c))
      project.flags = int(c)

      self.projects.append(project)

    # Configurations
    c = fp.readline().strip()
    if 0 == len(c) or not c.isdigit():
      raise ParseException('Number of configurations format error, got [{}]'.format(c))
    nb_configurations = int(c)

    self.configurations = []
    for i in range(nb_configurations):
      configuration = Configuration()

      # Name
      c = fp.readline().strip()
      if len(c) == 0:
        raise ParseException('Empty project name')
      configuration.name = c

      # Flags
      c = fp.readline().strip()
      if 0 == len(c) or not c.isdigit():
        raise ParseException('Flags format error, got [{}]'.format(c))
      configuration.flags = int(c)

      # Project count
      c = fp.readline().strip()
      if 0 == len(c) or not c.isdigit():
        raise ParseException('Project count format error, got [{}]'.format(c))
      nb_projects = int(c)

      configuration.projects = []
      for j in range(nb_projects):
        # Name
        c = fp.readline().strip()
        if len(c) == 0:
          raise ParseException('Empty project name')
        configuration.projects.append(c)
      self.configurations.append(configuration)

class Directory:
  def __init__(self):
    self.name_index = None
    self.subdirs_index = None
    self.subdirs_nb = None
    self.files_index = None
    self.files_nb = None

    self.name = None
    self.subdirs = []
    self.files = []

  def __repr__(self):
    return 'Dir(name={}, subdirs_nb={}, files_nb={})'.format(
      self.name, self.subdirs_nb, self.files_nb)

  def pretty(self, indent = 0):
    out = ['  ' * indent + repr(self)]
    for f in self.files:
      out.append('  ' * (1+indent) + repr(f))
    for d in self.subdirs:
      out.append(d.pretty(indent + 1))
    return '\n'.join(out)

  def list_files(self):
    files = [f.path for f in self.files]
    for d in self.subdirs:
      files += d.list_files()
    return files

class File:
  def __init__(self):
    self.name_index = None
    self.version = None
    self.hash = None

    # Compressed = 0x10
    self.flags = None

    self.size = None
    self.compressed_size = None
    self.unk1 = None
    self.type = None
    self.unk2 = None
    self.unk3 = None

    self.name = None
    self.path = None

  def __repr__(self):
    return 'File(name={}, version={}, size={}, csize={}, flags={})'.format(
      self.name, self.version, self.size, self.compressed_size, self.flags)

class ReleaseManifest:
  def __init__(self, file_path = None):
    self.type = None
    self.entries = None
    self.version = None
    self.files = None

    self.tree = None
    self.file_path = None
    self.rafs = {}
    if file_path != None:
      self.parse(file_path)

  def __repr__(self):
    tree = '' if self.tree == None else '\n' + self.tree.pretty(1)
    return 'ReleaseManifest(type={}, version={}, entries={})'.format(
      self.type, self.version, self.entries) + tree

  def list_files(self):
    return self.tree.list_files()

  def parse(self, f):
    self.file_path = f
    fp = open(f, 'rb')

    # Magic
    headers_magic = fp.read(4)
    if b'RLSM' != headers_magic:
      raise ParseException('Invalid magic value, got [{}]'.format(headers_magic))

    self.type = struct.unpack('<I', fp.read(4))[0]
    self.entries = struct.unpack('<I', fp.read(4))[0]
    self.version = parse_version(fp.read(4))

    nb_directories = struct.unpack('<I', fp.read(4))[0]
    directories = []
    for i in range(nb_directories):
      d = Directory()
      d.name_index = struct.unpack('<I', fp.read(4))[0]
      d.subdirs_index = struct.unpack('<I', fp.read(4))[0]
      d.subdirs_nb = struct.unpack('<I', fp.read(4))[0]
      d.files_index = struct.unpack('<I', fp.read(4))[0]
      d.files_nb = struct.unpack('<I', fp.read(4))[0]

      directories.append(d)

    nb_files = struct.unpack('<I', fp.read(4))[0]
    self.files = []
    for i in range(nb_files):
      f = File()
      f.name_index = struct.unpack('<I', fp.read(4))[0]
      f.version = parse_version(fp.read(4))
      f.hash = fp.read(16)
      f.flags = struct.unpack('<I', fp.read(4))[0]
      f.size = struct.unpack('<I', fp.read(4))[0]
      f.compressed_size = struct.unpack('<I', fp.read(4))[0]
      f.unk1 = struct.unpack('<I', fp.read(4))[0]
      f.type = struct.unpack('<H', fp.read(2))[0]
      f.unk2 = struct.unpack('B', fp.read(1))[0]
      f.unk3 = struct.unpack('B', fp.read(1))[0]

      self.files.append(f)

    strings_nb = struct.unpack('<I', fp.read(4))[0]
    strings_size = struct.unpack('<I', fp.read(4))[0]
    pos = fp.tell()

    strings = []
    strings_buff = fp.read(strings_size)
    strings = strings_buff.split(b'\0')[:-1]

    for d in directories:
      d.name = strings[d.name_index].decode('ascii')

    for f in self.files:
      f.name = strings[f.name_index].decode('ascii')

    directories[0].path = ''
    dirs_todo = [directories[0]]
    while len(dirs_todo) > 0:
      d = dirs_todo.pop()
      d.subdirs = []
      for i in range(d.subdirs_index, d.subdirs_index + d.subdirs_nb):
        directories[i].path = d.path + directories[i].name + '/'
        d.subdirs.append(directories[i])
        dirs_todo.append(directories[i])

      d.files = []
      for i in range(d.files_index, d.files_index + d.files_nb):
        self.files[i].path = d.path + self.files[i].name
        d.files.append(self.files[i])

    self.tree = directories[0]

  def extract(self, path, dest):
    f = next(x for x in self.files if x.path == path)
    project_path = os.path.normpath(os.path.join(self.file_path, '../' * 3))
    project_name = os.path.dirname(project_path)
    raf = os.path.join(project_path, 'filearchives', f.version, 'Archive_1.raf')

    if raf not in self.rafs:
      self.rafs[raf] = RAF(raf)

    archive = self.rafs[raf]
    archive.extract(f.path, dest)

def hash_path(path):
  h = 0
  temp = 0
  for c in path:
    h = (h << 4) + ord(c.lower())
    temp = h & 0xf0000000
    if temp != 0:
      h = h ^ (temp >> 24)
      h = h ^ temp
  return h

class RAFFile:
  def __init__(self):
    self.path_hash = None
    self.data_offset = None
    self.data_size = None
    self.path_index = None

    self.path = None

  def __repr__(self):
    return str(self.path)

class RAF:
  def __init__(self, file_path = None):
    self.version = None
    self.manager_index = None
    self.files = None
    self.file_path = None

    if file_path != None:
      self.parse(file_path)

  def __repr__(self):
    return 'RAF(version={}, nb_files={})'.format(
      self.version, len(self.files))

  def parse(self, f):
    self.file_path = f
    fp = open(f, 'rb')

    # Magic
    headers_magic = fp.read(4)
    if b'\xf0\x0e\xbe\x18' != headers_magic:
      raise ParseException('Invalid magic value, got [{}]'.format(headers_magic))

    self.version = parse_version(fp.read(4))
    self.manager_index = struct.unpack('<I', fp.read(4))[0]
    files_offset = struct.unpack('<I', fp.read(4))[0]
    paths_offset = struct.unpack('<I', fp.read(4))[0]

    # File list
    nb_files = struct.unpack('<I', fp.read(4))[0]
    self.files = []
    for i in range(nb_files):
      f = RAFFile()
      f.path_hash = struct.unpack('<L', fp.read(4))[0]
      f.data_offset = struct.unpack('<I', fp.read(4))[0]
      f.data_size = struct.unpack('<I', fp.read(4))[0]
      f.path_index = struct.unpack('<I', fp.read(4))[0]
      self.files.append(f)

    # Path list
    paths_size = struct.unpack('<I', fp.read(4))[0]
    paths_nb = struct.unpack('<I', fp.read(4))[0]
    paths = []
    for i in range(paths_nb):
      path_offset = struct.unpack('<I', fp.read(4))[0]
      path_len = struct.unpack('<I', fp.read(4))[0]
      paths.append((path_offset, path_len))

    # Strings
    path_strings = fp.read()
    for f in self.files:
      string_offset, string_len = paths[f.path_index][0], paths[f.path_index][1]
      start = string_offset - 2*4 - 2*4*paths_nb
      path = path_strings[start:start + string_len]

      if path[-1] == 0: path = path[:-1]
      f.path = path.decode('ascii')

      if (hash_path(f.path) != f.path_hash):
        raise ParseException('Path hash mismatch for {}, computed={} stored={}'.format(f.path, hash_path(f.path), f.path_hash))

  def extract(self, src, dest, decompress = True):
    f = next(x for x in self.files if x.path == src)
    fp1 = open(self.file_path + '.dat', 'rb')
    fp2 = open(dest, 'wb+')
    fp1.seek(f.data_offset)
    d = fp1.read(f.data_size)
    if decompress: d = zlib.decompress(d)
    fp2.write(d)
    fp2.close()
    fp1.close()
