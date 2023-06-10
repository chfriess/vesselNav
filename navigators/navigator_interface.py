import math
import statistics

import numpy as np


class Navigator:

    @staticmethod
    def load_values(path: str):
        values = np.load(path)
        return list(values)

    @staticmethod
    def normalize_values(data: list) -> list:
        mu = statistics.mean(data)
        sigma = statistics.stdev(data)
        for i, el in enumerate(data):
            data[i] = (el - mu) / sigma
        return data

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

    @staticmethod
    def predict_impedance_from_diameter(diameter):
        # expects diameter in mm, converts it to m
        diameter = diameter / 1000
        circumference = diameter * math.pi
        csa = ((diameter / 2) ** 2) * math.pi
        sensor_distance = 3 / 1000
        tissue_conductivity = 0.30709
        blood_conductivity = 0.7
        return 1000 * ((csa * blood_conductivity) / sensor_distance + tissue_conductivity * circumference) ** (-1)


