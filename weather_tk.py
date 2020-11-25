import concurrent.futures
from gui import MainWindow

def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as threadworker:
        app = MainWindow(threadworker)
        app.mainloop()

if __name__ == "__main__":
    main()
