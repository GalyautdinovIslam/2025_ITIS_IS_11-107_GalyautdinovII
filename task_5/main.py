from task_5.system import System


def main():
    system = System()
    print(system.find("слух"))
    print(system.find("слабый слух"))
    print(system.find("слабый фотофакт"))
    print(system.find("слабый фотофакт и слух"))


if __name__ == '__main__':
    main()
