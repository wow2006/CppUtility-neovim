import os, sys, copy
import json
import neovim
import tempfile
import weakref
import subprocess
from os import chdir, curdir, remove
from os.path import dirname, exists, isdir, join, abspath


@neovim.plugin
class Main(object):
    def __init__(self, vim):
        self.vim = vim
        self.temp_file = join(tempfile.gettempdir(), tempfile.gettempprefix() + "_analysis")
        self.build_dir = ''
        json_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins.json")

        with open(json_file, "r") as f:
            self.commands = json.load(f)

    def __del__(self):
        remove(self.temp_file)

    @neovim.function('DoItPython')
    def doItPython(self, args):
        self.vim.command('echo "hello"')

    @neovim.command('Tidy', range='', nargs='*')
    def analysisTidy(self, args, nargs='*'):
        self.vim.out_write("args {} {}\n".format(len(args), args))
        if type(args) == str:
            self.readTidy(args)
        else:
            self.readTidy(*args)

    @neovim.command('ReadabilityTidy', range='', nargs='*')
    def TidyReadability(self, args, nargs='*'):
        self.analysisTidy('readability-*')

    @neovim.command('ReadabilityTidyFix', range='', nargs='*')
    def TidyReadabilityFix(self, args, nargs='*'):
        self.analysisTidy(['readability-*', '-fix'])

    @neovim.command('ModernizeTidy', range='', nargs='*')
    def TidyModernize(self, args, nargs='*'):
        self.analysisTidy('modernize-*')

    @neovim.command('PortabilityTidy', range='', nargs='*')
    def TidyPortability(self, args, nargs='*'):
        self.analysisTidy('portability-*')

    @neovim.command('PerformanceTidy', range='', nargs='*')
    def TidyPerformance(self, args, nargs='*'):
        self.analysisTidy('performance-*')

    @neovim.command('CppCoreGuidelinesTidy', range='', nargs='*')
    def TidyCppCoreGuidelines(self, args, nargs='*'):
        self.analysisTidy('cppcoreguidelines-*')

    @neovim.command('ClangAnalyzerTidy', range='', nargs='*')
    def TidyClangAnalyzer(self, args, nargs='*'):
        self.analysisTidy('clang-analyzer-*')

    def readTidy(self, analysisFilter, fix_file=None):
        current_file = self.vim.current.buffer.name

        if(not current_file):
            return

        tidy_info = copy.deepcopy(self.commands["clang-tidy"])

        command = tidy_info["pipeline"][0]

        args = tidy_info[command]

        index = args.index("{current_file}")

        args[index] = current_file

        if analysisFilter:
            args[2] = analysisFilter

        if fix_file:
            args[3] = fix_file
        else:
            args[3] = ""

        full_command = args[0].format(*args[1:])

        result = self.runCommand(full_command)

        if not result:
            self.vim.out_write("Result is None")
            return

        if fix_file:
            self.vim.call(":edit")
            return

        errors = result.stdout.decode("utf-8")

        self.writeToQuickFix(errors, current_file)

    def runCommand(self, command):
        self.vim.out_write("{}\n".format(command))
        try:
            result = subprocess.run(command,
                                    shell=True, check=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)

            if(result.returncode in [0, 1]):
                return result

            self.vim.err_write("ERROR at {}:\n{}\n{}".format(result.args,
                               result.stderr.decode("utf-8"),
                               result.stdout.decode("utf-8")))

            return None
        except subprocess.CalledProcessError as e:
            self.vim.out_write("ERROR ----")
            #self.vim.err_write(e.output)

    def writeToQuickFix(self, error_string, current_file):
        errors_string = error_string.split('\n')
        errors = '\n'.join([x for x in errors_string if current_file in x])

        with open('/tmp/test.txt', 'w') as f:
            f.write(errors)

        if not errors:
            errors = "Nothing to do!\n"

        # write errors to temp file
        with open(self.temp_file, 'w') as f:
            f.write(errors)

        # open errors in cerror
        self.vim.command("cfile %s" % self.temp_file)
        self.vim.command("copen")

