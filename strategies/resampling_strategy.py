from abc import abstractmethod
from utils.particle_set import ParticleSet


class ResamplingStrategy:
    @abstractmethod
    def resample(self, particles: ParticleSet) -> ParticleSet:
        raise NotImplementedError
