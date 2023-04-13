from tslearn.metrics import dtw
from strategies.measurement_strategy import MeasurementStrategy
from utils.particle_reference_retriever import ParticleReferenceRetriever
from utils.particle_set import ParticleSet


class SlidingDTWMeasurementModel(MeasurementStrategy):

    def __init__(self, reference_signal: list):  # TODO: change to vessel tree reference

        super().__init__()
        self.reference_signal = reference_signal  # TODO: change to vessel tree reference

        self.measurement_history = []
        self.particle_reference_retriever = ParticleReferenceRetriever()

    def raw_weight_particles(self, particles: ParticleSet, measurement: float) -> ParticleSet:
        self.measurement_history.append(measurement)
        if len(self.measurement_history) > 10:
            self.measurement_history = self.measurement_history[-10:]

        for particle in particles:
            particle.reference_history += self.particle_reference_retriever.retrieve_reference_update(
                particle, self.reference_signal)
            if len(particle.reference_history) > 10:
                particle.reference_history = particle.reference_history[-10:]
            particle.weight = dtw(self.measurement_history, particle.reference_history)
        return particles