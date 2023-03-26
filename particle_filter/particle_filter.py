from scipy import stats
from motion_model.motion_model import MotionModel
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

    def catheter_is_moving(self) -> bool:
        if len(self.displacement_history) < 5:
            return True
        test_result = stats.ttest_1samp(self.displacement_history[-5:], popmean=0)
        """
        if p value is smaller than 0.1, the average displacement is  significantly different from 0
        then, the catheter is moving 
        """
        return test_result[1] < 0.1

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
        if not self.catheter_is_moving():
            return previous_particle_set

        prediction_particle_set = self.motion_model.move_particles(
            previous_particle_set=previous_particle_set,
            displacement_measurement=displacement_measurement)

        weighted_particle_set = self.measurement_strategy.weight_particles(
            particles=prediction_particle_set,
            measurement=self.normalize_impedance(impedance_measurement=impedance_measurement,
                                                 displacement_measurement=displacement_measurement))

        resampled_particle_set = self.resampler.resample(weighted_particle_set)
        return self.injector.inject(resampled_particle_set)
