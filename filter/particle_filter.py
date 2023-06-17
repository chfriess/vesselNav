from strategies.injection_strategy import InjectionStrategy
from strategies.measurement_strategy import MeasurementStrategy
from strategies.motion_strategy import MotionStrategy
from strategies.resampling_strategy import ResamplingStrategy
from utils.particle_set import ParticleSet


class ParticleFilter:
    def __init__(self,
                 motion_model: MotionStrategy,
                 measurement_strategy: MeasurementStrategy,
                 resampler: ResamplingStrategy,
                 injector: InjectionStrategy) -> None:
        self.motion_model = motion_model
        self.measurement_strategy = measurement_strategy
        self.resampler = resampler
        self.injector = injector

    def get_reference(self):
        return self.measurement_strategy.get_reference()  # TODO add Return value and do I even need it?

    def filter(self,
               previous_particle_set: ParticleSet,
               displacement_measurement: float,
               impedance_measurement: float) -> ParticleSet:
        prediction_particle_set = self.motion_model.move_particles(
            previous_particle_set=previous_particle_set,
            displacement_measurement=displacement_measurement)

        weighted_particle_set = self.measurement_strategy.weight_particles(
            particles=prediction_particle_set,
            measurement=impedance_measurement)

        resampled_particle_set = self.resampler.resample(weighted_particle_set)
        injected_particle_set = self.injector.inject(resampled_particle_set)
        return injected_particle_set
