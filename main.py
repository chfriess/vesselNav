import json
import math
import pickle
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


def evaluate_performance():
    performance_per_sample = {}
    error_per_sample = {}

    particle_numbers = [100, 200]

    SAMPLES = ["20", "25", "30", "31", "34"]
    for sample_nr in SAMPLES:
        reference_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\phantom_data_testing\\" + "smoothed_standardised_simulated_reference_agar.json"
        impedance_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\phantom_data_testing\\sample_" + sample_nr \
                         + "\\data_sample_" + sample_nr + "\\normalized_impedance_from_iliaca_without_plastic.npy"
        groundtruth_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\phantom_data_testing\\sample_" + sample_nr + \
                           "\\data_sample_" + sample_nr + "\\groundtruth_from_iliaca_without_plastic_offset_corrected.npy"
        displacement_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\phantom_data_testing\\sample_" + sample_nr \
                            + "\\data_sample_" + sample_nr + "\\displacements_from_iliaca_without_plastic.npy"
        destination_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\test\\performance\\AHISTORIC\\"

        displacements = np.load(displacement_path)
        impedance = np.load(impedance_path)
        groundtruth = np.load(groundtruth_path)

        navigator = VesselNavigator()

        performance = {}
        errors = {}
        for n in particle_numbers:
            navigator.setup_navigator(reference_path=reference_path,
                                      log_destination_path=destination_path,
                                      filename="performance",
                                      number_of_particles=n,
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
            estimates = [x for [x, y] in estimates]
            errors[n] = VesselNavigator.rms(signal=estimates, groundtruth=list(groundtruth[1:]))
        performance_per_sample[sample_nr] = performance
        error_per_sample[sample_nr] = errors

    average_performance = {}
    average_error = {}

    for n in particle_numbers:
        acc_performance = 0
        acc_errors = 0
        for sample_nr in SAMPLES:
            acc_performance += performance_per_sample[sample_nr][n]
            acc_errors += error_per_sample[sample_nr][n]
        average_performance[n] = acc_performance / len(SAMPLES)
        average_error[n] = acc_errors / len(SAMPLES)

    fig, ax = plt.subplots()
    ax.scatter(average_performance.keys(), average_performance.values(),  color="blue")
    ax.plot(average_performance.keys(), average_performance.values(), color="blue", label="performance")
    ax.set_ylabel("average time per execution step [s]")
    ax.set_xlabel("number of particles")
    plt.legend()

    ax2 = ax.twinx()
    ax2.scatter(average_performance.keys(), average_error.values(), color="red")
    ax2.plot(average_performance.keys(), average_error.values(), color="red", label="errors", )
    ax2.set_ylabel("average rms error from grountruth [mm]")

    plt.legend()

    destination_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\test\\performance\\AHISTORIC\\"
    plt.savefig(destination_path + "performance.svg")


    with open(destination_path + "performance per sample.pkl", 'wb') as f:
        pickle.dump(performance_per_sample, f)

    with open(destination_path + "error per sample.pkl", 'wb') as f:
        pickle.dump(error_per_sample, f)

    with open(destination_path + "errors per particle number.pkl", 'wb') as f:
        pickle.dump(average_error, f)

    with open(destination_path + "performance per particle number.pkl", 'wb') as f:
        pickle.dump(average_performance, f)


if __name__ == "__main__":
    evaluate_performance()
    """
    
    #SAMPLES = ["20", "25", "27", "29", "30", "31", "34", "35"]
    #SAMPLES = ["20", "25", "30", "31", "34"]
    #SAMPLES = ["30", "31", "34"]

    SAMPLES = ["39", "41", "42", "44", "45"]
    #SAMPLES = ["39"]
    PATH = "C:\\Users\\Chris\\OneDrive\\Desktop\\test_plastic\\"


    for sample_nr in SAMPLES:
        for measurement_model in MeasurementType:


            reference_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\phantom_data_testing\\" + "smoothed_standardised_simulated_reference_agar.json"
            impedance_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\phantom_data_testing\\sample_" + sample_nr \
                             + "\\data_sample_" + sample_nr + "\\normalized_impedance_from_iliaca_without_plastic.npy"
            groundtruth_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\phantom_data_testing\\sample_" + sample_nr + \
                               "\\data_sample_" + sample_nr + "\\groundtruth_from_iliaca_without_plastic_offset_corrected.npy"
            displacement_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\phantom_data_testing\\sample_" + sample_nr \
                                + "\\data_sample_" + sample_nr + "\\displacements_from_iliaca_without_plastic.npy"
            destination_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\test\\sample_" + sample_nr + "\\" + str(
                measurement_model.name) + "\\"

            reference_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\plastic coregistration data\\04_06_2023_BS\\smoothed_standardised_simulated_reference_plastic.json"
            impedance_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\plastic coregistration data\\04_06_2023_BS\\coregistration_" + sample_nr \
                             + "\\data_bioelectric_sensors" "\\normalized_impedance_from_iliaca_without_plastic.npy"
            groundtruth_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\plastic coregistration data\\04_06_2023_BS\\coregistration_" + sample_nr \
                               + "\\data_bioelectric_sensors" "\\groundtruth_from_iliaca_without_plastic_offset_corrected.npy"
            displacement_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\plastic coregistration data\\04_06_2023_BS\\coregistration_" + sample_nr \
                                + "\\data_bioelectric_sensors" "\\displacements_from_iliaca_without_plastic.npy"
            destination_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\test_plastic\\sample_" + sample_nr + "\\" + str(
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
                 {"REF_PATH": reference_path, "IMP_PATH": impedance_path,
                  "GRTRUTH_PATH": groundtruth_path, "BASE_PATH": destination_path})



    exec(open("C:\\Users\\Chris\\PycharmProjects\\data_analysis_scripts_BA\\prepare_for_statistics.py").read(),
         {"SAMPLES": SAMPLES, "PATH": PATH})

    exec(open("C:\\Users\\Chris\\PycharmProjects\\data_analysis_scripts_BA\\statistical_evaluation.py").read(),
         {"SAMPLES": SAMPLES, "PATH": PATH})

    """
