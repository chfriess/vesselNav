class Position:
    def __init__(self, center: float, error: float):
        self.center = center
        self.error = error

    def __str__(self):
        return f'[center: {str(self.center)} | error: {str(self.error)}]'

    def get_center(self) -> float:
        return self.center

    def get_error(self) -> float:
        return self.error


class Position3D(Position):
    def __init__(self,
                 center: float,
                 error: float,
                 branch: int,
                 number_of_particles: int):
        super().__init__(center, error)
        self.branch = branch
        self.number_of_particles = number_of_particles

    def get_branch(self):
        return self.branch

    def get_number_of_particles(self):
        return self.number_of_particles
