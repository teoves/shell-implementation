import sys


def main():
    while(True):
        sys.stdout.write("$ ")
        command = input()
        match command.split(' ')[0]:
            case "exit": break;
            case "echo": print(command)
            case _: print(f"{command}: command not found")


if __name__ == "__main__":
    main()
