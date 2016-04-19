import configparser
import os
import subprocess
import argparse

import sys

PROCESSES = [
    {'index': 1, 'process': 'Visual Studio'},
    {'index': 2, 'process': 'Message Router'},
    {'index': 3, 'process': 'Forecourt Controller'},
    {'index': 4, 'process': 'OSD Service'},
    {'index': 5, 'process': 'Ticket Module'},
    {'index': 6, 'process': 'Watchdog'},
]


class Branch:
    name = None
    base_path = None


class Launcher:
    def __init__(self):
        super().__init__()
        self.config = configparser.ConfigParser()
        self.config.read('launcher.cfg')
        self.run_in_2008 = self.config.get('General', 'run_in_2008')
        self.branches = []

    def load_branches(self):
        # Get root dir to look for branches
        root_dir = self.config.get('General', 'root_dir')
        # Walk root dir looking for branches
        for directory in os.listdir(root_dir):
            if os.path.isdir(os.path.join(root_dir, directory, 'SSF.Dev')):
                branch = Branch()
                branch.name = directory
                branch.base_path = os.path.join(root_dir, directory)
                self.branches.append(branch)

    @staticmethod
    def ask_for_config():
        conf = 1000
        while conf < 0 or conf > 2:
            print('1. Debug')
            print('2. Release')
            print('0. Exit')
            conf = int(input('Please, select a configuration: '))
        return conf

    def ask_for_branch(self):
        option = 1000
        while option < 0 or option > len(self.branches):
            i = 0
            for branch in self.branches:
                print('%d. %s' % (i, branch.name))
                i += 1
            print('%d. Exit' % i)
            option = int(input('Please, select a branch: '))
        return option

    @staticmethod
    def ask_for_what_to_run():
        option = 1000
        while option < 0 or option > len(PROCESSES):
            for process in PROCESSES:
                print('%d. %s' % (process['index'], process['process']))
            print('0. Exit')
            option = int(input('Please, what to run: '))

        return option

    @staticmethod
    def run_fusion(branch_base_path, what_to_run, debug=True):
        run_fusion = os.path.join(branch_base_path, 'SSF.Dev\\SSF.FC.Solution\\Scripts.Windows\\DevTools\\run_fusion.bat')
        print(run_fusion)
        subprocess.Popen([
            run_fusion,
            branch_base_path,
            what_to_run,
            'debug' if debug else 'release'
        ])

    def launch_vs(self, branch, conf_option):
        # Prepare PATH to launch VS
        env = os.environ
        bin_base_folder ='win32' if conf_option == 1 else 'win32.release'
        env['PATH'] = os.path.join(branch.base_path, 'SSF.Dev', bin_base_folder, 'lib') + ';' + env['PATH']
        sln_file = os.path.join(branch.base_path, 'SSF.Dev\SSF.FC.Solution\SSF.FC\Dev\SSF.FC-Global.sln')
        vs_path = ''
        if branch.name in self.run_in_2008:
            vs_path = self.config.get('General', 'vs2008')
        else:
            vs_path = self.config.get('General', 'vs2013')
        subprocess.Popen([vs_path, sln_file], env=env)

    def main(self):

        # Check branches downloaded
        self.load_branches()

        # Ask for what to run
        process_option = self.ask_for_what_to_run()
        if process_option == len(PROCESSES):
            return

        # Select branch
        branch_option = self.ask_for_branch()
        if branch_option == len(self.branches):
            return

        # Select run config
        config_option = self.ask_for_config()
        if config_option == 0:
            return

        branch = self.branches[branch_option]
        print('Selected branch: ', branch.name)

        if process_option == 1:
            print('Will launch Visual Studio')
            self.launch_vs(branch, config_option)

        if process_option == 2:
            print('Will launch Message Router')
            self.run_fusion(branch.base_path, 'router', True if config_option == 1 else False)

        if process_option == 3:
            print('Will launch Forecourt Controller')
            self.run_fusion(branch.base_path, 'fc', True if config_option == 1 else False)

        if process_option == 4:
            print('Will launch OSD Service')
            self.run_fusion(branch.base_path, 'osd', True if config_option == 1 else False)

        if process_option == 5:
            print('Will launch Ticket Module')
            self.run_fusion(branch.base_path, 'ticket_module', True if config_option == 1 else False)

        if process_option == 6:
            print('Will launch Watchdog')
            self.run_fusion(branch.base_path, 'watchdog', True if config_option == 1 else False)


if __name__ == '__main__':
    launcher = Launcher()
    launcher.main()

