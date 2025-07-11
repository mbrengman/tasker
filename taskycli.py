import csv
import os
from datetime import datetime
import re

options: list[str] = ['add', 'update', 'delete', 'in-progress', 'completed', 'list', 'change', 'done']
description: list[str] = [
    'to add a new task to the task list',
    'to change the status of a task',
    'to remove a task from the list',
    'to list all tasks that are currently in progress',
    'to list all completed tasks',
    'to list all tasks in the task list',
    'to change task status to in-progress',
    'to mark a task as done'
]
tasky: str = 'tasky-cli '

def list_options(options, description, tasky):
    index: int = 0
    while index < len(options):
        print(f'\t{options[index]} - {description[index]}')
        index += 1

def intro() -> str:
    print('\nTasky is now online...')
    print('Please choose from the following options: ')
    list_options(options, description, tasky)
    print('Press enter to quit')
    user: str = input(tasky)
    return user

def main():
    manager = Manager()
    manager.start_session()
    user: str = intro()
    while user != '':
        begin: list[str] = user.split()
        if begin[0] not in options:
            print('\nInvalid entry')
            list_options(options, description, tasky)
        elif len(user.split()) < 2:
            if user.startswith(options[5]): # list all tasks
                manager.display()
            elif user.startswith(options[3]): # list in progress
                manager.list_progressing()
            elif user.startswith(options[4]): # list completed
                manager.list_complete()
        else:
            choice: list[str] = user.split()
            if choice[0] not in options:
                print('\nInvalid entry')
                list_options(options, description, tasky)
            if len(choice) < 2:
                print('please input item')
                action: str = input(f'\t{tasky}')
                if action == '':
                    break
                user: str = f'{user} {action}'
            user: list[str] = user.split()
            if user[0] == options[0]: # add
                manager.add(user[1])
            elif user[0] == options[1]: # change
                if len(user) < 3:
                    print('option missing fields')
                    break
                manager.update(user[1], user[2])
            elif user[0] == options[2]: # remove
                manager.delete(user[1])
            elif user[0] == options[6]:
                manager.change_status(user[1])
            elif user[0] == options[7]: # done
                print(user[1])
                manager.complete(user[1])
            else:
                print("\nInvalid entry")
                list_options(options, description, tasky)
        user: str = input(tasky)
    manager.end_session()
    print('Goodbye')


class Manager:
    def __init__(self):
        self.tasks: dict[int, tuple[str]] = dict()
        self.origin: dict[int, tuple[str]] = dict()
        self.path: str = 'tasks.csv'
        self.id: int = 0

    def length(self) -> int:
        return len(self.tasks)

    def start_session(self):
        if os.path.exists(self.path):
            csv.register_dialect('tasker', delimiter='\n', quoting=csv.QUOTE_NONE)
            with open(self.path) as csvfile:
                task = csv.reader(csvfile, 'tasker')
                for row in task:
                    row = str(row).split(',')
                    key = re.findall(r'\d', row[0])
                    self.origin[int(''.join(key))] = (row[1], row[2], row[3], row[4].strip(']'))
                    self.tasks[int(''.join(key))] = (row[1], row[2], row[3], row[4].strip(']'))
                self.id = len(self.origin)

    def end_session(self):
        if self.origin != self.tasks:
            with open(self.path, 'w') as csvfile:
                fieldnames: list[str] = ['id', 'item', 'status', 'created', 'updated']
                task = csv.DictWriter(csvfile, fieldnames=fieldnames)
                for key, value in self.tasks.items():
                    task.writerow({
                        fieldnames[0]:key,
                        fieldnames[1]:value[0],
                        fieldnames[2]:value[1],
                        fieldnames[3]:value[2],
                        fieldnames[4]:value[3]})

    def add(self, item):
        for stuff in self.tasks.values():
            if item == stuff[0]:
                print('task already present')
                return
        self.id += 1
        if self.id == 1:
            status: str = 'in-progress'
        else:
            status: str = 'todo'
        self.tasks[self.id] = (item, status, get_time(), get_time())

    def complete(self, item):
        finish: str = 'completed'
        if item.isdigit():
            if int(item) > self.id:
                print(f'index {item} is out of range')
            for key, value in self.tasks.items():
                if key == item:
                    if value[1] == finish:
                        print(f'{value[0]} already marked {finish}')
                        return
                    print(f'marking {value[0]} complete')
                    self.update(key, finish)
                    return
        if item.isalpha():
            for key, value in self.tasks.items():
                if value[0] == item:
                    if value[1] == finish:
                        print(f'{item} already marked {finish}')
                        return
                    print(f'marking {value[0]} complete')
                    self.update(key, finish)
                    return
        print('program failed to find item')

    def change_status(self, item):
        new = dict()
        if item.isdigit():
            for key, value in self.tasks.items():
                if key != item and value[1] == 'in-progress':
                    new[key] = (value[0], 'todo', value[2], get_time())
                elif key == item and value[1] != 'in-progress':
                    new[key] = (value[0], 'in-progress', value[2], get_time())
                else:
                    new[key] = value
        elif item.isalpha():
            for key, value in self.tasks.items():
                if value[0] != item and value[1] == 'in-progress':
                    new[key] = (value[0], 'todo', value[2], get_time())
                elif value[0] == item and value[1] != 'in-progress':
                    new[key] = (value[0], 'in-progress', value[2], get_time())
                else:
                    new[key] = value
        if len(new) > 0:
            self.tasks = new

    def delete(self, item):
        if item.isdigit():
            if int(item) not in self.tasks.keys():
                print(f'{item} not in tasks')
                return
            else:
                print(f'deleting {item}')
                del self.tasks[int(item)]
        elif item.isalpha():
            output = None
            for key, value in self.tasks.items():
                if value[0] == item:
                    print(f'deleting {item}')
                    output: int = key
            if output:
                del self.tasks[output]
        if len(self.tasks) > 0:
            index: int = 1
            new: dict[tuple[str]] = dict()
            for value in self.tasks.values():
                new[index] = value
                index += 1
            self.tasks = new
            self.id = len(self.tasks)

    def display(self):
        if not self.tasks:
            print('No current tasks')
            return
        for key, value in self.tasks.items():
            print(f'{key} {value}')

    def list_complete(self):
        if not self.tasks:
            print('no current tasks')
            return
        for key, value in self.tasks.items():
            if value[1].endswith('done'):
                print(f'{key} {value}')

    def list_progressing(self):
        if not self.tasks:
            print('no current tasks')
            return
        for key, value in self.tasks.items():
            if value[1].endswith('progress'):
                print(f'{key} {value}')

    def update(self, id, action):
        if str(id).isalpha():
            for key, value in self.tasks.items():
                if value[0] == id:
                    self.tasks[key] = (value[0], action, value[2], get_time())
                    return
        elif str(id).isdigit():
            for key, value in self.tasks.items():
                if int(id) == key:
                    self.tasks[key] = (value[0], action, value[2], get_time())
                    return
        print(f'{id} not in task list')

def get_time():
    now: str = str(datetime.now())
    output: list[str] = now.split('.')
    output = output[0].replace(' ', '@')
    return output

main()
