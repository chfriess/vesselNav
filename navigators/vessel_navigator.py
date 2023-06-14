import logging
from filter.model3D import Model3D
from navigators.navigator_interface import Navigator
from utils.position_estimate import PositionEstimate
from utils.particle_filter_component_enums import MeasurementType, InjectorType


class VesselNavigator(Navigator):

    def __init__(self, model: Model3D = None):
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
                        measurement_type: MeasurementType = MeasurementType.AHISTORIC,
                        injector_type: InjectorType = InjectorType.ALPHA_VARIANCE,
                        number_of_particles: int = 1000,
                        initial_branch: int = 0,
                        initial_position_center: float = 0,
                        initial_position_variance: float = 0.5,
                        alpha_center: float = 1.5,
                        alpha_variance: float = 0.1
                        ):
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

    def get_current_average_alpha(self):
        return self.model.get_current_average_alpha()

    def update_step(self, displacement: float, impedance: float) -> PositionEstimate:
        self.model.update_model(displacement=displacement, impedance=impedance)
        return self.model.estimate_current_position()
