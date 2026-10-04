import sys
import os
import subprocess

BUILTINS = ["exit", "echo", "type", "pwd", "cd"]

def main():
    while(True):

        sys.stdout.write("$ ")
        try:
            user_input = input()
        except EOFError:
            break
        params = [""]

        # parse input char-wise to apply quoting and escaping rules
        # by keeping track of the following states
        sq = False #single quotes
        dq = False #double quotes
        nl = False #next literal
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
            
        command = params[0]

        #handle command logic
        match command:
            case "exit": # exits 
                break;
            case "echo": # prints
                print(" ".join(params[1:]))
            case "type": # check if a command is builtin, external or not in PATH
                try:
                    prog = params[1]
                except IndexError:
                    print(f"{command}: no argument provided")
                    continue
                if prog in BUILTINS:
                    print(f"{prog} is a shell builtin")
                elif(full_path := find_exec(params[1])):
                    print(f"{prog} is {full_path}")
                else:
                    print(f"{prog}: not found")
            case "pwd": # print working directory
                print(os.getcwd())
            case "cd": # change directory
                try:
                    target = params[1]
                except IndexError:
                    print(f"{command}: no directory provided")
                    continue
                try:
                    os.chdir(target)
                except OSError:
                    print(f"cd: {target}: No such file or directory")
            case _: 
                #handles execution of commands that are not builtins
                if(full_path := find_exec(params[0])):
                    subprocess.run(params)
                else:
                    print(f"{command}: command not found")

# function to search PATH for commands that are not builtins
def find_exec(command):
    for dir in  os.environ.get("PATH","").split(os.pathsep):
        full_path = os.path.join(dir,command)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            return full_path
    return None

if __name__ == "__main__":
    main()
