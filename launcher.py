import configparser
import os
import subprocess
import argparse


class Branch:
    name = None
    base_path = None


class VSLauncher:
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

    def main(self, args):
        # Look for the branches
        self.load_branches()

        option = self.ask_for_option()

        if option == 0:
            return

        conf = self.ask_for_config()

        if conf == 0:
            return

        branch = self.branches[option]

        print('Selected branch: ', branch.name, 'Configuration: ', 'Debug' if conf == 1 else 'Release')

        env = os.environ
        env['PATH'] += os.path.join(branch.base_path, 'SSF.Dev', 'win32' if conf == 'Debug' else 'win32.release','lib')

        self.launch_vs(branch, env)

    def launch_vs(self, branch, env):
        sln_file = os.path.join(branch.base_path, 'SSF.Dev', 'SSF.FC.Solution', 'SSF.FC', 'Dev', 'SSF.FC-Global.sln')
        vs_path = ''
        if branch.name in self.run_in_2008:
            self.config.get('General', 'vs2008')
        else:
            self.config.get('General', 'vs2013')
        subprocess.Popen([vs_path, sln_file], env=env)

    @staticmethod
    def ask_for_config():
        conf = 1000
        while conf < 0 or conf > 2:
            print('1. Debug')
            print('2. Release')
            print('0. Exit')
            conf = int(input('Please, select a configuration: '))
        return conf

    def ask_for_option(self):
        option = 1000
        while option < 0 or option > len(self.branches):
            i = 0
            for branch in self.branches:
                print('%d. %s' % (i, branch.name))
                i += 1
            print('%d. Exit' % i)
            option = int(input('Please, select a branch: '))
        return option


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-vs', '--visual-studio', help='Launch VS', action='store_true')
    parser.add_argument('-m', '--message-router', help='Run Message Router', action='store_true')

    args = parser.parse_args()

    if not args.spiders and not args.normalizer  and not args.eraser and not args.samleren:
        parser.print_help()
    else:
        launcher = VSLauncher()
        launcher.main(args)
