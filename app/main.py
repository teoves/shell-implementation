import sys
import os

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
                if params[1] in BUILTINS: 
                    print(f"{params[1]} is a shell builtin")
                else: 
                    isFound = False
                    for dir in  os.environ.get("PATH","").split(os.pathsep):
                        full_path = os.path.join(dir,params[1])
                        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                            print(f"{params[1]} is {full_path}")
                            isFound = True
                            break;
                        
                    if not isFound: print(f"{params[1]}: not found")

            case _: print(f"{command}: command not found")


if __name__ == "__main__":
    main()
