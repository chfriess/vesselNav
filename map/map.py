import random


class Position:
    def __init__(self, displacement: float, branch: int):
        self.displacement = displacement
        self.branch = branch

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.displacement == other.displacement and self.branch == other.branch
        return False

    def __str__(self):
        return "displacement = " + str(self.displacement) + "mm | " + "branch id: " + str(self.branch)

    def get_displacement(self):
        return self.displacement

    def get_branch(self):
        return self.branch

class VesselTreeSegment:
    def __init__(self, length_in_millimeters: float,
                 branch_id: int,
                 diameter_per_millimeter_in_millimeter: list,
                 parent=None):
        if length_in_millimeters != len(diameter_per_millimeter_in_millimeter):
            raise ValueError("length of the vessel in millimeter must be equal to number "
                             "of diameter values per millimeter ")
        self.length = length_in_millimeters
        self.diameters = diameter_per_millimeter_in_millimeter
        self.branch_id = branch_id
        self.children = []
        self.parent = parent

    def get_diameter(self, displacement: float):
        n = round(displacement)
        if n < 0 or n > self.length:
            raise ValueError("index " + str(displacement) + " out of bounds for VesselTreeElement id = "
                             + str(self.branch_id) + " with a length of " + str(self.length))
        return self.diameters[n]

    def add_child_vessel(self, child_vessel):
        self.children.append(child_vessel)

    def remove_child_vessel(self, child_vessel):
        self.children.remove(child_vessel)

    def add_parent_vessel(self, parent_vessel):
        self.parent = parent_vessel

    def remove_parent_vessel(self):
        self.parent = None


class VesselTreeMap:

    def __init__(self):
        self.vessels = []

    def add_vessel_segment(self, vessel: VesselTreeSegment):
        self.vessels.append(vessel)
        self.vessels.sort(key=lambda e: e.branch_id, reverse=False)

    def get_vessel_diameter_at_position(self, position: Position):
        if position.branch < 0 or position.branch >= len(self.vessels):
            raise ValueError("branch " + str(position.branch) + " is not a valid branch id")
        return self.vessels[position.branch].get_diameter(position.displacement)

    def update_position(self, displacement: float, position: Position):
        if position.branch < 0 or position.branch >= len(self.vessels):
            raise ValueError("branch " + str(position.branch) + " is not a valid branch id")
        elif 0 <= position.displacement + displacement < self.vessels[position.branch].length:
            position.displacement += displacement
        # case move out of vessel backwards
        elif position.displacement + displacement < 0:
            if self.vessels[position.branch].parent:
                if displacement >= 0:
                    raise ValueError("Position estimate cannot be negative")
                displacement += position.displacement
                position.branch = self.vessels[position.branch].parent.branch_id
                position.displacement = self.vessels[position.branch].length + displacement
                if position.displacement < 0:
                    position.displacement = 0
            else:
                position.displacement = 0

        # case move out of vessel forwards
        elif position.displacement + displacement >= self.vessels[position.branch].length:
            if self.vessels[position.branch].children:
                position.displacement = displacement - (self.vessels[position.branch].length - position.displacement)
                position.branch = random.choice(self.vessels[position.branch].children).branch_id
                if position.displacement >= self.vessels[position.branch].length:
                    position.displacement = self.vessels[position.branch].length - 1
            else:
                position.displacement = self.vessels[position.branch].length - 1

"""
if __name__ == "__main__":
    tree = VesselTreeMap()
    vessel_one = VesselTreeSegment(length_in_millimeters=5,
                                   branch_id=0,
                                   diameter_per_millimeter_in_millimeter=[2, 2, 2, 2, 2],
                                   )

    vessel_two = VesselTreeSegment(length_in_millimeters=3,
                                   branch_id=1,
                                   diameter_per_millimeter_in_millimeter=[1, 1, 1],
                                   )
    vessel_three = VesselTreeSegment(length_in_millimeters=3,
                                     branch_id=2,
                                     diameter_per_millimeter_in_millimeter=[1, 1, 1],
                                     )

    vessel_one.add_child_vessel(vessel_two)
    vessel_one.add_child_vessel(vessel_three)

    vessel_two.add_parent_vessel(vessel_one)
    vessel_three.add_parent_vessel(vessel_one)

    tree.add_vessel_segment(vessel_one)
    tree.add_vessel_segment(vessel_two)
    tree.add_vessel_segment(vessel_three)

    p = Position(displacement=4, branch=0)
    tree.update_position(displacement=7, position=p)
    print(p)
"""
