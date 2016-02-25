import configparser
import os
import subprocess
import argparse

import sys


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
        args = type('Namespace', (object,), {})
        processes = [
            {'index': 1, 'process': 'Visual Studio'},
            {'index': 2, 'process': 'Message Router'},
        ]
        option = 1000
        while option < 0 or option > len(processes):
            for process in processes:
                print('%d. %s' % (process['index'], process['process']))
            print('0. Exit')
            option = int(input('Please, what to run: '))

        args.count = 0
        if option == 1:
            args.visual_studio = True
            args.msg_router = False
            args.count = 1
        if option == 2:
            args.msg_router = True
            args.visual_studio = False
            args.count = 1

        return args

    def launch_vs(self, branch, env):
        sln_file = os.path.join(branch.base_path, 'SSF.Dev', 'SSF.FC.Solution', 'SSF.FC', 'Dev', 'SSF.FC-Global.sln')
        vs_path = ''
        if branch.name in self.run_in_2008:
            vs_path = self.config.get('General', 'vs2008')
        else:
            vs_path = self.config.get('General', 'vs2013')
        subprocess.Popen([vs_path, sln_file], env=env)

    @staticmethod
    def launch_message_router(branch, env, conf):
        router_exe = os.path.join(branch.base_path,
                                  'SSF.Dev',
                                  'win32' if conf == 1 else 'win32.release', 'bin',
                                  'SSF.Msg.Router.D.exe' if conf == 1 else 'SSF.Msg.Router.exe'
                                  )
        print(router_exe)
        subprocess.Popen([router_exe, '-debug'], env=env, creationflags=subprocess.CREATE_NEW_CONSOLE)

    def main(self, args):
        arguments = args
        # Look for the branches
        self.load_branches()

        if args.interactive:
            arguments = self.ask_for_what_to_run()
            if arguments.count == 0:
                return

        # Select branch
        option = self.ask_for_branch()
        if option == len(self.branches):
            return

        # Select run config
        conf = self.ask_for_config()
        if conf == 0:
            return

        branch = self.branches[option]

        print('Selected branch: ', branch.name, 'Configuration: ', 'Debug' if conf == 1 else 'Release')

        env = os.environ
        env['PATH'] += os.path.join(branch.base_path, 'SSF.Dev', 'win32' if conf == 1 else 'win32.release', 'lib')

        if arguments.visual_studio:
            print('Will launch Visual Studio')
            self.launch_vs(branch, env)

        if arguments.msg_router is not None:
            print('Will launch Message Router')
            self.launch_message_router(branch, env, conf)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-vs', '--visual-studio', help='Launch VS', action='store_true')
    parser.add_argument('-mr', '--msg-router', help='Run Message Router', action='store_true')
    parser.add_argument('-i', '--interactive', help='Interactively ask what to run', action='store_true')

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
    else:
        launcher = Launcher()
        launcher.main(args)
