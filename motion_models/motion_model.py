from numpy import random
from scipy.stats import sem

from map.map import VesselTreeMap
from utils.particle_set import ParticleSet


class MotionModel:

    def __init__(self, vessel_tree: VesselTreeMap, included_measurements: int = 10):
        if included_measurements < 1:
            raise ValueError("number of included measurements cannot be smaller than 1")
        self.included_measurements = included_measurements
        self.displacement_history = []
        self.vessel_tree = vessel_tree


    @staticmethod
    def calculate_displacement_error(displacements: list, included_measurements: int = 0):
        if len(displacements) < 2:
            return 0.3
        elif included_measurements <= 1 or included_measurements >= len(displacements):
            return sem(displacements)
        else:
            last_index = len(displacements) - 1
            return sem(displacements[(last_index - included_measurements):last_index])

    def move_particles(self, previous_particle_set: ParticleSet,
                       displacement_measurement: float) -> ParticleSet:

        self.displacement_history.append(displacement_measurement)
        error = self.calculate_displacement_error(self.displacement_history)

        for particle in previous_particle_set:
            position_update = particle.state.get_position().get_branch() \
                              + (displacement_measurement * particle.state.alpha)  # TODO: change to vessel tree position estimate
            position_update = random.normal(loc=position_update, scale=error)

            self.vessel_tree.update_position(displacement=position_update,
                                             position=particle.state.get_position())
        return previous_particle_set
