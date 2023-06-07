import numbers


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

    def add_vessel_as_dict(self, vessel: dict, index: int):
        pass

    def add_vessel_as_millimeter_list(self, vessel: list, index: int):
        if not all(isinstance(x, numbers.Number) for x in vessel):
            raise ValueError("The diameters of a vessel can only contain numeric values")
        if index in self.vessels.keys():
            raise ValueError("Vessel with index " + str(index) + " already preset in the map")
        self.vessels[index] = vessel

    def add_mapping(self, mapping: list):
        if not all(isinstance(x, tuple) for x in mapping):
            raise ValueError("The mapping must consist of tuples containing 2 integer values")
        if not all(len(x) == 2 for x in mapping):
            raise ValueError("The mapping must consist of tuples containing 2 integer values")
        if not all(isinstance(x, int) and isinstance(y, int) for (x, y) in mapping):
            raise ValueError("The mapping must consist of tuples containing 2 integer values")
        self.mappings.append(mapping)

    def get_vessel(self, index: int) -> list:
        return self.vessels[index]

    def get_index_of_predecessor(self, index: int) -> int:
        for mapping in self.mappings:
            if mapping[1] == index:
                return mapping[0]
        raise ValueError("No vessel with index " + str(index) + "found in the map")

    def get_indices_of_successors(self, index: int) -> list:
        successor_indices = []
        for mapping in self.mappings:
            if mapping[0] == index:
                successor_indices.append(mapping[1])
        if not successor_indices:
            raise ValueError("No vessel with index " + str(index) + "found in the map")
        return successor_indices
