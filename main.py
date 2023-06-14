import json
import math
import os
import time
from statistics import mean

import numpy as np
from matplotlib import pyplot as plt
import logging

from scipy.stats import sem

from navigators.post_hoc_vessel_navigator import PostHocVesselNavigator
from navigators.vessel_navigator import VesselNavigator
from utils.particle_filter_component_enums import MeasurementType, InjectorType, MapType


def rms(signal: list, groundtruth: list) -> float:
    if len(signal) != len(groundtruth):
        raise ValueError("signal and groundtruth must be of same length for rms calculation")
    acc = 0
    for i in range(len(groundtruth)):
        acc += math.pow((signal[i] - groundtruth[i]), 2)
    return math.sqrt(acc / len(groundtruth))


def posthoc_run_3D_vessel_navigator(ref_path: str,
                                    imp_path: str,
                                    grtruth_path: str,
                                    displace_path: str,
                                    dest_path: str,
                                    filename: str):
    navigator = VesselNavigator()
    navigator.setup_navigator(reference_path=ref_path,
                              log_destination_path=dest_path,
                              filename=filename,
                              map_type=MapType.MAP_3D,
                              alpha_center=2,
                              initial_position_center=30
                              )

    impedance = np.load(imp_path)
    displacements = np.load(displace_path)
    grtruth = np.load(grtruth_path)

    positions = {}
    particles_per_step = {}
    clusters_per_step = {}
    alpha_estimates = []

    posest = []
    err = []

    posest_2 = []
    err_2 = []

    for i in range(len(impedance)):
        estimate = navigator.update_step(displacement=displacements[i], impedance=impedance[i])
        alpha_estimates.append(navigator.get_current_average_alpha())
        particles = navigator.get_current_particle_set()
        particles_per_step[i] = []
        positions[i] = estimate.get_first_cluster_mean()
        clusters_per_step[i] = estimate.get_clusters()
        posest.append(estimate.get_first_cluster_mean()[0])

        err.append(estimate.get_first_cluster_error())
        posest_2.append(estimate.get_second_cluster_mean()[0])

        err_2.append(estimate.get_second_cluster_error())
        print("[UPDATE STEP] " + str(i) + ": " + str(positions[i]))
        print("[FIRST CLUSTER MEAN] =" + str(estimate.get_first_cluster_mean()[0]))
        print("[SECOND CLUSTER MEAN] =" + str(estimate.get_second_cluster_mean()[0]))
        print("\n\n")

        for particle in particles:
            pos = particle.get_position()["displacement"]
            branch = particle.get_position()["branch"]
            particles_per_step[i].append([branch, pos])

    # save particles per step
    jo = json.dumps(particles_per_step, indent=4)

    with open(dest_path + "particles_per_step.json", "w") as outfile:
        outfile.write(jo)

    # save positions per step
    jo2 = json.dumps(positions, indent=4)

    with open(dest_path + "positions.json", "w") as outfile2:
        outfile2.write(jo2)

    #jo3 = json.dumps(clusters_per_step, indent=4)

    # save all clusters
    #with open(dest_path + "clusters.json", "w") as outfile3:
        #outfile2.write(jo3)

    np.save(dest_path + "best cluster means", np.array(posest))
    np.save(dest_path + "best cluster variances", np.array(err))

    np.save(dest_path +"second best cluster means", np.array(posest_2))
    np.save(dest_path +"second best cluster variances", np.array(err_2))

    np.save(dest_path +"alpha estimates", np.array(alpha_estimates))



    acc = []
    for index in range(len(positions)):
        acc.append(positions[index][0] - grtruth[1:][index])

    np.save(dest_path + "pf estimate errors from groundtruth", np.array(acc))

    logging.info(
        "final difference estimate vs. groundtruth = " + str(grtruth[-1] - posest[-1]))
    logging.info("Mean absolute deviation of PF estimate from groundtruth in mm = " + str(mean(acc)))
    logging.info("Sem of Mean absolute deviation of PF estimate from groundtruth in mm = " + str(sem(acc)))
    logging.info("Mean particle dispersion at each time step as sem of dominant cluster = " + str(sem(err)))



def evaluate_performance():
    samples = ["44"]
    sample_nr = "44"
    ref_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\plastic coregistration data\\04_06_2023_BS\\" + "reference_for_plastic_from_iliaca.npy"
    imp_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\plastic coregistration data\\04_06_2023_BS\\coregistration_" + sample_nr + "\\data_bioelectric_sensors" + "\\impedance_from_iliaca.npy"
    grtruth_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\plastic coregistration data\\04_06_2023_BS\\coregistration_" + sample_nr + "\\data_bioelectric_sensors" + "\\groundtruth_shifted_from_iliaca.npy"
    displace_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\plastic coregistration data\\04_06_2023_BS\\coregistration_" + sample_nr + "\\data_bioelectric_sensors" + "\\displacements_from_iliaca.npy"

    displacements = np.load(displace_path)
    impedance = np.load(imp_path)
    groundtruth = np.load(grtruth_path)

    dest_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\"
    file = "phantom_sample_" + sample_nr
    navigator = VesselNavigator()

    performance = {}
    errors = {}
    for n in range(100, 1100, 100):
        navigator.setup_navigator(reference_path=ref_path,
                                  log_destination_path=dest_path,
                                  filename=file,
                                  number_of_particles=1000,
                                  initial_position_variance=0.1,
                                  alpha_center=2,
                                  alpha_variance=0.1,
                                  measurement_type=MeasurementType.AHISTORIC,
                                  injector_type=InjectorType.RANDOM_PARTICLE
                                  )
        acc = 0
        clusters = []
        for i in range(len(displacements)):
            start = time.time()
            clusters.append(navigator.update_step(displacement=displacements[i], impedance=impedance[i]))
            end = time.time()
            acc = end - start
        estimates = [x.get_first_cluster_mean() for x in clusters]
        performance[n] = acc / len(displacements)
        errors[n] = rms(estimates, list(groundtruth[1:]))

    plt.plot(errors.keys(), errors.values())
    plt.figure(1)
    plt.plot(performance.keys(), performance.values())
    # np.savez("errors per particle number", errors)
    # np.savez("performance per particle number", performance)


def calculate_post_hoc_accuracy():
    estimator = PostHocVesselNavigator()
    # samples = ["20", "25", "27", "29", "30", "31", "34", "35"]  # samples for agar phantom

    # samples = [str(x) for x in range(39, 60)]  # samples for plastic phantom
    samples = ["44"]
    for sample_nr in samples:
        print("[STARTING TO CALCULATE POST HOC PATH FOR SAMPLE " + sample_nr + "] \n\n")

        # PLASTIC PHANTOM PATHS

        ref_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\plastic coregistration data\\04_06_2023_BS\\" + "reference_for_plastic_from_iliaca.npy"
        imp_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\plastic coregistration data\\04_06_2023_BS\\coregistration_" + sample_nr + "\\data_bioelectric_sensors" + "\\impedance_from_iliaca.npy"
        grtruth_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\plastic coregistration data\\04_06_2023_BS\\coregistration_" + sample_nr + "\\data_bioelectric_sensors" + "\\groundtruth_shifted_from_iliaca.npy"
        displace_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\plastic coregistration data\\04_06_2023_BS\\coregistration_" + sample_nr + "\\data_bioelectric_sensors" + "\\displacements_from_iliaca.npy"

        dest_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\plastic coregistration data\\04_06_2023_BS\\coregistration_" + sample_nr + "\\results_sample_" + sample_nr + "\\"
        """
        ref_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\phantom_data_testing\\" + "reference_from_iliaca.npy"
        imp_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\phantom_data_testing\\sample_" + sample_nr + "\\data_sample_" \
                   + sample_nr + "\\impedance_from_iliaca.npy"
        grtruth_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\phantom_data_testing\\sample_" + sample_nr + \
                       "\\data_sample_" + sample_nr + "\\groundtruth_from_iliaca.npy"
        displace_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\phantom_data_testing\\sample_" + sample_nr \
                        + "\\data_sample_" + sample_nr + "\\displacements_from_iliaca.npy"
        dest_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\phantom_data_testing\\sample_" + sample_nr \
                    + "\\results_sample_" + sample_nr + "\\"
         """
        file = "phantom_sample_" + sample_nr

        estimator.estimate_post_hoc_catheter_trajectory(reference_path=ref_path,
                                                        impedance_path=imp_path,
                                                        groundtruth_path=grtruth_path,
                                                        displacements_path=displace_path,
                                                        destination_path=dest_path,
                                                        filename=file,
                                                        number_of_particles=1000,
                                                        initial_position_variance=0.1,
                                                        alpha_center=2,
                                                        alpha_variance=0.1,
                                                        offset_groundtruth_bioelectric=-3,
                                                        measurement_type=MeasurementType.AHISTORIC,
                                                        injector_type=InjectorType.RANDOM_PARTICLE)
        print("[FINISHED CALCULATING POST HOC PATH FOR SAMPLE " + sample_nr + "] \n\n")


if __name__ == "__main__":
    sample_nr = "20"
    ref_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\phantom_data_testing\\" + "reference_from_iliaca.npy"
    imp_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\phantom_data_testing\\sample_" + sample_nr + "\\data_sample_" \
               + sample_nr + "\\impedance_from_iliaca.npy"
    grtruth_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\phantom_data_testing\\sample_" + sample_nr + \
                   "\\data_sample_" + sample_nr + "\\groundtruth_from_iliaca.npy"
    displace_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\phantom_data_testing\\sample_" + sample_nr \
                    + "\\data_sample_" + sample_nr + "\\displacements_from_iliaca.npy"
    dest_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\"
    posthoc_run_3D_vessel_navigator(ref_path=ref_path,
                                    imp_path=imp_path,
                                    grtruth_path=grtruth_path,
                                    displace_path=displace_path,
                                    dest_path=dest_path,
                                    filename="test")
