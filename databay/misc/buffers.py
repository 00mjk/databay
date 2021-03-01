import time
from typing import List, Union

from databay import Record


class Buffer():
    def __init__(self,
                 count_threshold : int = None,
                 time_threshold: float = None,
                 custom_controllers: Union[callable, List[callable]] = None):
        self.count_threshold = count_threshold
        self.time_threshold = time_threshold
        self.custom_controllers = custom_controllers

        if self.custom_controllers is None:
            self.custom_controllers = []
        elif not isinstance(self.custom_controllers, list):
            self.custom_controllers = [self.custom_controllers]


        self.controllers = []
        self.records = []

        self.time_start = None
        self.flush = False


    def count_controller(self, records:List[Record]) -> bool:
        if len(records) > self.count_threshold:
            return True
        else:
            return False

    def time_controller(self, records:List[Record]) -> bool:
        if self.time_start is None:
            self.time_start = time.time()

        if time.time() > (self.time_start + self.time_threshold):
            return True
        else:
            return False

    def get_controllers(self):
        controllers = []
        if self.count_threshold is not None:
            controllers.append(self.count_controller)
        if self.time_threshold is not None:
            controllers.append(self.time_controller)
        controllers = controllers + self.custom_controllers
        return controllers


    def execute(self, records:List[Record]) -> List[Record]:
        self.records += records
        rv = []
        if self.flush:
            rv =  self.records
        else:
            for controller in self.get_controllers():
                if controller(self.records):
                    rv = self.records

        if rv != []:
            self.reset()
        return rv


    def __call__(self, records:List[Record]):
        return self.execute(records)

    def reset(self):
        self.records = []
        self.time_start = None
        self.flush = False