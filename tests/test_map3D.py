from unittest import TestCase

from utils.map3D import Map3D


class TestMap3D(TestCase):


    def test_load_map(self):
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

        map3D.save_map("C:\\Users\\Chris\\OneDrive\\Desktop", "test_map")

        reloaded = Map3D()
        reloaded.load_map("C:\\Users\\Chris\\OneDrive\\Desktop\\test_map.json")

        print(reloaded == map3D)


    def test_load_centerline_as_npy(self):
        map3D = Map3D()
        map3D.load_map("C:\\Users\\Chris\\OneDrive\\Desktop\\phantom_data_testing\\" + "reference_from_iliaca.npy")

        self.assertTrue(map3D.get_index_of_predecessor(0) == -1)
        self.assertTrue(map3D.get_indices_of_successors(0) == [])

