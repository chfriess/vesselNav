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
        self.alpha_center = 1

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
                                   cumulative_displacement: list,
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

        x = [p for p in range(len(grtruth))]
        y = [l for l in range(len(posest))]
        d = [z for z in range(len(cumulative_displacement))]

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
                                        cumulative_displacement=cumulative_displacements,
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
        ref = self.normalize_values(self.load_values(reference_path))
        #ref = self.normalize_values(self.generate_reference())

        print("LOADING IMPEDANCE FROM: " + impedance_path)
        impedance = self.normalize_values(self.load_values(impedance_path))

        print("LOADING GROUNDTRUTH FROM: " + groundtruth_path)
        groundtruth = self.load_values(groundtruth_path)
        # correcting the offset between
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
                              inital_position_variance=initial_position_variance,
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


if __name__ == "__main__":

    estimator = PostHocEstimator()

    # samples = ["20", "25", "27", "29", "30", "31", "34", "35"]
    # samples = ["54", "44", "46", "55", "56", "57", "59"]
    samples = [str(x) for x in range(39, 60)]
    for sample_nr in samples:
        print("[STARTING TO CALCULATE POST HOC PATH FOR SAMPLE " + sample_nr + "] \n\n")

        #base_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\phantom_data_testing\\"

        ref_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\plastic coregistration data\\04_06_2023_BS\\"+ "reference.npy"
        imp_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\plastic coregistration data\\04_06_2023_BS\\coregistration_" + sample_nr + "\\data_bioelectric_sensors"+ "\\impedance_interpolated_" + sample_nr + ".npy"
        grtruth_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\plastic coregistration data\\04_06_2023_BS\\coregistration_" + sample_nr + "\\data_bioelectric_sensors"+"\\em_interpolated_" + sample_nr + ".npy"
        displace_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\plastic coregistration data\\04_06_2023_BS\\coregistration_" + sample_nr + "\\data_bioelectric_sensors"+"\\displacements_interpolated_" + sample_nr + ".npy"

        dest_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\plastic coregistration data\\04_06_2023_BS\\coregistration_" + sample_nr + "\\results_sample_"+ sample_nr + "\\"
        file = "phantom_sample_" + sample_nr

        estimator.estimate_post_hoc_catheter_trajectory(reference_path=ref_path,
                                                        impedance_path=imp_path,
                                                        groundtruth_path=grtruth_path,
                                                        displacements_path=displace_path,
                                                        destination_path=dest_path,
                                                        filename=file,
                                                        number_of_particles=1000,
                                                        initial_position_variance=0.1,
                                                        alpha_center=1,
                                                        alpha_variance=0.1,
                                                        offset_groundtruth_bioelectric=3,
                                                        measurement_type=MeasurementType.AHISTORIC,
                                                        injector_type=InjectorType.ALPHA_VARIANCE)
        print("[FINISHED CALCULATING POST HOC PATH FOR SAMPLE " + sample_nr + "] \n\n")
