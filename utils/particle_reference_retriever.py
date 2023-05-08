
# TODO: when calling retrieve reference update: pass the reference signal of the current branch!
class ParticleReferenceRetriever:

    def retrieve_reference_update(self, particle, reference_signal: list) -> list:
        position = round(particle.state.position.displacement)
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
        # TODO: check for upper out of bounds? Why did I once observe a runtime increase over time when checking
        # for upper out of bounds?
        if last_reference_index >= len(reference_signal):
            raise ValueError("last_reference_index was greater than length of reference signal")

        for index in range(last_reference_index - 1, position - 1, -1):
            if 0 <= index:
                reference_update.append(reference_signal[index])
        return reference_update
