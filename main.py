import json
import math
import time
from statistics import mean
import numpy as np
from matplotlib import pyplot as plt
import logging
from scipy.stats import sem
from navigators.vessel_navigator import VesselNavigator
from utils.particle_filter_component_enums import MeasurementType, InjectorType


def rms(signal_one: list, signal_two: list) -> float:
    if len(signal_one) != len(signal_two):
        raise ValueError("signal and groundtruth must be of same length for rms calculation")
    acc = 0
    for i in range(len(signal_two)):
        acc += math.pow((signal_one[i] - signal_two[i]), 2)
    return math.sqrt(acc / len(signal_two))


def posthoc_run_3D_vessel_navigator(ref_path: str,
                                    imp_path: str,
                                    grtruth_path: str,
                                    displace_path: str,
                                    dest_path: str,
                                    filename: str,
                                    measurement_type: MeasurementType = MeasurementType.AHISTORIC,
                                    injector_type: InjectorType = InjectorType.ALPHA_VARIANCE,
                                    number_of_particles: int = 1000,
                                    initial_branch: int = 0,
                                    initial_position_center: float = 0,
                                    initial_position_variance: float = 0.5,
                                    alpha_center: float = 1.5,
                                    alpha_variance: float = 0.1):
    navigator = VesselNavigator()
    navigator.setup_navigator(reference_path=ref_path,
                              log_destination_path=dest_path,
                              filename=filename,
                              measurement_type=measurement_type,
                              injector_type=injector_type,
                              number_of_particles=number_of_particles,
                              initial_branch=initial_branch,
                              initial_position_center=initial_position_center,
                              initial_position_variance=initial_position_variance,
                              alpha_center=alpha_center,
                              alpha_variance=alpha_variance
                              )

    impedance = np.load(imp_path)
    displacements = np.load(displace_path)
    groundtruth = np.load(grtruth_path)

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

    """
    TODO: make Position3D Json serializable
    jo3 = json.dumps(clusters_per_step, indent=4)

    # save all clusters
    with open(dest_path + "clusters.json", "w") as outfile3:
        outfile3.write(jo3)
    """

    np.save(dest_path + "best cluster means", np.array(posest))
    np.save(dest_path + "best cluster variances", np.array(err))

    np.save(dest_path + "second best cluster means", np.array(posest_2))
    np.save(dest_path + "second best cluster variances", np.array(err_2))

    np.save(dest_path + "alpha estimates", np.array(alpha_estimates))

    acc = [0]
    cumulative_position_estimate = [groundtruth[0]]
    cumulative_displacements = [groundtruth[0]]
    cumulative_alpha_displacements = [groundtruth[0]]
    for index in range(len(positions)):
        acc.append(positions[index][0] - groundtruth[index])
        cumulative_position_estimate.append(positions[index][0])
        cumulative_displacements.append(cumulative_displacements[index] + displacements[index])
        cumulative_alpha_displacements.append(cumulative_alpha_displacements[index]
                                              + (alpha_center * displacements[index]))

    with open(dest_path + filename + "_rms.txt", 'w') as f:
        f.write("The rms value of the deviation of the best position estimate from the groundtruth is: \n")
        f.write(str(rms(signal_one=cumulative_position_estimate, signal_two=list(groundtruth))))
        f.write("\n\n")
        f.write("The rms value of the deviation of the displacement from the groundtruth is: \n")
        f.write(str(rms(signal_one=cumulative_displacements, signal_two=list(groundtruth))))
        cumulative_displacements_transformed = [groundtruth[0]]
        for i in range(len(displacements)):
            cumulative_displacements_transformed.append(
                displacements[i] * alpha_center + cumulative_displacements_transformed[i])
        f.write("\n\n")
        f.write(
            "The rms value of the deviation of the displacement multiplied with alpha from the groundtruth is: \n")
        f.write(str(rms(signal_one=cumulative_alpha_displacements, signal_two=list(groundtruth))))

    np.save(dest_path + "pf estimate errors from groundtruth", np.array(acc))

    logging.info(
        "final difference estimate vs. groundtruth = " + str(groundtruth[-1] - posest[-1]))
    logging.info("Mean absolute deviation of PF estimate from groundtruth in mm = " + str(mean(acc)))
    logging.info("Sem of Mean absolute deviation of PF estimate from groundtruth in mm = " + str(sem(acc)))
    logging.info("Mean particle dispersion at each time step as sem of dominant cluster = " + str(sem(err)))


def evaluate_performance(ref_path: str,
                         imp_path: str,
                         grtruth_path: str,
                         displace_path: str,
                         dest_path: str,
                         filename: str):
    displacements = np.load(displace_path)
    impedance = np.load(imp_path)
    groundtruth = np.load(grtruth_path)

    navigator = VesselNavigator()

    performance = {}
    errors = {}
    for n in range(100, 1100, 100):
        navigator.setup_navigator(reference_path=ref_path,
                                  log_destination_path=dest_path,
                                  filename=filename,
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
        errors[n] = VesselNavigator.rms(estimates, list(groundtruth[1:]))

    plt.plot(errors.keys(), errors.values())
    plt.figure(1)
    plt.plot(performance.keys(), performance.values())
    np.save(dest_path + "errors per particle number", errors)
    np.save(dest_path + "performance per particle number", performance)


if __name__ == "__main__":
    SAMPLES = ["20", "25", "27", "29", "30", "31", "34", "35"]
    PATH = "C:\\Users\\Chris\\OneDrive\\Desktop\\test\\"


    for sample_nr in SAMPLES:
        for measurement_model in MeasurementType:
            reference_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\phantom_data_testing\\" + "reference_from_iliaca.npy"
            impedance_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\phantom_data_testing\\sample_" + sample_nr \
                             + "\\data_sample_" + sample_nr + "\\impedance_from_iliaca.npy"
            groundtruth_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\phantom_data_testing\\sample_" + sample_nr + \
                               "\\data_sample_" + sample_nr + "\\groundtruth_from_iliaca.npy"
            displacement_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\phantom_data_testing\\sample_" + sample_nr \
                                + "\\data_sample_" + sample_nr + "\\displacements_from_iliaca.npy"
            destination_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\test\\sample_" + sample_nr + "\\" + str(
                measurement_model.name) + "\\"
            groundtruth = np.load(groundtruth_path)
            posthoc_run_3D_vessel_navigator(ref_path=reference_path,
                                            imp_path=impedance_path,
                                            grtruth_path=groundtruth_path,
                                            displace_path=displacement_path,
                                            dest_path=destination_path,
                                            measurement_type=measurement_model,
                                            filename=sample_nr,
                                            alpha_center=2,
                                            initial_position_center=groundtruth[0],
                                            initial_branch=0)
            print("Finished for " + sample_nr + " run of " + str(measurement_model.name))

    exec(open("C:\\Users\\Chris\\PycharmProjects\\data_analysis_scripts_BA\\plot_result_figures.py").read(),
         {"SAMPLES": SAMPLES, "PATH": PATH})
    exec(open("C:\\Users\\Chris\\PycharmProjects\\data_analysis_scripts_BA\\prepare_for_statistics.py").read(),
         {"SAMPLES": SAMPLES, "PATH": PATH})

    exec(open("C:\\Users\\Chris\\PycharmProjects\\data_analysis_scripts_BA\\statistical_evaluation.py").read(),
         {"SAMPLES": SAMPLES, "PATH": PATH})
