import concurrent.futures
from gui import MainWindow

def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as threadworker:
        # this threadpool is used to fetch weather data
        # it's used so that the tkinter's mainloop does not get blocked by a http request
        # it's being passed to the app so that a method inside it can use it
        app = MainWindow(threadworker)
        app.mainloop()

if __name__ == "__main__":
    main()
