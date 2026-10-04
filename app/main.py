import sys
import os
import subprocess

BUILTINS = ["exit", "echo", "type", "pwd", "cd"]

def main():
    while(True):

        sys.stdout.write("$ ")
        user_input = input()
        params = [""]

        #implement single quoting
        sq = False #single quotes
        dq = False #double quotes
        nl = False #next literal
        for char in user_input:
            if nl:
                params[-1]+=char
                nl = False
                continue;
            
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

        if params[-1] == "" and len(params) > 1:
            params.pop()
            
        command = params[0]

        match command:
            case "exit": break;
            case "echo": print(" ".join(params[1:]))
            case "type":
                if params[1] in BUILTINS:
                    print(f"{params[1]} is a shell builtin")
                elif(full_path := find_exec(params[1])):
                    print(f"{params[1]} is {full_path}")
                else:
                    print(f"{params[1]}: not found")
            case "pwd":
                print(os.getcwd())
            case "cd":
                target = params[1]
                try:
                    os.chdir(target)
                except OSError:
                    print(f"cd: {target}: No such file or directory")
            case _: 
                if(full_path := find_exec(params[0])):
                    subprocess.run(params)
                    #in case of 'clear' do it again to fully clear it should display something
                    if params[0] == "clear": subprocess.run(params)
                else:
                    print(f"{command}: command not found")

def find_exec(command):
    for dir in  os.environ.get("PATH","").split(os.pathsep):
        full_path = os.path.join(dir,command)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            return full_path
          
    return None

if __name__ == "__main__":
    main()
