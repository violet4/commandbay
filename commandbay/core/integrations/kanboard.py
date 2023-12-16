import os
import tomllib
from threading import Lock
from typing import Set
import logging
from functools import wraps

import kanboard

logger = logging.getLogger(__name__)


def is_project_valid():
    def wrapper(fn):
        @wraps(fn)
        def wrapped(self, *args, **kwargs):
            project_id: int = getattr(self, 'project_id', -1)
            NO_PROJECT: int = getattr(self, 'NO_PROJECT', -1)
            if project_id == NO_PROJECT:
                return None
            return fn(self, *args, **kwargs)
        return wrapped
    return wrapper


class Kanboard(kanboard.Client):
    _lock = Lock()
    project_name: str
    project_id: int
    added_reminders: Set[str]
    NO_PROJECT: int = -1

    def __init__(self):
        self.added_reminders = set()
        this_file = os.path.abspath(__file__)
        this_dir = os.path.dirname(this_file)
        containing_dir = os.path.dirname(os.path.dirname(this_dir))
        toml_file = os.path.join(containing_dir, 'kanboard.toml')
        if not os.path.exists(toml_file):
            self.project_id = self.NO_PROJECT
            return
        with open(toml_file, 'rb') as fr:
            creds = tomllib.load(fr)['server']
        kwargs = {}
        self.project_name = creds['project_name']
        if 'cafile' in creds:
            kwargs['cafile'] = creds['cafile']
        super().__init__(creds['url'], creds['username'], creds['password'], **kwargs)
        try:
            self.project_id = self.get_project_by_name(name=self.project_name)['id']  # type: ignore
        except kanboard.ClientError:
            self.project_id = self.NO_PROJECT
            logger.exception(
                f"Failed to get project by name for project name '{self.project_name}'; "
                f"Does a project by that name exist? Do you lack permissions?"
            )

    @is_project_valid()
    def add_task(self, task_title:str):
        no_project_id = lambda: self.project_id == self.NO_PROJECT
        already_created_task = lambda: task_title in self.added_reminders

        if no_project_id() or already_created_task():
            return
        task = self.create_task(title=task_title, project_id=self.project_id)
        self.added_reminders.add(task_title)
        return task


if __name__ == '__main__':
    logger.setLevel(level=logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG)
    kb = Kanboard()
    import datetime
    task = kb.add_task(str(datetime.datetime.now()))
    print(task)
