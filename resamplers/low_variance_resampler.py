import copy
import random

from strategies.resampling_strategy import ResamplingStrategy
from utils.particle_set import ParticleSet


class LowVarianceResampler(ResamplingStrategy):

    @staticmethod
    def generate_cumulative_weight_list(particle_set: ParticleSet) -> list:
        cumulative_weights = [particle_set[0].weight]
        for index in range(1, len(particle_set)):
            cumulative_weights.append(cumulative_weights[index - 1] + particle_set[index].weight)
        return cumulative_weights

    def resample(self, weighted_particle_set: ParticleSet) -> ParticleSet:
        resampled_particle_set = ParticleSet()

        n = len(weighted_particle_set)
        random_root = random.uniform(0, (1 / n))
        cumulative_weights = self.generate_cumulative_weight_list(particle_set=weighted_particle_set)
        i = 0
        for j in range(0, n):
            accumulator = random_root + j * (1 / n)
            while accumulator > cumulative_weights[i]:
                i += 1
                if i > len(cumulative_weights)-1:
                    # TODO: change print to logger
                    print("ERROR OCCURRED - Ov")
                    if len(resampled_particle_set) < len(weighted_particle_set):
                        resampled_particle_set.append(weighted_particle_set[0])
                        return resampled_particle_set
                    else:
                        return resampled_particle_set
            resampled_particle_set.append(particle=copy.deepcopy(weighted_particle_set[i]))

        return resampled_particle_set
