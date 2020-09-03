import re
import pynvim
import subprocess
from os import path

# TODO:
# 1. Detect build directory.
# 2. Run build command.
# 3. Make list of build directories. ie. {CLang,GNU}, {Release,Debug}
@pynvim.plugin
class Building:
    def __init__(self, vim):
        self.vim           = vim
        self.build_dir     = None
        self.build_command = None
    
    def get_building_dir(self):
        index = 0
        found = False
        curret_dir = path.abspath(path.curdir)
        compile_commands = path.join(curret_dir, "compile_commands.json")

        while(not found and index < 3):
            compile_commands = path.join(curret_dir, "compile_commands.json")
            if(path.islink(compile_commands)):
                found = True
            index += 1
            curret_dir = path.abspath(path.join(path.curdir, ".."))
        
        if(found):
            self.build_dir = path.dirname(path.realpath(compile_commands))
            self.vim.out_write(self.build_dir + "\n")

    def detect_build_type(self):
        if path.exists(path.join(self.build_dir, "build.ninja")):
            self.build_command = "ninja"
        elif path.exists(path.join(self.build_dir, "build.ninja")):
            self.build_command = "Makefile"

    @pynvim.autocmd('BufEnter', pattern='*.cpp', sync=True)
    def setBuild(self):
        self.get_building_dir()

    @pynvim.command('Build', range='', nargs='*')
    def build(self, args, nargs='*'):
        if not self.build_dir:
            self.vim.err_write("Where is build dir?!\n")
            return

        self.detect_build_type()
        if not self.build_command:
            self.vim.err_write("Can not find build command?!\n")
            return
        
        self.runCommand(self.build_command)

    def runCommand(self, command):
        try:
            result = subprocess.run(command,
                                    shell=True,
                                    cwd=self.build_dir,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            if(result.returncode == 0):
                self.vim.out_write("Success!\n")
            else:
                copen_file = '/tmp/test.txt'
                self.write_erros(result.stdout, copen_file)
                self.write_to_quick_fix(copen_file)

        except subprocess.CalledProcessError as e:
            self.vim.out_write("ERROR ----\n")

    def write_erros(self, stdout, copen_file):
        errors = stdout.decode("utf-8")
        errors_string = errors.split('\n')
        filterd_errors = []
        for error in errors_string:
            tokens = error.split(' ')
            result = re.match("(?P<path>.*\.\w{3}):(?P<line>\d):(?P<col>\d):$", tokens[0])
            if result:
                filterd_errors.append(error)
        errors = '\n'.join([x for x in filterd_errors])
        with open(copen_file, 'w') as f:
            f.write(errors)

    def write_to_quick_fix(self, errors_file):
        # open errors in cerror
        self.vim.command(f"cfile {errors_file}")
        self.vim.command("copen")
