import json
import numbers

import numpy as np


class Map3D:

    def __init__(self,
                 vessels: dict = None,
                 mappings: list = None,
                 ):
        if vessels is None:
            self.vessels = {}
        else:
            self.vessels = vessels
        if mappings is None:
            self.mappings = []
        else:
            self.mappings = mappings

    def __str__(self):
        return f'[Vessels: {str(self.vessels)} | mappings: {self.mappings} ]'

    def __eq__(self, other):
        if isinstance(other, Map3D):
            return self.vessels == other.vessels and self.mappings == other.mappings
        return False

    def add_vessel_impedance_prediction_per_position_in_mm(self, positions: list, diameters: list, index: int):
        if not positions[0] == 0:
            raise ValueError("must provide diameter of vessel beginn")
        x = np.linspace(0, positions[-1], round(positions[-1]))
        diameters = np.interp(x, positions, diameters)
        self.add_vessel_impedance_prediction_as_millimeter_list(vessel=list(diameters), index=index)

    def add_vessel_impedance_prediction_as_millimeter_list(self, vessel: list, index: int):
        if not all(isinstance(x, numbers.Number) for x in vessel):
            raise ValueError("The diameters of a vessel can only contain numeric values")
        if index in self.vessels.keys():
            raise ValueError("Vessel with index " + str(index) + " already preset in the map")
        self.vessels[index] = vessel

    def add_mapping(self, mapping: list):
        if not all(isinstance(x, int) for x in mapping):
            raise ValueError("The mapping must consist of integer values")
        if not len(mapping) == 2:
            raise ValueError("The mapping must consist of 2 integer values")
        self.mappings.append(mapping)

    def get_vessels(self):
        return self.vessels

    def get_mappings(self):
        return self.mappings

    def get_vessel(self, index: int) -> list:
        return self.vessels[index]

    def get_index_of_predecessor(self, index: int) -> int:
        for mapping in self.mappings:
            if mapping[1] == index:
                return mapping[0]
        return -1

    def get_indices_of_successors(self, index: int) -> list:
        successor_indices = []
        for mapping in self.mappings:
            if mapping[0] == index:
                successor_indices.append(mapping[1])
        if not successor_indices:
            return []
        return successor_indices

    def save_map(self, absolut_path: str, filename: str):
        map_storage_format = {"vessels": self.vessels, "mappings": self.mappings}
        jo = json.dumps(map_storage_format, indent=4)

        with open(absolut_path + "\\" + filename + ".json", "w") as outfile:
            outfile.write(jo)

    def load_map(self, absolute_path: str):
        with open(absolute_path, "r") as infile:
            map_to_read = json.load(infile)
            self.vessels = map_to_read["vessels"]
            self.mappings = map_to_read["mappings"]

        """
        cannot iterate over key set directly while popping keys, therefore the keys list 
        conversion of key to int is necessary, because json only allows keys to be stored as strings
        """

        keys = [key for key in self.vessels.keys()]
        for key in keys:
            self.vessels[int(key)] = self.vessels.pop(key)



if __name__ == "__main__":
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