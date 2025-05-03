from task_5.system import System


def main():
    system = System()

    # print(system.find("слух"))
    # print(system.find("слабый слух"))
    # print(system.find("слабый фотофакт"))
    # print(system.find("слабый фотофакт и слух"))

    print("кадр: ", system.find("кадр"))
    print("значительный: ", system.find("значительный"))
    print("значительный кадр: ", system.find("значительный кадр"))
    print("значительное имя: ", system.find("значительное имя"))
    print("значительное имя и кадр: ", system.find("значительное имя и кадр"))


if __name__ == '__main__':
    main()
