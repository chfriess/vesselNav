import logging
import random
from collections import OrderedDict
from statistics import mean

import numpy as np
from scipy.stats import sem
from sklearn.cluster import DBSCAN

from filter.particle_filter import ParticleFilter
from injectors.alpha_variance_injector import AlphaVariationInjector
from injectors.random_particle_injector import RandomParticleInjector
from measurement_models.ahistoric_measurement_model import AhistoricMeasurementModel
from measurement_models.sliding_dtw_measurement_model import SlidingDTWMeasurementModel
from motion_models.motion_model import MotionModel
from resamplers.low_variance_resampler import LowVarianceResampler
from utils.cluster_position_estimate import ClusterPositionEstimate
from utils.multidimensional_cluster_position_estimate import MultidimensionalClusterPositionEstimate
from particles.particle import Particle
from utils.particle_filter_component_enums import MeasurementType, InjectorType
from utils.particle_set import ParticleSet
from utils.position_estimate import PositionEstimate
from particles.sliding_particle import SlidingParticle
from particles.state import State


class VesselSegment:
    def __init__(self, branch_id: int, parent_id: int, pf: ParticleFilter):
        self.branch_id = branch_id
        self.parent = parent_id,
        self.children = [],
        self.pf = pf
        self.particles = ParticleSet()

    def update(self, displacement: float, impedance: float):
        self.particles = self.pf.filter(previous_particle_set=self.particles,
                                        displacement_measurement=displacement,
                                        impedance_measurement=impedance)

    def get_number_of_particles(self):
        return len(self.particles)

    def get_positions_of_particles(self) -> list:
        return [particle.state.position for particle in self.particles]

    def pop_out_of_range_particles(self):
        underflowed_particles = []
        overflowed_particles = []
        for particle in self.particles:
            if particle.state.position < 0:
                underflowed_particles.append(particle)
                self.particles.remove(particle=particle)
                continue
            if particle.state.position > len(self.pf.get_reference()):
                overflowed_particles.append(particle)
                self.particles.remove(particle=particle)
        return underflowed_particles, overflowed_particles

    def get_length_of_segment(self):
        return len(self.pf.get_reference())

    def add_particle(self, particle: Particle):
        self.particles.append(particle=particle)

    def get_children(self):
        return self.children


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

    def get_index_of_vessel_with_most_particles(self) -> int:
        biggest_vessel_index = 0
        for i in range(len(self.vessels)):
            if self.vessels[i].get_number_of_particles() > self.vessels[biggest_vessel_index].get_number_of_particles():
                biggest_vessel_index = i
        return biggest_vessel_index

    def redistribute_particles_to_correct_segment(self):
        for vessel in self.vessels:
            underflowed_particles, overflowed_particles = vessel.pop_out_of_range_particles()
            for particle in underflowed_particles:
                child = random.choice(vessel.get_children())
                particle.state.position = particle.state.position + child.get_length_of_segment()
                child.add_particle(particle=particle)
            for particle in overflowed_particles:
                particle.state.position = particle.state.position - vessel.get_length_of_segment()
                random.choice(vessel.get_children()).add_particle(particle=particle)

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
                        initial_position_variance: float = 0.0,
                        alpha_center: float = 2.0,
                        alpha_variance: float = 0.1):

        if self.vessel_tree.vessel_count == 0:
            raise ValueError("You must initialize the vessel tree before initializing the particles")
        particles = ParticleSet()
        logging.info("Number of particles = " + str(number_of_particles))
        logging.info("initial position =  " + str(initial_position_center) + " +/- " + str(initial_position_variance))
        logging.info("alpha = " + str(alpha_center) + " +/- " + str(alpha_variance) + "\n\n")

        if isinstance(self.measurement_strategy, AhistoricMeasurementModel):
            for index in range(number_of_particles):
                state = State()
                state.assign_random_position(center=initial_position_center, variance=initial_position_variance)
                state.assign_random_alpha(center=alpha_center, variance=alpha_variance)
                particle = Particle(state=state, weight=0)
                particles.append(particle)
        if isinstance(self.measurement_strategy, SlidingDTWMeasurementModel):
            for index in range(number_of_particles):
                state = State()
                state.assign_random_position(center=initial_position_center, variance=initial_position_variance)
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

    @staticmethod
    def get_values_length(d):
        key, values = d
        return len(values)

    def estimate_current_position_dbscan_in_single_branch(self, positions) -> ClusterPositionEstimate:
        """
        positions = [particle.state.position for particle in
                     self.particles]
        """
        reshaped_positions = np.reshape(positions, (-1, 1))
        clustering1 = DBSCAN(eps=3, min_samples=2).fit(reshaped_positions)

        labels = clustering1.labels_
        cluster_indices = list(np.unique(labels))

        no_clusters = len(np.unique(labels))
        no_noise = int(np.sum(np.array(labels) == -1, axis=0))

        if -1 in cluster_indices:
            cluster_indices.remove(-1)
        d = {}
        for index in cluster_indices:
            d[index] = [y for (x, y) in list(zip(labels, positions)) if x == index]

        od = OrderedDict(sorted(d.items(), key=self.get_values_length, reverse=True))
        first_cluster = None
        second_cluster = None
        if len(od) > 0:
            first_cluster = PositionEstimate(mean(od[0]), sem(od[0]))
        if len(od) > 1:
            second_cluster = PositionEstimate(mean(od[1]), sem(od[1]))

        position_estimate = ClusterPositionEstimate(first_cluster=first_cluster, second_cluster=second_cluster,
                                                    number_of_clusters=no_clusters, number_of_noise=no_noise)

        return position_estimate

    def estimate_current_position_dbscan(self) -> MultidimensionalClusterPositionEstimate:
        index_of_vessel_with_most_particles = self.vessel_tree.get_index_of_vessel_with_most_particles()
        position_estimate = self.estimate_current_position_dbscan_in_single_branch(
            self.vessel_tree.vessels[index_of_vessel_with_most_particles].get_positions_of_particles())
        multidim_position_estimate = MultidimensionalClusterPositionEstimate(index_of_vessel_with_most_particles,
                                                                             position_estimate)
        logging.info("Best Position Estimate mean/sem = " + str(multidim_position_estimate) + "\n")
        return multidim_position_estimate
