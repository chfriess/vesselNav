import math
import time

import numpy as np
from matplotlib import pyplot as plt

from estimators.online_estimator import OnlineEstimator
from estimators.post_hoc_estimator import PostHocEstimator
from utils.particle_filter_component_enums import MeasurementType, InjectorType



def rms(signal: list, groundtruth: list) -> float:
    if len(signal) != len(groundtruth):
        raise ValueError("signal and groundtruth must be of same length for rms calculation")
    acc = 0
    for i in range(len(groundtruth)):
        acc += math.pow((signal[i] - groundtruth[i]), 2)
    return math.sqrt(acc / len(groundtruth))

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
    estimator = OnlineEstimator()

    performance = {}
    errors = {}
    for n in range(100, 1100, 100):
        estimator.setup_model(reference_path=ref_path,
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
            clusters.append(estimator.update_step(displacement=displacements[i], impedance=impedance[i]))
            end = time.time()
            acc = end-start
        estimates = [x.get_first_cluster_mean() for x in clusters]
        performance[n] = acc/len(displacements)
        errors[n] = rms(estimates, list(groundtruth[1:]))

    plt.plot(errors.keys(), errors.values())
    plt.figure(1)
    plt.plot(performance.keys(), performance.values())
    #np.savez("errors per particle number", errors)
    #np.savez("performance per particle number", performance)


def calculate_post_hoc_accuracy():
    estimator = PostHocEstimator()
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
    calculate_post_hoc_accuracy()
