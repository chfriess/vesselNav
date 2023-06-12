import json
import logging

import numpy as np
from matplotlib import pyplot as plt

from filter.model import Model
from filter.model3D import Model3D
from navigators.navigator_interface import Navigator
from particles.particle import Particle3D
from particles.state import State3D
from utils.map3D import Map3D
from utils.particle_set import ParticleSet
from utils.position_estimate import PositionEstimate
from utils.particle_filter_component_enums import MeasurementType, InjectorType, MapType


class VesselNavigator(Navigator):

    def __init__(self, model: Model = None):
        self.model = model
        self.impedance_normalizer = 1
        self.impedance_history = []

    def normalize_impedance(self, impedance: float) -> float:
        if len(self.impedance_history) <= 10:
            self.impedance_history.append(impedance)
            self.impedance_normalizer = sum(self.impedance_history) / len(self.impedance_history)
        return impedance / self.impedance_normalizer

    @staticmethod
    def normalize_reference(ref: list) -> list:
        if len(ref) < 10:
            normalizer = sum(ref) / len(ref)

        else:
            normalizer = sum(ref[:10] / 10)

        for i in range(len(ref)):
            ref[i] = ref[i] / normalizer

        return ref

    def setup_navigator(self,
                        reference_path: str,
                        log_destination_path: str,
                        filename: str,
                        map_type: MapType = MapType.MAP_1D,
                        measurement_type: MeasurementType = MeasurementType.AHISTORIC,
                        injector_type: InjectorType = InjectorType.ALPHA_VARIANCE,
                        number_of_particles: int = 1000,
                        initial_branch: int = 0,
                        initial_position_center: float = 0,
                        initial_position_variance: float = 0.5,
                        alpha_center: float = 1.5,
                        alpha_variance: float = 0.1
                        ):
        if map_type == MapType.MAP_1D:
            self.model = Model()
            self.model.setup_particle_filter(map_path=reference_path,
                                             measurement_model=measurement_type,
                                             injector_type=injector_type,
                                             alpha_center=alpha_center)
            self.model.setup_particles(number_of_particles=number_of_particles,
                                       initial_position_center=initial_position_center,
                                       initial_position_variance=initial_position_variance,
                                       alpha_center=alpha_center,
                                       alpha_variance=alpha_variance
                                       )

        else:
            self.model = Model3D()
            self.model.setup_particle_filter(map_path=reference_path,
                                             measurement_model=measurement_type,
                                             injector_type=injector_type,
                                             alpha_center=alpha_center)
            self.model.setup_particles(number_of_particles=number_of_particles,
                                       initial_position_center=initial_position_center,
                                       initial_position_variance=initial_position_variance,
                                       alpha_center=alpha_center,
                                       alpha_variance=alpha_variance,
                                       initial_branch=initial_branch
                                       )
        self.model.setup_logger(loglevel=logging.INFO,
                                log_directory=log_destination_path,
                                filename=filename + "_log")

    def get_current_particle_set(self):
        return self.model.get_particles()

    def update_step(self, displacement: float, impedance: float) -> PositionEstimate:
        self.model.update_model(displacement=displacement, impedance=impedance)
        return self.model.estimate_current_position()


if __name__ == "__main__":
    sample_nr = "30"
    ref_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\phantom_data_testing\\" + "reference_from_iliaca.npy"
    imp_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\phantom_data_testing\\sample_" + sample_nr + "\\data_sample_" \
               + sample_nr + "\\impedance_interpolated_" + sample_nr + ".npy"
    displace_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\phantom_data_testing\\sample_" + sample_nr \
                    + "\\data_sample_" + sample_nr + "\\displacements_interpolated_" + sample_nr + ".npy"
    dest_path = "C:\\Users\\Chris\\OneDrive\\Desktop\\"

    file = "phantom_sample_" + sample_nr



    particles = ParticleSet()

    for _ in range(1000):
        particles.append(Particle3D(State3D(position=0, branch=0, alpha=2)))

    navigator = VesselNavigator()
    navigator.setup_navigator(reference_path="",
                              log_destination_path=dest_path,
                              filename=file,
                              map_type=MapType.MAP_3D,
                              alpha_center=2,
                              initial_position_center=30
                              )

    impedance = np.load(imp_path)/100000
    displacements = np.load(displace_path)

    positions = {}
    particles_per_step = {}

    for i in range(len(impedance)):
        estimate = navigator.update_step(displacement=displacements[i], impedance=impedance[i])
        particles = navigator.get_current_particle_set()
        particles_per_step[i] = []
        positions[i] = estimate.get_first_cluster_mean()

        for particle in particles:
            pos = particle.get_position()["displacement"]
            branch = particle.get_position()["branch"]
            particles_per_step[i].append([branch, pos])


    jo = json.dumps(particles_per_step, indent=4)

    with open(dest_path+"particles_per_step.json", "w") as outfile:
        outfile.write(jo)

    jo2 = json.dumps(positions, indent=4)

    with open(dest_path + "positions.json", "w") as outfile2:
        outfile2.write(jo2)

"""
     
        1. Test, ob 3D model überhaupt funktioniert
         - generiere referenz 3D map, die einlesbar ist als map aus np datei
         - teste erst einmal einen update step, ob der überhaupt funktioniert; einfach mal immer position und branch
         printen, dann mal einen ganzen run
        
        2. Visualisierung
         - wie kann ich die partikel für jeden schritt so speicher, dass sie im visualisierungsskript geladen werden
         können?
         - wie soll ich die partikel dann für jeden updateschritt darstellen? kleiner film?
        """

