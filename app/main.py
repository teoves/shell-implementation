import sys
import os
import subprocess
import readline

BUILTINS = ["exit", "echo", "type", "pwd", "cd"]

REDIRECTS = {
    ">":   ("out", "w"),
    "1>":  ("out", "w"),
    ">>":  ("out", "a"),
    "1>>": ("out", "a"),
    "2>":  ("err", "w"),
    "2>>": ("err", "a"),
}

# index all executables
def path_execs():
    names = set()
    for dir in os.environ.get("PATH","").split(os.pathsep):
        try:
            entries = os.listdir(dir)
        except OSError:
            continue
        for name in entries:
            full_path = os.path.join(dir,name)
            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                names.add(name)
    return names

matches = []

def completer(text, state):
    global matches
    if state == 0: # first call for this Tab press
        names = set(BUILTINS) | path_execs()
        matches = sorted(name + " " for name in names if name.startswith(text))
    return matches[state] if state < len(matches) else None

readline.set_completer(completer)
if "libedit" in (readline.__doc__ or ""):
    readline.parse_and_bind("bind ^I rl_complete")   # macOS
else:
    readline.parse_and_bind("tab: complete")         # GNU

def main():
    while(True):

        try:
            user_input = input("$ ")
        except EOFError:
            break
        params = [""]

        # parse input char-wise to apply quoting and escaping rules
        # by keeping track of the following states
        sq = False # single quotes are active
        dq = False # double quotes are active
        nl = False # next literal (treat next character as literal because of a backslash)
        for char in user_input:
            if nl:
                if dq and char not in '"\\$`':
                    params[-1] += "\\"
                params[-1] += char
                nl = False
                continue
            
            if char =="\\" and not sq:
                nl = True
                continue;
            else:
                nl = False

            if char == "\"" and not sq:
                dq = not dq
                continue

            if char == "'" and not dq:
                sq = not sq
                continue

            if sq or dq:
                params[-1]+=char
            else:
                #handle special chars
                #expand tilde
                if char == "~" and params[-1]=="":
                    params[-1] += os.path.expanduser("~")

                elif char == " ":
                    if params[-1]:
                        params.append("")
                else:
                    params[-1]+=char

        # remove trailing empty commands due to trailing whitespace
        if params[-1] == "" and len(params) > 1:
            params.pop()

        # preempt empty input
        if not params[0]:
            continue

        # handle redirects
        out, err = sys.stdout, sys.stderr
        for op, (stream, mode) in REDIRECTS.items():
            if op in params:
                i = params.index(op)
                f = open(params[i + 1], mode)
                params = params[:i] + params[i + 2:]
                if stream == "out":
                    out = f
                else:
                    err = f

        # handle command logic    
        command = params[0]  

        match command:
            case "exit": # exits 
                break;
            case "echo": # prints
                print(" ".join(params[1:]), file=out)
            case "type": # check if a command is builtin, external or not in PATH
                try:
                    prog = params[1]
                except IndexError:
                    print(f"{command}: no argument provided", file=err)
                    continue
                if prog in BUILTINS:
                    print(f"{prog} is a shell builtin", file=out)
                elif(full_path := find_exec(params[1])):
                    print(f"{prog} is {full_path}", file=out)
                else:
                    print(f"{prog}: not found", file=err)
            case "pwd": # print working directory
                print(os.getcwd(), file=out)
            case "cd": # change directory
                try:
                    target = params[1]
                except IndexError:
                    print(f"{command}: no directory provided", file=err)
                    continue
                try:
                    os.chdir(target)
                except OSError:
                    print(f"cd: {target}: No such file or directory", file=err)
            case _: 
                # handles execution of commands that are not builtins
                if(full_path := find_exec(params[0])):
                    subprocess.run(params, stdout=out, stderr=err)
                else:
                    print(f"{command}: command not found", file=err)

        # close out files that were opened for redirects if any
        if out is not sys.stdout:
            out.close()
        if err is not sys.stderr:
            err.close()

# helper function to search PATH for commands that are not builtins
def find_exec(command):
    for dir in  os.environ.get("PATH","").split(os.pathsep):
        full_path = os.path.join(dir,command)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            return full_path
    return None

if __name__ == "__main__":
    main()
