from pidwatcher import PidFileWatcher, write_pid_file


def main():
    proc = write_pid_file(__file__)
    print("PROG", proc)
    PidFileWatcher(proc, "QW", "QW2", debug=1).wait()
    print(f"{proc}: all required programs up")


if __name__ == "__main__":
    main()
