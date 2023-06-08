import csv
import math
import statistics

import matplotlib
from matplotlib import pyplot as plt
import logging
import time
from scipy.stats import sem
from statistics import mean
import os
from filter.model import Model
import numpy as np
from utils.particle_filter_component_enums import MeasurementType, InjectorType


class PostHocEstimator:

    def __init__(self):
        self.alpha_center = 2

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
    def save_figures_with_metadata(pfestimates: list,
                                   grtruth: list,
                                   alpha_estimates: list,
                                   path: str):
        os.chdir(path)
        posest = []
        err = []

        posest_2 = []
        err_2 = []
        for clusterPositionEstimate in pfestimates:
            posest.append(clusterPositionEstimate.first_cluster.center)

            err.append(clusterPositionEstimate.first_cluster.error)

            if clusterPositionEstimate.second_cluster is not None:
                posest_2.append(clusterPositionEstimate.second_cluster.center)

                err_2.append(clusterPositionEstimate.second_cluster.error)
            else:
                posest_2.append(clusterPositionEstimate.first_cluster.center)
                err_2.append(clusterPositionEstimate.first_cluster.error)

        x = [index for index in range(len(grtruth))]
        y = [index for index in range(len(posest))]

        font = {'family': 'normal',
                'size': 14}

        matplotlib.rc('font', **font)

        # plt.plot(d, cumulative_displacement, color="orange", label="cumulative displacement")
        plt.plot(x, grtruth, color="black", label="groundtruth")
        plt.plot(y, posest, color="blue", label="first cluster")
        plt.errorbar(y, posest, yerr=err, ls="None", color="blue", capsize=2, elinewidth=0.5, capthick=0.5)
        plt.scatter(y, posest, color="blue", s=2)

        if posest_2:
            plt.plot(y, posest_2, color="green", label="second cluster")
            plt.errorbar(y, posest_2, yerr=err_2, ls="None", color="green", capsize=2, elinewidth=0.5, capthick=0.5)
            plt.scatter(y, posest_2, color="green", s=2)

        plt.legend()
        plt.xlabel("update steps ")
        plt.ylabel("displacement along centerline [mm]")
        plt.savefig("groundtruth vs. pf estimate.svg")
        np.save("best cluster means", np.array(posest))
        np.save("best cluster variances", np.array(err))

        np.save("second best cluster means", np.array(posest_2))
        np.save("second best cluster variances", np.array(err_2))

        np.save("alpha estimates", np.array(alpha_estimates))

        acc = []
        for index in range(len(grtruth)):
            acc.append(posest[index] - grtruth[index])

        np.save("pf estimate errors from groundtruth", np.array(acc))

        logging.info(
            "final difference estimate vs. groundtruth = " + str(grtruth[-1] - pfestimates[-1].first_cluster.center))
        logging.info("Mean absolute deviation of PF estimate from groundtruth in mm = " + str(mean(acc)))
        logging.info("Sem of Mean absolute deviation of PF estimate from groundtruth in mm = " + str(sem(acc)))
        logging.info("Mean particle dispersion at each time step as sem of dominant cluster = " + str(sem(err)))
        plt.clf()

    @staticmethod
    def calculate_and_save_trajectory_as_csv(self,
                                             displacements: list,
                                             impedance: list,
                                             groundtruth: list,
                                             model: Model,
                                             destination_path: str,
                                             filename: str):
        position_estimates = []
        alpha_estimates = []
        cumulative_displacements = []
        length = len(displacements) if len(displacements) < len(impedance) else len(impedance)
        position_estimates.append(model.estimate_current_position_dbscan())
        cumulative_displacements.append(groundtruth[0])
        print("START POST HOC ESTIMATION \n")
        devations_from_groundtruth = []
        with open(destination_path + filename + "_results.csv", 'w') as f:
            writer = csv.writer(f, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(
                ["Update step #",
                 "Displacement",
                 "Impedance",
                 "Groundtruth",
                 "Position estimate - Groundtruth",
                 "first cluster mean",
                 "first cluster error",
                 "second cluster mean",
                 "second cluster error",
                 "number of clusters",
                 "number of noise points",
                 "duration of update step"])
            for i in range(length):
                cumulative_displacements.append(cumulative_displacements[i] + displacements[i])
                logging.info("Groundtruth = " + str(groundtruth[i + 1]))
                start = time.time()
                model.update_model(displacement=displacements[i],
                                   impedance=impedance[i])
                end = time.time()
                position_estimate = model.estimate_current_position_dbscan()
                position_estimates.append(position_estimate)
                alpha_estimates.append(model.get_current_average_alpha())
                print("Best position estimate cluster: " + str(position_estimates[i]))
                devations_from_groundtruth.append(position_estimate.get_first_cluster_mean() - groundtruth[i + 1])
                writer.writerow([str(i + 1),
                                 str(displacements[i]),
                                 str(impedance[i]),
                                 str(groundtruth[i + 1]),
                                 str(position_estimate.get_first_cluster_mean() - groundtruth[i + 1]),
                                 str(position_estimate.get_first_cluster_mean()),
                                 str(position_estimate.get_first_cluster_error()),
                                 str(position_estimate.get_second_cluster_mean()),
                                 str(position_estimate.get_second_cluster_error()),
                                 str(position_estimate.number_of_clusters),
                                 str(position_estimate.number_of_noise),
                                 str(end - start)])

        self.save_figures_with_metadata(pfestimates=position_estimates,
                                        grtruth=groundtruth,
                                        alpha_estimates=alpha_estimates,
                                        path=destination_path)
        with open(destination_path + filename + "_rms.txt", 'w') as f:
            f.write("The rms value of the deviation of the best position estimate from the groundtruth is: \n")
            f.write(str(self.rms_of_deviations(deviations=devations_from_groundtruth)))
            f.write("\n\n")
            f.write("The rms value of the deviation of the displacement from the groundtruth is: \n")
            f.write(str(self.rms(signal=cumulative_displacements[1:], groundtruth=groundtruth[1:])))
            cumulative_displacements_transformed = [groundtruth[0]]
            for i in range(len(displacements)):
                cumulative_displacements_transformed.append(
                    displacements[i] * self.alpha_center + cumulative_displacements_transformed[i])
            f.write("\n\n")
            f.write(
                "The rms value of the deviation of the displacement multiplied with alpha from the groundtruth is: \n")
            f.write(str(self.rms(signal=cumulative_displacements_transformed[1:], groundtruth=groundtruth[1:])))

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

    def estimate_post_hoc_catheter_trajectory(self,
                                              reference_path: str,
                                              impedance_path: str,
                                              groundtruth_path: str,
                                              displacements_path: str,
                                              destination_path: str,
                                              filename: str,
                                              number_of_particles: int = 10000,
                                              initial_position_variance: float = 0.5,
                                              alpha_center: float = 2,
                                              alpha_variance: float = 0.1,
                                              offset_groundtruth_bioelectric=0.0,
                                              measurement_type: MeasurementType = MeasurementType.AHISTORIC,
                                              injector_type: InjectorType = InjectorType.ALPHA_VARIANCE
                                              ):
        self.alpha_center = alpha_center
        print("Alpha:" + str(self.alpha_center))
        print("LOADING REFERENCE FROM: " + reference_path)
        ref_raw = self.normalize_values(self.load_values(reference_path))
        ref = [self.predict_impedance_from_diameter(x) for x in ref_raw]
        kernel_size = 10
        kernel = np.ones(kernel_size) / kernel_size
        ref = list(np.convolve(ref, kernel, mode='same'))

        print("LOADING IMPEDANCE FROM: " + impedance_path)
        impedance = self.normalize_values(self.load_values(impedance_path))

        print("LOADING GROUNDTRUTH FROM: " + groundtruth_path)
        groundtruth = self.load_values(groundtruth_path)
        groundtruth = list(np.array(groundtruth) + offset_groundtruth_bioelectric)

        print("LOADING DISPLACEMENTS FROM: " + displacements_path)
        displacements = self.load_values(displacements_path)

        print("SETUP MODEL \n")
        model = Model()
        model.setup_logger(loglevel=logging.INFO,
                           log_directory=destination_path,
                           filename=filename + "_log")
        model.setup_particle_filter(reference=ref,
                                    measurement_model=measurement_type,
                                    injector_type=injector_type, alpha_center=alpha_center)
        model.setup_particles(number_of_particles=number_of_particles,
                              initial_position_center=groundtruth[0],
                              initial_position_variance=initial_position_variance,
                              alpha_center=alpha_center,
                              alpha_variance=alpha_variance
                              )
        self.calculate_and_save_trajectory_as_csv(self,
                                                  displacements=displacements,
                                                  impedance=impedance,
                                                  groundtruth=groundtruth,
                                                  model=model,
                                                  destination_path=destination_path,
                                                  filename=filename)
