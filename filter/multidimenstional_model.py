import logging

from filter.particle_filter import ParticleFilter
from injectors.AlphaVarianceInjector import AlphaVariationInjector
from injectors.RandomParticleInjector import RandomParticleInjector
from measurement_models.ahistoric_measurement_model import AhistoricMeasurementModel
from measurement_models.sliding_dtw_measurement_model import SlidingDTWMeasurementModel
from motion_models.motion_model import MotionModel
from resamplers.low_variance_resampler import LowVarianceResampler
from utils.particle import Particle
from utils.particle_filter_component_enums import MeasurementType, InjectorType
from utils.particle_set import ParticleSet
from utils.sliding_particle import SlidingParticle
from utils.state import State


class VesselSegment:
    def __init__(self, branch_id: int, parent_id: int, pf: ParticleFilter):
        self.branch_id = branch_id
        self.parent = parent_id,
        self.children = [],
        self.pf = pf
        self.particles = ParticleSet()

    def update(self, displacement: float, impedance: float):
        self.pf.filter(displacement_measurement=displacement, impedance_measurement=impedance)


class VesselTree:
    def __init__(self):
        self.vessels = []
        self.vessel_count = 0

    def initialize_particles(self, particles: ParticleSet, initial_segment: int = 0):
        if initial_segment >= self.vessel_count:
            raise ValueError("Vessel Tree does not contain selected initial segment with id = " + str(initial_segment))
        self.vessels[initial_segment].particles = particles

    def add_vessel_segment(self, new_vessel: VesselSegment):
        self.vessels.append(new_vessel)
        self.vessels.sort(key=lambda e: e.branch_id, reverse=False)
        self.vessel_count += 1
        for vessel in self.vessels:
            if vessel.branch_id == new_vessel.parent:
                vessel.children.append(new_vessel.branch_id)

    def redistribute_particles_to_correct_segment(self):
        pass

    def update(self, displacement: float, impedance: float):
        for vessel in self.vessels:
            vessel.update(displacement, impedance)
        self.redistribute_particles_to_correct_segment()


class MultidimensionalModel:

    def __init__(self,
                 measurement_strategy: MeasurementType = MeasurementType.AHISTORIC,
                 injector_type: InjectorType = InjectorType.ALPHA_VARIANCE,

                 ) -> None:
        self.vessel_tree = VesselTree()
        self.update_steps = 1
        self.measurement_strategy = measurement_strategy,
        self.injector_type = injector_type

    def generate_particle_filter(self,
                                 reference: list,
                                 ) -> ParticleFilter:
        if self.injector_type == InjectorType.ALPHA_VARIANCE:
            injection_strategy = AlphaVariationInjector(map_borders=[0, len(reference)])
            logging.info("injector: alpha variance")
        elif self.injector_type == InjectorType.RANDOM_PARTICLE:
            injection_strategy = RandomParticleInjector(map_borders=[0, len(reference)])
            logging.info("injector: random particle")
        else:
            raise ValueError("Select a valid injection strategy: alpha variance or random particle")

        if self.measurement_strategy == MeasurementType.AHISTORIC:
            measurement_strategy = AhistoricMeasurementModel(reference_signal=reference)
            logging.info("measurement model: ahistoric")
        elif self.measurement_strategy == MeasurementType.SLIDING_DTW:
            measurement_strategy = SlidingDTWMeasurementModel(reference_signal=reference)
            logging.info("measurement model: sliding_dtw")
        else:
            raise ValueError("Select a valid measurement strategy: ahistoric or sliding_dtw")
        motion_model = MotionModel()
        resampling_strategy = LowVarianceResampler()

        return ParticleFilter(motion_model=motion_model,
                              measurement_strategy=measurement_strategy,
                              resampler=resampling_strategy,
                              injector=injection_strategy)

    def add_vessel_segment(self, reference: list, branch_id: int, parent_id: int):
        particle_filter = self.generate_particle_filter(reference=reference)
        new_vessel = VesselSegment(branch_id=branch_id,
                                   parent_id=parent_id,
                                   pf=particle_filter)
        self.vessel_tree.add_vessel_segment(new_vessel=new_vessel)

    def setup_particles(self,
                        number_of_particles: int = 1000,
                        initial_segment: int = 0,
                        initial_position_center: float = 0.0,
                        inital_position_variance: float = 0.0,
                        alpha_center: float = 2.0,
                        alpha_variance: float = 0.1):

        if self.vessel_tree.vessel_count == 0:
            raise ValueError("You must initialize the vessel tree before initializing the particles")
        particles = ParticleSet()
        logging.info("Number of particles = " + str(number_of_particles))
        logging.info("initial position =  " + str(initial_position_center) + " +/- " + str(inital_position_variance))
        logging.info("alpha = " + str(alpha_center) + " +/- " + str(alpha_variance) + "\n\n")

        if isinstance(self.measurement_strategy, AhistoricMeasurementModel):
            for index in range(number_of_particles):
                state = State()
                state.assign_random_position(center=initial_position_center, variance=inital_position_variance)
                state.assign_random_alpha(center=alpha_center, variance=alpha_variance)
                particle = Particle(state=state, weight=0)
                particles.append(particle)
        if isinstance(self.measurement_strategy, SlidingDTWMeasurementModel):
            for index in range(number_of_particles):
                state = State()
                state.assign_random_position(center=initial_position_center, variance=inital_position_variance)
                particle = SlidingParticle(state=state, weight=0)
                particles.append(particle)
        self.vessel_tree.initialize_particles(particles=particles, initial_segment=initial_segment)

    def reset_model(self):
        self.update_steps = 1

    def update_model(self, displacement: float, impedance: float):
        logging.info("Update step #: " + str(self.update_steps))
        logging.info("Displacement measurement: " + str(displacement))
        logging.info("Impedance measurement: " + str(impedance))

        self.vessel_tree.update(displacement=displacement, impedance=impedance)

        self.update_steps += 1

    def estimate_current_position_dbscan(self):
        pass
