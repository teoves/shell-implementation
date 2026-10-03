import sys


def main():
    while(True):
        sys.stdout.write("$ ")
        command = input()
        match command:
            case "exit": break;
            case "echo": print(command)

        print(f"{command}: command not found")


if __name__ == "__main__":
    main()
