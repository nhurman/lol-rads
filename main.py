from RADS import RADS
from pprint import pprint
import os

wd = 'C:\\Riot Games\\League of Legends\\RADS\\solutions\\lol_game_client_sln\\releases\\0.0.1.155\\deploy'
r = RADS(wd)

locale = r.open_configuration('lol_game_client_sln', r.version).locale
solution = r.open_solution('lol_game_client_sln', r.version)
project_names = next(x.projects for x in solution.configurations if x.name == locale)
projects = [x for x in solution.projects if x.name in project_names]
project = r.open_project(projects[0].name, projects[0].version)

# List project files
#pprint(list(project.list_files()))

# Extract a file
#project.extract(project.files[121].path, os.path.basename(project.files[121].path))
#project.extract('DATA/CFG/defaults/Input.ini', 'Input.ini')
