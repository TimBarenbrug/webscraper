"""
Usage:
    changelog_ws_cli.py
    changelog_ws_cli.py changelogsperperson
    changelog_ws_cli.py avgtimebetweenchangelogs
    changelog_ws_cli.py test
"""
import os 
import subprocess

from pprint import pprint
from docopt import docopt
from webscraper import ChangeLogScraper, ChangeLogArticle

if __name__ == '__main__':
    arguments = docopt(__doc__, version='DEMO 1.0')
    first_page_url = "https://support.hypernode.com/category/changelog/"
    parent_ws = ChangeLogScraper(first_page_url)
    if arguments['changelogsperperson']:
        pprint(parent_ws.change_logs_per_person())
    elif arguments['avgtimebetweenchangelogs']:
        print(parent_ws.avg_time_between_changelogs())
    elif arguments['test']:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        subprocess.run(['python3', os.path.join(dir_path, 'test_webscraper.py')])
    else:
        print(arguments)