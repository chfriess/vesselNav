import random


class Position:
    def __init__(self, displacement: float, branch: int):
        self.displacement = displacement
        self.branch = branch


class VesselTreeSegment:
    def __init__(self, length: float,
                 branch: int,
                 diameters: list,
                 children: list = None):
        self.length = length
        self.diameters = diameters
        self.branch = branch
        self.children = children

    def get_diameter(self, displacement: float):
        n = round(displacement)
        if n < 0 or n > self.length:
            raise ValueError("index " + str(displacement) + " out of bounds for VesselTreeElement id = " + str(id))
        return self.diameters[n]


class VesselTreeMap:

    def __init__(self):
        self.vessels = []

    def add_vessel_segment(self, vessel: VesselTreeSegment):
        self.vessels.append(vessel)
        self.vessels.sort(key=lambda e: e.branch, reverse=False)

    def get_vessel_diameter_at_position(self, position: Position):
        if position.branch < 0 or position.branch >= len(self.vessels):
            raise ValueError("branch " + str(position.branch) + " is not a valid branch id")
        return self.vessels[position.branch].get_diameter(position.displacement)

    def update_position(self, displacement: float, position: Position):
        if position.branch < 0 or position.branch >= len(self.vessels):
            raise ValueError("branch " + str(position.branch) + " is not a valid branch id")
        if 0 <= position.displacement + displacement <= self.vessels[position.branch].length:
            position.displacement += displacement
        else:
            position.displacement = displacement - (self.vessels[position.branch].length - position.displacement)
            position.branch = random.choice(self.vessels[position.branch].children)
