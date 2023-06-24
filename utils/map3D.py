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

    # TODO test this fuction
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
            if not current_vessel[index-1]["centerline_position"] <= displacement\
                   <= current_vessel[index]["centerline_position"]:
                raise ValueError("Error in get_reference_value function:"
                                 " displacement could not be located between to adjacent centerline points")
            x = [current_vessel[index-1]["centerline_position"], current_vessel[index]["centerline_position"]]
            y = [current_vessel[index-1]["reference_signal"], current_vessel[index]["reference_signal"]]
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
                self.vessels = map_to_read["vessels"]
                self.mappings = map_to_read["mappings"]
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

    # TODO: load vessel only directly from json