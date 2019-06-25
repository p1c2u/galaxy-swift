class SeqIdGenerator:

    def __init__(self, start=1, step=1):
        self.start = start
        self.step = step

    def __iter__(self):
        return self

    def __next__(self):
        res = self.start
        self.start += self.step
        return res
