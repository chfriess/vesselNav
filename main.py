import logging

import matplotlib
import numpy as np
import os
import time
from numpy import random
import matplotlib.pyplot as plt
from scipy.stats import sem
from statistics import mean

from filter.model import Model
from filter.particle_filter import ParticleFilter
from injectors.AlphaVarianceInjector import AlphaVariationInjector
from measurement_models.ahistoric_measurement_model import AhistoricMeasurementModel
from motion_models.motion_model import MotionModel
from resamplers.low_variance_resampler import LowVarianceResampler
from utils.particle import Particle
from utils.particle_set import ParticleSet
from utils.state import State

os.chdir("C:\\Users\\Chris\\OneDrive\\Desktop\\")
logging.basicConfig(
    filename='particleFilterLog.log',
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


def setup_model(reference: list) -> Model:
    particle_filter = setup_particle_filter(reference=reference)
    particles = setup_initial_particle_set()
    return Model(particle_filter=particle_filter,
                 particles=particles,
                 loglevel=logging.INFO,
                 log_directory="C:\\Users\\Chris\\OneDrive\\Desktop\\")


def setup_particle_filter(reference: list) -> ParticleFilter:
    motion_model = MotionModel()
    measurement_model = AhistoricMeasurementModel(reference_signal=reference)
    resampler = LowVarianceResampler()
    injector = AlphaVariationInjector(map_borders=[0, len(reference)])

    return ParticleFilter(motion_model=motion_model,
                          measurement_strategy=measurement_model,
                          resampler=resampler,
                          injector=injector)


def setup_initial_particle_set() -> ParticleSet:
    particles = ParticleSet()
    for index in range(1000):
        state = State(position=0)
        particle = Particle(state=state, weight=0)
        particles.append(particle)
    return particles


def load_values(path: str) -> list:
    with open(path) as f:
        values_string = f.readline()
        values_list = values_string.split(", ")
        values_list = [float(x) for x in values_list]
        return values_list


def simulate_impedance(refdata: list) -> list:
    simulated_impedance = [random.normal(loc=refdata[0], scale=refdata[0] * 0.01)]
    for x in range(1, len(refdata)):
        simulated_impedance.append(random.normal(loc=refdata[x], scale=refdata[x] * 0.01))
    return simulated_impedance


def simulate_displacement(length: int) -> list:
    d = [0]
    for x in range(1, length):
        d.append(random.normal(loc=0.5, scale=0.01))
    return d


def simulate_reference(path: str) -> list:
    imp = np.load(path)
    return list(imp)


def simulate_position_groundtruth(length: int) -> list:
    gt = [x for x in range(length)]
    return gt


def display_simulation_results(grtruth: list, pfestimates: list):
    posest = []
    err = []

    for clusterPositionEstimate in pfestimates:
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


if __name__ == '__main__':
    data_vault_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\Bachelorarbeit\\Data\\Simulated " \
                      "Data\\data\\br1\\catheter_trajectory_original_simulated_signal.npy"

    ref = simulate_reference(data_vault_path)
    impedance = simulate_impedance(ref)
    groundtruth = simulate_position_groundtruth(len(impedance))
    displacements = simulate_displacement(len(impedance))

    """
    for i in range(int(len(displacements)/2), len(displacements)):
        displacements[i] = displacements[i]/2
    """

    for i in range(len(ref)):
        print("Reference= " + str(ref[i]) + "|  impedance= " + str(impedance[i]) + "|  displacements= " + str(
            displacements[i]) + "|  groundtruth= " + str(groundtruth[i]))

    position_estimate = []

    model = setup_model(reference=ref)
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

    display_simulation_results(groundtruth, position_estimate)
