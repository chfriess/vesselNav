from unittest import TestCase

from particles.particle import SlidingParticle3D
from particles.state import State3D
from utils.map3D import Map3D
from utils.particle_reference_retriever import CroppingParticleReferenceRetriever


class TestParticleReferenceRetriever3D(TestCase):
    def test_retrieve_reference_update(self):
        map3D = Map3D()

        aorta_before = [1 / 20 for _ in range(70)]
        aorta_after = [1 / 20 for _ in range(130)]
        renal_left = [1 / 15 for _ in range(100)]
        renal_right = [1 / 15 for _ in range(100)]
        iliaca_left = [1 / 10 for _ in range(100)]
        iliaca_right = [1 / 10 for _ in range(100)]


        map3D.add_vessel_impedance_prediction_as_millimeter_list(aorta_before, 0)
        map3D.add_vessel_impedance_prediction_as_millimeter_list(aorta_after, 1)
        map3D.add_vessel_impedance_prediction_as_millimeter_list(renal_left, 2)
        map3D.add_vessel_impedance_prediction_as_millimeter_list(renal_right, 3)
        map3D.add_vessel_impedance_prediction_as_millimeter_list(iliaca_left, 4)
        map3D.add_vessel_impedance_prediction_as_millimeter_list(iliaca_right, 5)

        map3D.add_mapping([0, 1])
        map3D.add_mapping([0, 2])
        map3D.add_mapping([0, 3])
        map3D.add_mapping([1, 4])
        map3D.add_mapping([1, 5])

        retriever = CroppingParticleReferenceRetriever()
        p = SlidingParticle3D(State3D(position=65, branch=0))
        p.state.set_position(110)
        p.state.branch = 4

        print(retriever.retrieve_reference_update(p, map3D))
        print(retriever.retrieve_reference_update(p, map3D))
        print(len(retriever.retrieve_reference_update(p, map3D)))


