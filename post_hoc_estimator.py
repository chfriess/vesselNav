import csv
import matplotlib
from matplotlib import pyplot as plt
import logging
import time
from scipy.stats import sem
from statistics import mean
import os
from filter.model import Model
import numpy as np
import tkinter as tk
from tkinter import filedialog, simpledialog
from tkinter import messagebox

from utils.measurement_model_type_enum import MeasurementType


def load_values(path: str):
    values = np.load(path)
    return list(values)


def open_user_dialog():
    application_window = tk.Tk()
    ask_filename_button = tk.Button(application_window,
                                    text="select reference as npy file",
                                    command=ask_reference)
    ask_filename_button.pack()
    application_window.mainloop()


def ask_reference():
    filename = filedialog.askopenfilename()
    filename = filename.replace("/", "\\\\")
    print(filename)


def ask_source_directory():
    application_window = tk.Tk()

    source_directory = filedialog.askdirectory(parent=application_window,
                                               initialdir=os.getcwd(),
                                               title="Please select a folder:")
    source_directory = source_directory.replace("/", "\\\\") + "\\\\"
    return source_directory


def ask_destination_directory():
    root = tk.Tk()
    root.withdraw()

    messagebox.showinfo("Information", "Please select destination directory")
    destination_directory = filedialog.askdirectory()
    destination_directory = destination_directory.replace("/", "\\\\") + "\\\\"
    return destination_directory


def save_figures_with_metadata(pfestimates: list,
                               grtruth: list,
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

    font = {'family': 'normal',
            'size': 14}

    matplotlib.rc('font', **font)

    plt.plot(x, grtruth, color="black", label="groundtruth")
    plt.plot(y, posest, color="blue", label="first cluster")
    plt.errorbar(y, posest, yerr=err, ls="None", color="blue", capsize=2, elinewidth=0.5, capthick=0.5)
    plt.scatter(y, posest, color="blue", s=2)

    if posest_2:
        plt.plot(y, posest_2, color="green", label="second cluster")
        plt.errorbar(y, posest_2, yerr=err_2, ls="None", color="green", capsize=2, elinewidth=0.5, capthick=0.5)
        plt.scatter(y, posest_2, color="green", s=2)

    plt.legend()
    plt.xlabel("update steps [update frequency 10Hz]")
    plt.ylabel("cumulative displacement in mm")
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


def calculate_and_save_trajectory_as_csv(displacements: list,
                                         impedance: list,
                                         groundtruth: list,
                                         model: Model,
                                         destination_path: str,
                                         filename: str):
    position_estimates = []
    length = len(displacements) if len(displacements) < len(impedance) else len(impedance)
    position_estimates.append(model.estimate_current_position_dbscan())
    print("START POST HOC ESTIMATION \n")
    with open(destination_path + filename + "_results.csv", 'w') as file:
        writer = csv.writer(file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
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
            logging.info("Groundtruth = " + str(groundtruth[i]))
            start = time.time()
            model.update_model(displacement=displacements[i],
                               impedance=impedance[i])
            end = time.time()
            position_estimate = model.estimate_current_position_dbscan()
            position_estimates.append(position_estimate)
            print("Best position estimate cluster: " + str(position_estimates[i]))
            writer.writerow([str(i + 1),
                             str(displacements[i]),
                             str(impedance[i]),
                             str(groundtruth[i]),
                             str(position_estimate.get_first_cluster_mean() - groundtruth[i]),
                             str(position_estimate.get_first_cluster_mean()),
                             str(position_estimate.get_first_cluster_error()),
                             str(position_estimate.get_second_cluster_mean()),
                             str(position_estimate.get_second_cluster_error()),
                             str(position_estimate.number_of_clusters),
                             str(position_estimate.number_of_noise),
                             str(end - start)])

    save_figures_with_metadata(pfestimates=position_estimates,
                               grtruth=groundtruth,
                               path=destination_path)


def estimate_post_hoc_catheter_trajectory(reference_path: str,
                                          impedance_path: str,
                                          groundtruth_path: str,
                                          displacements_path: str,
                                          destination_path: str,
                                          filename: str,
                                          number_of_particles: int = 1000,
                                          initial_position_variance: float = 0.5,
                                          alpha_center: float = 1.5,
                                          alpha_variance: float = 0.1,
                                          measurement_type: MeasurementType = MeasurementType.AHISTORIC,
                                          ):
    print("LOADING REFERENCE FROM: " + base_path + reference_path)
    ref = load_values(base_path + reference_path)

    print("LOADING IMPEDANCE FROM: " + base_path + impedance_path)
    impedance = load_values(base_path + impedance_path)

    print("LOADING GROUNDTRUTH FROM: " + base_path + groundtruth_path)
    groundtruth = load_values(base_path + groundtruth_path)

    print("LOADING DISPLACEMENTS FROM: " + base_path + displacements_path)
    displacements = load_values(base_path + displacements_path)

    print("SETUP MODEL \n")
    model = Model()
    model.setup_logger(loglevel=logging.INFO,
                       log_directory=destination_path,
                       filename=filename + "_log")
    model.setup_particle_filter(reference=ref,
                                measurement_model=measurement_type)
    model.setup_particles(number_of_particles=number_of_particles,
                          initial_position_center=groundtruth[0],
                          inital_position_variance=initial_position_variance,
                          alpha_center=alpha_center,
                          alpha_variance=alpha_variance
                          )
    calculate_and_save_trajectory_as_csv(displacements=displacements,
                                         impedance=impedance,
                                         groundtruth=groundtruth,
                                         model=model,
                                         destination_path=destination_path,
                                         filename=filename)


if __name__ == "__main__":

    samples = ["27", "29",  "31"]
    for sample_nr in samples:
        print("[STARTING TO CALCULATE POST HOC PATH FOR SAMPLE " + sample_nr + "] \n\n")

        base_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\phantom_data_testing\\sample_" + \
                    sample_nr + "\\data_sample_" + sample_nr + "\\"

        ref_path = "reference.npy"
        imp_path = "impedance_cropped.npy"
        grtruth_path = "groundtruth_cropped.npy"
        displace_path = "displacements_cropped.npy"

        dest_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\phantom_data_testing\\sample_" + \
                    sample_nr + "\\results_sample_" + sample_nr + "\\"
        file = "phantom_sample_" + sample_nr

        estimate_post_hoc_catheter_trajectory(reference_path=ref_path,
                                              impedance_path=imp_path,
                                              groundtruth_path=grtruth_path,
                                              displacements_path=displace_path,
                                              destination_path=dest_path,
                                              filename=file,
                                              number_of_particles=1000,
                                              initial_position_variance=0.5,
                                              alpha_center=1.3,
                                              alpha_variance=0.1,
                                              measurement_type=MeasurementType.SLIDING_DTW)
        print("[FINISHED CALCULATING POST HOC PATH FOR SAMPLE " + sample_nr + "] \n\n")
