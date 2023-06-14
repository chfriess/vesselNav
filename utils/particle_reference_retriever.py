from utils.map3D import Map3D


class ParticleReferenceRetriever3D:
    @staticmethod
    def retrieve_reference_update(particle, map3D: Map3D) -> list:
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
