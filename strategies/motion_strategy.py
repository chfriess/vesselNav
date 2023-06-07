from abc import abstractmethod
from utils.particle_set import ParticleSet
from scipy.stats import sem


class MotionStrategy:

    @abstractmethod
    def move_particles(self, previous_particle_set: ParticleSet,
                       displacement_measurement: float) -> ParticleSet:
        raise NotImplementedError

    @staticmethod
    def calculate_displacement_error(displacements: list, included_measurements: int = 0):
        if len(displacements) < 2:
            return 0.3
        elif included_measurements <= 1 or included_measurements >= len(displacements):
            return sem(displacements)
        else:
            last_index = len(displacements) - 1
            return sem(displacements[(last_index - included_measurements):last_index])

