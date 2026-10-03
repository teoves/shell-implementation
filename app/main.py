import sys


def main():
    while(True):
        sys.stdout.write("$ ")
        command = input()
        match command.split(' ')[0]:
            case "exit": break;
            case "echo": print(command.replace('echo ','',1))
            case "type":
                match command.split(' ')[1]:
                    case "exit" | "echo" | "type": print(f"{command.split(' ')[1]} is a shell builtin")
                    case _: print(f"{command.split(' ')[1]}: not found")
            case _: print(f"{command}: command not found")


if __name__ == "__main__":
    main()
