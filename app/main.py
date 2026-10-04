import sys
import os
import subprocess

BUILTINS = ["exit", "echo", "type"]

def main():
    while(True):

        sys.stdout.write("$ ")
        user_input = input()
        params = user_input.split(' ')
        command = params[0]

        match command:
            case "exit": break;
            case "echo": print(user_input.replace('echo ','',1))
            case "type": 
                if(full_path := find_exec(params[1])):
                    print(f"{params[1]} is {full_path}")
                else:
                    print(f"{params[1]}: not found")

            case _: 
                if(full_path := find_exec(params[0])):
                    subprocess.run(params)
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
