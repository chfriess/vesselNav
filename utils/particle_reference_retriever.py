

class ParticleReferenceRetriever:

    def retrieve_reference_update(self, particle, reference_signal: list) -> list: #  TODO: change to vessel tree reference

        position = round(particle.get_state().get_position()) # TODO: change to vessel tree position estimate
        if position < 0: # TODO: change to vessel tree position estimate
            particle.last_reference_index = 0
            return [reference_signal[0]]
        elif position > len(reference_signal) - 1:  # TODO: change to vessel tree position estimate
            particle.last_reference_index = len(reference_signal)-1  # TODO: change to vessel tree reference
            return [reference_signal[len(reference_signal) - 1]]  # TODO: change to vessel tree reference
        # forward motion
        if particle.last_reference_index <= position:  # TODO: change to vessel tree position estimate
            reference_update = self.retrieve_reference_update_forward(
                position=position,  # TODO: change to vessel tree position estimate
                last_reference_index=particle.last_reference_index,
                reference_signal=reference_signal)  # TODO: change to vessel tree reference
            particle.last_reference_index += len(reference_update)
        # backward motion
        else:
            reference_update = self.retrieve_reference_update_backward(
                position=position, # TODO: change to vessel tree position estimate
                last_reference_index=particle.last_reference_index,
                reference_signal=reference_signal)  # TODO: change to vessel tree reference

            particle.last_reference_index -= len(reference_update) # TODO: change to vessel tree reference
        if not reference_update:
            reference_update = [reference_signal[position]]
        return reference_update

    @staticmethod
    def retrieve_reference_update_forward(position: int, last_reference_index: int, reference_signal: list) -> list:  # TODO: change to vessel tree position estimate
        reference_update = []
        for index in range(last_reference_index + 1, position + 1):  # TODO: change to vessel tree position estimate
            if index < len(reference_signal):
                reference_update.append(reference_signal[index])   # TODO: change to vessel tree reference
        return reference_update

    @staticmethod
    def retrieve_reference_update_backward(position: int, last_reference_index: int, reference_signal: list) -> list:  # TODO: change to vessel tree position estimate
        reference_update = []
        # TODO: check for upper out of bounds? Why did I once observe a runtime increase over time when checking
        # for upper out of bounds?
        if last_reference_index >= len(reference_signal):  # TODO: change to vessel tree reference
            raise ValueError("last_reference_index was greater than length of reference signal")

        for index in range(last_reference_index - 1, position - 1, -1):  # TODO: change to vessel tree position estimate
            if 0 <= index:
                reference_update.append(reference_signal[index])  # TODO: change to vessel tree reference
        return reference_update
