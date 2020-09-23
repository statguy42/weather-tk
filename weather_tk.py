import concurrent.futures
from gui import MainWindow

def main():
    threadworker = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    app = MainWindow(threadworker)
    app.mainloop()

if __name__ == "__main__":
    main()
