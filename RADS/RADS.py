import os
from .parsers import ConfigurationManifest, SolutionManifest, ReleaseManifest

class RADS:
  def __init__(self, working_directory):
    self.working_directory = working_directory
    self.root = os.path.normpath(os.path.join(working_directory, '../' * 5))
    self.version = os.path.basename(os.path.dirname(working_directory))

  def solution_path(self, name, version):
    return os.path.join(self.root, 'solutions', name, 'releases', version)

  def project_path(self, name, version):
    return os.path.join(self.root, 'projects', name, 'releases', version)

  def archive_path(self, project_name, version):
    return os.path.join(self.root, 'projects', project_name, 'filearchives', version, 'Archive_1.raf')

  def open_configuration(self, name, version):
    path = os.path.join(self.solution_path(name, version), 'configurationmanifest')
    return ConfigurationManifest(path)

  def open_solution(self, name, version):
    path = os.path.join(self.solution_path(name, version), 'solutionmanifest')
    return SolutionManifest(path)

  def open_project(self, name, version):
    path = os.path.join(self.project_path(name, version), 'releasemanifest')
    return ReleaseManifest(path)
