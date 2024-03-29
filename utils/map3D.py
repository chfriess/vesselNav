import copy
import json
import numbers

import numpy as np

"""
THe map3D class represents a 3D vessel tree as set of centerlines. Each vessel possesses a 
unique index. The connections between the vessels are encoded by an index structure. 
If two vessels with index i and j have a connection from i to j, the pair [i,j] represents this
connection.
"""


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

    def check_right_vessel_format(self, index: int):
        if len(self.vessels) > 0 and max(list(self.vessels.keys())) == index:
            raise ValueError("Vessels with index: "
                             + str(max(list(self.vessels.keys()))) + str(" was already added"))
        if len(self.vessels) > 0 and max(list(self.vessels.keys())) != index - 1:
            raise ValueError("Vessels must be added in ascending order; last added index was: "
                             + str(max(list(self.vessels.keys()))))

    def add_vessel_impedance_prediction_per_position_in_mm(self, positions: list, reference_values: list, index: int):
        self.check_right_vessel_format(index=index)
        if not len(positions) == len(reference_values):
            raise ValueError("Number of positions and number of diameters must be equal to map correspondences")
        vessel = []
        for i, position in enumerate(positions):
            vessel.append({"centerline_position": position, "reference_signal": reference_values[i]})
        self.vessels[index] = vessel

    def add_vessel_impedance_prediction_as_millimeter_list(self, reference_values: list, index: int):
        if not all(isinstance(x, numbers.Number) for x in reference_values):
            raise ValueError("The reference of a vessel can only contain numeric values")
        positions = [x for x in range(len(reference_values))]
        self.add_vessel_impedance_prediction_per_position_in_mm(positions=positions,
                                                                reference_values=reference_values,
                                                                index=index)

    def add_vessel_as_list_of_dicts(self, vessel: list, index: int):
        self.check_right_vessel_format(index=index)
        self.vessels[index] = vessel

    def add_vessel_from_json(self, absolute_path: str, index: int):
        self.check_right_vessel_format(index)
        if absolute_path.endswith('.json'):
            with open(absolute_path, "r") as infile:
                vessel_to_read = json.load(infile)
                vessel = vessel_to_read["signal_per_centerline_position"]
                self.vessels[index] = vessel
        else:
            raise ValueError("File must be of type .json")

    def add_mapping(self, mapping: list):
        if not all(isinstance(x, int) for x in mapping):
            raise ValueError("The mapping must consist of integer values")
        if not len(mapping) == 2:
            raise ValueError("The mapping must consist of 2 integer values")
        self.mappings.append(mapping)

    def get_vessels(self):
        return self.vessels

    def get_number_of_vessels(self):
        return len(self.vessels)

    def get_mappings(self):
        return self.mappings

    def get_vessel(self, index: int) -> list:
        return self.vessels[index]

    def get_index_of_predecessor(self, index: int) -> int:
        for mapping in self.mappings:
            if mapping[1] == index:
                return mapping[0]

        # base vessel is its own predecessor
        return 0

    def get_indices_of_successors(self, index: int) -> list:
        successor_indices = []
        for mapping in self.mappings:
            if mapping[0] == index:
                successor_indices.append(mapping[1])
        if not successor_indices:
            return []
        return successor_indices

    # Expects centerline positions to be monotonically increasing! => makes search faster
    def get_reference_value(self, branch: int, displacement: float) -> float:
        if branch not in self.vessels.keys():
            raise ValueError("No vessel branch with index " + str(branch) + " in the map")
        current_vessel = self.vessels[branch]
        if displacement <= current_vessel[0]["centerline_position"]:
            return current_vessel[0]["reference_signal"]
        elif displacement >= current_vessel[-1]["centerline_position"]:
            return current_vessel[-1]["reference_signal"]
        else:
            index = 0
            while displacement > current_vessel[index]["centerline_position"]:
                index += 1
            if not current_vessel[index - 1]["centerline_position"] <= \
                   displacement <= current_vessel[index]["centerline_position"]:
                raise ValueError("Error in get_reference_value function:"
                                 " displacement could not be located between to adjacent centerline points")
            x = [current_vessel[index - 1]["centerline_position"], current_vessel[index]["centerline_position"]]
            y = [current_vessel[index - 1]["reference_signal"], current_vessel[index]["reference_signal"]]
            reference_value = np.interp(displacement, x, y)
            return reference_value

    def save_map(self, absolut_path: str, filename: str):
        map_storage_format = {"vessels": self.vessels, "mappings": self.mappings}
        jo = json.dumps(map_storage_format, indent=4)

        with open(absolut_path + "\\" + filename + ".json", "w") as outfile:
            outfile.write(jo)

    def load_map(self, absolute_path: str):
        if absolute_path.endswith('.json'):
            with open(absolute_path, "r") as infile:
                map_to_read = json.load(infile)
                if 'vessels' and 'mappings' in map_to_read.keys():
                    self.vessels = map_to_read["vessels"]
                    self.mappings = map_to_read["mappings"]
                elif 'signal_per_centerline_position' in map_to_read.keys():
                    self.add_vessel_from_json(absolute_path=absolute_path, index=0)
                else:
                    raise ValueError("json map not in the right format")
        elif absolute_path.endswith('.npy'):
            centerline = np.load(absolute_path)
            self.add_vessel_impedance_prediction_as_millimeter_list(list(centerline), 0)

        """
        cannot iterate over key set directly while popping keys, therefore the keys list 
        conversion of key to int is necessary, because json only allows keys to be stored as strings
        """

        keys = [key for key in self.vessels.keys()]
        for key in keys:
            self.vessels[int(key)] = self.vessels.pop(key)

if __name__ == "__main__":
    PATH = "C:\\Users\\Chris\\OneDrive\\Desktop\\branch_pruning_agar_I\\3D reference new\\"
    m = Map3D()

    aorta_0 = list(np.load(PATH+"aorta_0.npy"))
    aorta_1 = list(np.load(PATH+"aorta_1.npy"))
    aorta_2 = list(np.load(PATH+"aorta_2.npy"))
    aorta_3 = list(np.load(PATH+"aorta_3.npy"))
    aorta_4 = list(np.load(PATH+"aorta_4.npy"))

    renal = list(np.load(PATH+"renal.npy"))
    iliac = list(np.load(PATH+"iliac.npy"))
    lumbal = list(np.load(PATH+"lumbal.npy"))


    m.add_vessel_impedance_prediction_as_millimeter_list(aorta_0, 0)
    m.add_vessel_impedance_prediction_as_millimeter_list(aorta_1, 1)
    m.add_vessel_impedance_prediction_as_millimeter_list(aorta_2, 2)
    m.add_vessel_impedance_prediction_as_millimeter_list(aorta_3, 3)
    m.add_vessel_impedance_prediction_as_millimeter_list(aorta_4, 4)

    m.add_vessel_impedance_prediction_as_millimeter_list(iliac, 5)
    m.add_vessel_impedance_prediction_as_millimeter_list(copy.deepcopy(iliac), 6)

    m.add_vessel_impedance_prediction_as_millimeter_list(renal, 7)
    m.add_vessel_impedance_prediction_as_millimeter_list(copy.deepcopy(renal), 8)

    m.add_vessel_impedance_prediction_as_millimeter_list(lumbal, 9)
    m.add_vessel_impedance_prediction_as_millimeter_list(copy.deepcopy(lumbal), 10)

    m.add_mapping([0, 1])
    m.add_mapping([1, 2])
    m.add_mapping([2, 3])
    m.add_mapping([3, 4])

    m.add_mapping([4, 5])
    m.add_mapping([4, 6])

    m.add_mapping([0, 7])
    m.add_mapping([1, 8])
    m.add_mapping([2, 9])
    m.add_mapping([3, 10])

    m.save_map(PATH, "pruning_map")
