import matplotlib
from matplotlib import pyplot as plt
import logging
import time
from scipy.stats import sem
from statistics import mean

from filter.model import Model
import numpy as np


def load_values(path: str):
    values = np.load(path)
    return list(values)


def save_results(position_estimate: list, path: str):
    raise NotImplementedError("function save results not implemented yet")


def display_results(grtruth: list, pfestimates: list):  # TODO: change to vessel tree position estimate
    posest = []
    err = []

    for clusterPositionEstimate in pfestimates:  # TODO: change to vessel tree position estimate
        posest.append(clusterPositionEstimate.first_cluster.center)
        err.append(clusterPositionEstimate.first_cluster.error)
    x = [p for p in range(len(grtruth))]
    y = [l for l in range(len(posest))]

    font = {'family': 'normal',
            'size': 14}

    matplotlib.rc('font', **font)

    plt.plot(x, grtruth, color="black", label="groundtruth")
    plt.plot(y, posest, color="blue", label="PF position estimate")
    plt.errorbar(y, posest, yerr=err, fmt="o", color="blue", capsize=4)

    plt.legend()
    plt.xlabel("update steps [update frequency 10Hz]")
    plt.ylabel("cumulative displacement in mm")
    plt.show()

    acc = []
    for index in range(len(grtruth)):
        acc.append(posest[index] - grtruth[index])
    logging.info(
        "final difference estimate vs. groundtruth = " + str(grtruth[-1] - pfestimates[-1].first_cluster.center))
    logging.info("Mean absolute deviation of PF estimate from groundtruth in mm = " + str(mean(acc)))
    logging.info("Sem of Mean absolute deviation of PF estimate from groundtruth in mm = " + str(sem(acc)))
    logging.info("Mean particle dispersion at each time step as sem of dominant cluster = " + str(sem(err)))


if __name__ == "__main__":

    reference_path = ""
    impedance_path = ""
    groundtruth_path = ""
    displacements_path = ""

    ref = load_values(reference_path)
    impedance = load_values(impedance_path)
    groundtruth = load_values(groundtruth_path)
    displacements = load_values(displacements_path)

    position_estimate = []

    model = Model()
    model.setup_particle_filter(reference=ref,
                                measurement_model="ahistoric")
    model.setup_particles(number_of_particles=1000,
                          initial_position=0)
    model.setup_logger(loglevel=logging.INFO,
                       log_directory="C:\\Users\\Chris\\OneDrive\\Desktop\\")

    length = len(displacements) if len(displacements) < len(impedance) else len(impedance)
    position_estimate.append(model.estimate_current_position_dbscan())

    acc = 0
    for i in range(length):
        logging.info("Groundtruth = " + str(groundtruth[i]))
        start = time.time()
        model.update_model(displacement=displacements[i],
                           impedance=impedance[i])
        end = time.time()
        acc += (end - start)
        position_estimate.append(model.estimate_current_position_dbscan())
        print("Best position estimate cluster: " + str(position_estimate[i]))
        print("Position estimate total mean" + str(model.estimate_current_position_mean()))

    display_results(groundtruth, position_estimate)
