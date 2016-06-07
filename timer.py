import threading


class Timer():
    """
    interval - in seconds
    args - array of arguments
    """

    def __init__(self, interval, callback, args=[], single_shot=False):
        self.interval = interval
        self.callback = callback
        self.single_shot = single_shot
        self.args = args
        self.timer = None

    def start(self):
        if self.single_shot:
            self.timer = threading.Timer(self.interval, self.callback, self.args)  # args already wrapped in array
        else:
            self.timer = threading.Timer(self.interval, self.wrapper, [])  # self is passed to wrapper implicitly

        self.timer.start()

    def stop(self):
        if self.timer is not None:
            self.timer.cancel()

    def wrapper(self):
        self.callback(*self.args)
        self.timer = threading.Timer(self.interval, self.wrapper, [])
        self.timer.start()
