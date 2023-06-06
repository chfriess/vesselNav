import statistics

from scipy import stats

from motion_models.motion_model import MotionModel
from strategies.injection_strategy import InjectionStrategy
from strategies.measurement_strategy import MeasurementStrategy
from strategies.resampling_strategy import ResamplingStrategy
from utils.particle_set import ParticleSet


class ParticleFilter:
    def __init__(self,
                 motion_model: MotionModel,
                 measurement_strategy: MeasurementStrategy,
                 resampler: ResamplingStrategy,
                 injector: InjectionStrategy) -> None:
        self.motion_model = motion_model
        self.measurement_strategy = measurement_strategy
        self.resampler = resampler
        self.injector = injector
        self.displacement_history = []
        self.impedance_history = []

    def get_reference(self):
        return self.measurement_strategy.get_reference()

    @staticmethod
    def normalize_impedance(displacement_measurement: float,
                            impedance_measurement: float) -> float:
        if displacement_measurement == 0:
            return impedance_measurement
        return impedance_measurement / abs(displacement_measurement)

    def filter(self,
               previous_particle_set: ParticleSet,
               displacement_measurement: float,
               impedance_measurement: float) -> ParticleSet:
        self.displacement_history.append(displacement_measurement)
        self.impedance_history.append(impedance_measurement)

        prediction_particle_set = self.motion_model.move_particles(
            previous_particle_set=previous_particle_set,
            displacement_measurement=displacement_measurement)

        weighted_particle_set = self.measurement_strategy.weight_particles(
            particles=prediction_particle_set,
            measurement=impedance_measurement)

        resampled_particle_set = self.resampler.resample(weighted_particle_set)
        return self.injector.inject(resampled_particle_set)
