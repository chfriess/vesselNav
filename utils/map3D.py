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

