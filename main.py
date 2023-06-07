from estimators.post_hoc_estimator import PostHocEstimator
from utils.particle_filter_component_enums import MeasurementType, InjectorType

if __name__ == "__main__":

    estimator = PostHocEstimator()
    samples = ["20", "25", "27", "29", "30", "31", "34", "35"]  # samples for agar phantom

    # samples = [str(x) for x in range(39, 60)]  # samples for plastic phantom
    for sample_nr in samples:
        print("[STARTING TO CALCULATE POST HOC PATH FOR SAMPLE " + sample_nr + "] \n\n")
        """
        PLASTIC PHANTOM PATHS

        ref_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\plastic coregistration data\\04_06_2023_BS\\"+ "reference.npy"
        imp_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\plastic coregistration data\\04_06_2023_BS\\coregistration_" 
        + sample_nr + "\\data_bioelectric_sensors"+ "\\impedance_interpolated_" + sample_nr + ".npy"
        grtruth_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\plastic coregistration data\\04_06_2023_BS\\
        coregistration_" + sample_nr + "\\data_bioelectric_sensors"+"\\em_interpolated_" + sample_nr + ".npy"
        displace_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\plastic coregistration data\\04_06_2023_BS\\
        coregistration_" + sample_nr + "\\data_bioelectric_sensors"+"\\displacements_interpolated_" + sample_nr + ".npy"

        dest_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\plastic coregistration data\\04_06_2023_BS\\coregistration_"
         + sample_nr + "\\results_sample_"+ sample_nr + "\\"
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
                                                        injector_type=InjectorType.ALPHA_VARIANCE)
        print("[FINISHED CALCULATING POST HOC PATH FOR SAMPLE " + sample_nr + "] \n\n")
