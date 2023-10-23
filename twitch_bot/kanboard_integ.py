import os
import tomllib
from threading import Lock
from typing import Set

import kanboard


class Kanboard(kanboard.Client):
    _lock = Lock()
    project_name: str
    project_id: int
    added_reminders: Set[str]
    def __init__(self):
        self.added_reminders = set()
        this_file = os.path.abspath(__file__)
        this_dir = os.path.dirname(this_file)
        containing_dir = os.path.dirname(this_dir)
        toml_file = os.path.join(containing_dir, 'kanboard.toml')
        with open(toml_file, 'rb') as fr:
            creds = tomllib.load(fr)['server']
        kwargs = {}
        self.project_name = creds['project_name']
        if 'cafile' in creds:
            kwargs['cafile'] = creds['cafile']
        super().__init__(creds['url'], creds['username'], creds['password'], **kwargs)
        self.project_id = self.get_project_by_name(name=self.project_name)['id'] # type: ignore

    def add_task(self, task_title:str):
        if task_title in self.added_reminders:
            return
        task = self.create_task(title=task_title, project_id=self.project_id)
        self.added_reminders.add(task_title)
        return task


if __name__ == '__main__':
    kb = Kanboard()
    import datetime
    task = kb.add_task(str(datetime.datetime.now()))
    print(task)
