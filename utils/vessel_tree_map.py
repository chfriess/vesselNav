from abc import abstractmethod
import random


class Position:
    def __init__(self, x: float, branch: int):
        self.x = x
        self.branch = branch


class Map:
    @abstractmethod
    def get_diameter(self, position: Position):
        raise NotImplementedError

    @abstractmethod
    def update_position(self,
                        displacement: float,
                        position: Position):
        raise NotImplementedError


class VesselTreeElement:
    def __init__(self, length: float,
                 branch: int,
                 diameters: dict,
                 children: list = None):
        self.length = length
        self.diameters = diameters
        self.branch = branch
        self.children = children

    def get_diameter(self, x: float):
        # TODO: how to round x up or down?
        n = int(x)
        if n < 0 or n > self.length:
            raise ValueError("index " + str(x) + " out of bounds for VesselTreeElement id = " + str(id))
        return self.diameters[n]


class VesselTreeMap(Map):

    def __init__(self):
        self.elements = []

    def add_element(self, element: VesselTreeElement):
        self.elements.append(element)
        self.elements.sort(key=lambda e: e.index, reverse=False)

    def get_diameter(self, position: Position):
        if position.branch < 0 or position.branch >= len(self.elements):
            raise ValueError("branch " + str(position.branch) + " is not a valid branch id")
        return self.elements[position.branch].get_diameter()

    def update_position(self, displacement: float, position: Position):
        if position.branch < 0 or position.branch >= len(self.elements):
            raise ValueError("branch " + str(position.branch) + " is not a valid branch id")
        if 0 <= position.x + displacement <= self.elements[position.branch].length:
            position.x += displacement
        else:
            position.x = displacement - (self.elements[position.branch].length - position.x)
            position.branch = random.choice(self.elements[position.branch].children)


class LinearMap(Map):

    def __init__(self, length: float, diameters: dict):
        self.length = length
        self.diameters = diameters

    def get_diameter(self, position: Position):
        n = int(position.x)
        if n < 0 or n > self.length:
            raise ValueError("index " + str(position.x) + " out of bounds for VesselTreeElement id = " + str(id))
        return self.diameters[n]

    def update_position(self, displacement: float, position: Position):
        if 0 <= position.x + displacement <= self.length:
            position.x += displacement
        elif (position.x + displacement) > self.length:
            position.x = self.length
        else:
            position.x = 0
