from particles.particle import Particle


class ParticleSet(object):
    def __init__(self) -> None:
        self.set = []

    def append(self, particle: Particle) -> None:
        if not isinstance(particle, Particle):
            raise ValueError("ParticleSet must only contain objects of the Particle class")
        self.set.append(particle)

    def remove(self, particle: Particle) -> None:
        if not isinstance(particle, Particle):
            raise ValueError("ParticleSet must only contain objects of the Particle class")
        self.set.remove(particle)

    def sort_ascending_by_weight(self):
        self.set.sort(key=lambda p: p.weight, reverse=False)

    def sort_descending_by_weight(self):
        self.set.sort(key=lambda p: p.weight, reverse=True)

    def pop_last(self) -> Particle:
        return self.set.pop()

    def __len__(self):
        return len(self.set)

    def __getitem__(self, item):
        return self.set[item]

    def __iter__(self):
        return self.set.__iter__()
