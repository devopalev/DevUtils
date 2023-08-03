from abc import ABC, abstractmethod
import time


class BaseProgressBar(ABC):
    @abstractmethod
    def print(self, iteration):
        print("|██████████-----------------------------------------------------------------------------------| 10.0%")


class PrintProgressBar(BaseProgressBar):
    """
    С анимацией, но не работает в PyCharm
    """
    def __init__(self, total, prefix='', suffix='', decimals=1, length=100, fill='█', print_end="\r"):
        """
        @params:
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """

        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.decimals = decimals
        self.length = length
        self.fill = fill
        self.print_end = print_end

    def print(self, iteration):
        """
            Call in a loop to create terminal progress bar
            @params:
                iteration   - Required  : current iteration (Int)
        """

        percent = ("{0:." + str(self.decimals) + "f}").format(100 * (iteration / float(self.total)))
        filled_length = int(self.length * iteration // self.total)
        bar = self.fill * filled_length + '-' * (self.length - filled_length)
        print(f'\r{self.prefix} |{bar}| {percent}% {self.suffix}', end=self.print_end)
        # Print New Line on Complete
        if iteration == self.total:
            print()


class SimpleProgresBar(PrintProgressBar):
    """
    Построчный. С прогнозом времени выполнения.

    step_percent - шаг отображения в процентах, например каждые 2 процента (2, 4, 6 ... 98, 100)
    Example:
        pb = SimpleProgresBar(2, 100)
        pb.start()
        for i in range(100):
            time.sleep(0.5)  # work
            pb.print(i+1)
    """

    def __init__(self, step_percent=5, *args, **kwargs):
        self.step_percent = step_percent
        self.next_step = 0

        self.estimated_time = 0
        self.start_time = 0

        super().__init__(*args, **kwargs)

    def forecast(self, perc):
        prog = None
        curr_time = time.time()
        if self.start_time:
            timer = curr_time - self.start_time
            prog = (100 / perc) * timer - timer

        if prog:
            return f"Осталось {round(prog)} сек. ({round(prog / 60, 1)} мин.) ({round(prog / 60 / 60, 1)} ч.)"

    def start(self):
        print(f"Complete: 0.0% (start)")
        self.start_time = time.time()

    def print(self, iteration):
        percent_decimal = 100 * (iteration / float(self.total))

        if percent_decimal >= self.next_step:
            percent = ("{0:." + str(self.decimals) + "f}").format(percent_decimal)
            prog = self.forecast(percent_decimal)

            if prog:
                print(f"Complete: {percent}% | {prog}")
            else:
                print(f"Complete: {percent}%")
            self.next_step += self.step_percent
        if iteration == self.total:
            total_time = time.time() - self.start_time
            print(f"Finish: {round(total_time, 3)} сек. ({round(total_time / 60, 1)} мин.) "
                  f"({round(total_time / 60 / 60, 1)})")