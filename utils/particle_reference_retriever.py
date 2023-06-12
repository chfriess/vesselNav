from utils.map3D import Map3D


class ParticleReferenceRetriever:

    def retrieve_reference_update(self, particle, reference_signal: list) -> list:

        position = round(particle.get_state().get_position())
        if position < 0:
            particle.last_reference_index = 0
            return [reference_signal[0]]
        elif position > len(reference_signal) - 1:
            particle.last_reference_index = len(reference_signal)-1
            return [reference_signal[len(reference_signal) - 1]]
        # forward motion
        if particle.last_reference_index <= position:
            reference_update = self.retrieve_reference_update_forward(
                position=position,
                last_reference_index=particle.last_reference_index,
                reference_signal=reference_signal)
            particle.last_reference_index += len(reference_update)
        # backward motion
        else:
            reference_update = self.retrieve_reference_update_backward(
                position=position,
                last_reference_index=particle.last_reference_index,
                reference_signal=reference_signal)

            particle.last_reference_index -= len(reference_update)
        if not reference_update:
            reference_update = [reference_signal[position]]
        return reference_update

    @staticmethod
    def retrieve_reference_update_forward(position: int, last_reference_index: int, reference_signal: list) -> list:
        reference_update = []
        for index in range(last_reference_index + 1, position + 1):
            if index < len(reference_signal):
                reference_update.append(reference_signal[index])
        return reference_update

    @staticmethod
    def retrieve_reference_update_backward(position: int, last_reference_index: int, reference_signal: list) -> list:
        reference_update = []
        if last_reference_index >= len(reference_signal):
            raise ValueError("last_reference_index was greater than length of reference signal")
        for index in range(last_reference_index - 1, position - 1, -1):
            if 0 <= index:
                reference_update.append(reference_signal[index])
        return reference_update


class ParticleReferenceRetriever3D:
    def retrieve_reference_update(self, particle, map3D: Map3D) -> list:
        pass
