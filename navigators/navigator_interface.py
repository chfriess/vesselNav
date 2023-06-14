import math
import numpy as np


class Navigator:

    @staticmethod
    def load_values(path: str):
        values = np.load(path)
        return list(values)

    @staticmethod
    def rms(signal: list, groundtruth: list) -> float:
        if len(signal) != len(groundtruth):
            raise ValueError("signal and groundtruth must be of same length for rms calculation")
        acc = 0
        for i in range(len(groundtruth)):
            acc += math.pow((signal[i] - groundtruth[i]), 2)
        return math.sqrt(acc / len(groundtruth))

    @staticmethod
    def rms_of_deviations(deviations: list) -> float:
        acc = 0
        for i in range(len(deviations)):
            acc += math.pow((deviations[i]), 2)
        return math.sqrt(acc / len(deviations))

    @staticmethod
    def generate_reference():
        reference = []
        for i in range(75):
            reference.append((1 / 1.8) * 100)

        for i in range(100):
            reference.append((1 / 2) * 100)

        for i in range(80):
            reference.append((1 / 1.3) * 100)
        return reference
