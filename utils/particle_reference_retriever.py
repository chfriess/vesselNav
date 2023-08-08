from utils.map3D import Map3D


"""
The ParticleReferenceRetriever retrieves a reference prediction for a particle.
Therefore, it uses the position estimate of the particle and returns the reference value
stored in the map3D at the position estimate. 
"""


class ParticleReferenceRetriever:
    @staticmethod
    def retrieve_reference_update(particle, map3D: Map3D) -> list:
        local_reference_value = map3D.get_reference_value(
            branch=particle.get_state().get_position()["branch"],
            displacement=particle.get_state().get_position()["displacement"])
        return [local_reference_value]


