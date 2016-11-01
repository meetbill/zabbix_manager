import sys
  
class Stats:
  
    def __init__(self, sequence):
        # sequence of numbers we will process
        # convert all items to floats for numerical processing
        self.sequence = [float(item) for item in sequence]
  
    def sum(self):
        if len(self.sequence) < 1:
            return None
        else:
            return sum(self.sequence)
  
    def count(self):
        return len(self.sequence)
  
    def min(self):
        if len(self.sequence) < 1:
            return None
        else:
            return min(self.sequence)
  
    def max(self):
        if len(self.sequence) < 1:
            return None
        else:
            return max(self.sequence)
  
    def avg(self):
        if len(self.sequence) < 1:
            return None
        else:
            return sum(self.sequence) / len(self.sequence)   
  
    def median(self):
        if len(self.sequence) < 1:
            return None
        else:
            self.sequence.sort()
            return self.sequence[len(self.sequence) // 2]
  
    def stdev(self):
        if len(self.sequence) < 1:
            return None
        else:
            avg = self.avg()
            sdsq = sum([(i - avg) ** 2 for i in self.sequence])
            stdev = (sdsq / (len(self.sequence) - 1)) ** .5
            return stdev
  
    def percentile(self, percentile):
        if len(self.sequence) < 1:
            value = None
        elif (percentile >= 100):
            sys.stderr.write('ERROR: percentile must be < 100.  you supplied: %s\n'% percentile)
            value = None
        else:
            element_idx = int(len(self.sequence) * (percentile / 100.0))
            self.sequence.sort()
            value = self.sequence[element_idx]
        return value

if __name__ == "__main__":
    sequence=[2.3,4,6,10]
    wang = Stats(sequence)
    print wang.min()
    print wang.max()
    print wang.avg()
