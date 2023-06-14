from unittest import TestCase

from motion_models.motion_model import MotionModel3D
from particles.particle import Particle3D
from particles.state import State3D
from utils.particle_set import ParticleSet


class TestMotionModel3D(TestCase):
    def test_move_particles(self):
        map3D = Map3D()
        aorta_before = [1 / 20 for _ in range(70)]
        aorta_middle = [1 / 20 for _ in range(5)]
        aorta_after = [1 / 20 for _ in range(130)]

        renal_left = [1 / 15 for _ in range(100)]
        renal_right = [1 / 15 for _ in range(100)]
        iliaca_left = [1 / 10 for _ in range(100)]
        iliaca_right = [1 / 10 for _ in range(100)]

        map3D.add_vessel_impedance_prediction_as_millimeter_list(aorta_before, 0)
        map3D.add_vessel_impedance_prediction_as_millimeter_list(aorta_before, 1)
        map3D.add_vessel_impedance_prediction_as_millimeter_list(aorta_after, 2)

        map3D.add_mapping([0, 1])
        map3D.add_mapping([1, 2])

        motion_model = MotionModel3D(map3D)
        particles = ParticleSet()
        for _ in range(100):
            state = State3D()
            state.set_branch(2)
            state.assign_random_position(center=5, variance=0)
            state.assign_random_alpha(center=1, variance=0)
            particle = Particle3D(state=state, weight=0)
            particles.append(particle)

        for particle in particles:
            print(particle.get_position())

        print("___________________________________________\n\n")

        particles = motion_model.move_particles(particles, -20)

        for particle in particles:
            print(particle.get_position())

