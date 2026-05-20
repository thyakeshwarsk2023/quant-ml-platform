from abc import ABC, abstractmethod

class Strategy(ABC):
    def __init__(self,data):
        self.data =  data

    @abstractmethod
    def generate_signal(self,i):
        pass
        