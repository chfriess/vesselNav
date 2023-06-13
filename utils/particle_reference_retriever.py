from utils.map3D import Map3D


class ParticleReferenceRetriever:

    def retrieve_reference_update(self, particle, reference_signal: list) -> list:

        position = round(particle.get_state().get_position())
        if position < 0:
            particle.last_reference_index = 0
            return [reference_signal[0]]
        elif position > len(reference_signal) - 1:
            particle.last_reference_index = len(reference_signal)-1
            return [reference_signal[- 1]]
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
        current_branch = particle.get_state().get_position()["branch"]
        current_displacement = round(particle.get_state().get_position()["displacement"])
        last_branch_index = particle.get_last_reference_index()["branch_index"]
        last_displacement_index = particle.get_last_reference_index()["displacement_index"]

        reference_update = []

        if current_displacement < 0 and last_branch_index == current_branch:
            particle.set_last_reference_index(branch_index=current_branch, displacement_index=0)
            reference_update = map3D.get_vessel(current_branch)[0:last_displacement_index][::-1]
        elif current_displacement >= len(map3D.get_vessel(current_branch)) and last_branch_index == current_branch:
            particle.set_last_reference_index(branch_index=current_branch,
                                              displacement_index=len(map3D.get_vessel(current_branch)) - 1)
            reference_update = map3D.get_vessel(current_branch)[last_displacement_index:]

        # forward motion in same branch
        elif last_displacement_index <= current_displacement and last_branch_index == current_branch:

            for index in range(last_displacement_index + 1, current_displacement + 1):
                if index < len(map3D.get_vessel(current_branch)):
                    reference_update.append(map3D.get_vessel(current_branch)[index])

        # forward motion with branch switch
        elif last_branch_index < current_branch:
            branch_path = []
            acc = map3D.get_index_of_predecessor(current_branch)
            while acc > last_branch_index:
                branch_path.append(acc)
                acc = map3D.get_index_of_predecessor(acc)
            branch_path = branch_path[::-1]
            reference_update = map3D.get_vessel(last_branch_index)[last_displacement_index:]
            for index in branch_path:
                reference_update += map3D.get_vessel(index)
            for index in range(current_displacement):
                if index < len(map3D.get_vessel(current_branch)):
                    reference_update.append(map3D.get_vessel(current_branch)[index])

        # backward motion in same branch
        elif last_displacement_index > current_displacement and last_branch_index == current_branch:
            for index in range(last_displacement_index - 1, current_displacement - 1, -1):
                if 0 <= index:
                    reference_update.append(map3D.get_vessel(current_branch)[index])

        # backward motion in other branch
        elif last_branch_index > current_branch:
            reference_update = map3D.get_vessel(last_branch_index)[:last_displacement_index][::-1]
            last_branch_index -= 1
            while last_branch_index > current_branch:
                reference_update += map3D.get_vessel(last_branch_index)[::-1]
                last_branch_index = map3D.get_index_of_predecessor(index=last_branch_index)
            for index in range(len(map3D.get_vessel(current_branch)) - 1, current_displacement-1, -1):
                if 0 <= index:
                    reference_update.append(map3D.get_vessel(current_branch)[index])

        # backward motion with branch switch
        else:
            raise ValueError("Different direction of motion in branch index and displacement index occured "
                             "- which should not be possible")

        return reference_update


if __name__ == "__main__":
    # TODO: extensive testing of 3D particle reference retriever
    pass
