from utils.map3D import Map3D


# TODO: adapt to new reference data structure, and also write new Retriever with easier concept

class ParticleReferenceRetriever3D:


    def retrieve_reference_update(self, particle, map3D: Map3D) -> list:
        current_branch = particle.get_state().get_position()["branch"]
        current_displacement = round(particle.get_state().get_position()["displacement"])
        last_branch_index = particle.get_last_reference_index()["branch_index"]
        last_displacement_index = particle.get_last_reference_index()["displacement_index"]

        reference_update = []

        # reference update error handling if position estimate left branch
        if current_displacement < 0 and last_branch_index == 0:
            reference_update = self. \
                get_reference_update_if_catheter_left_map_backwards(particle=particle,
                                                                    current_branch=current_branch,
                                                                    map3D=map3D,
                                                                    last_displacement_index=last_displacement_index)
        elif current_displacement >= len(map3D.get_vessel(current_branch)) \
                and last_branch_index == map3D.get_number_of_vessels():
            reference_update = self. \
                get_reference_update_if_catheter_left_map_forwards(particle=particle,
                                                                   current_branch=current_branch,
                                                                   map3D=map3D,
                                                                   last_displacement_index=last_displacement_index)
        # forward motion in same branch
        elif last_displacement_index <= current_displacement and last_branch_index == current_branch:
            reference_update = self. \
                get_reference_update_forward_motion_same_branch(current_displacement=current_displacement,
                                                                current_branch=current_branch,
                                                                map3D=map3D,
                                                                last_displacement_index=last_displacement_index)

        # forward motion with branch switch
        elif last_branch_index < current_branch:
            reference_update = self. \
                get_reference_update_forward_motion_branch_switch(current_displacement=current_displacement,
                                                                  current_branch=current_branch,
                                                                  map3D=map3D,
                                                                  last_displacement_index=last_displacement_index,
                                                                  last_branch_index=last_branch_index)

        # backward motion in same branch
        elif last_displacement_index > current_displacement and last_branch_index == current_branch:
            reference_update = self. \
                get_reference_update_backward_motion_same_branch(current_displacement=current_displacement,
                                                                 current_branch=current_branch,
                                                                 map3D=map3D,
                                                                 last_displacement_index=last_displacement_index)

        # backward motion in other branch
        elif last_branch_index > current_branch:
            self.get_reference_update_backward_motion_branch_switch(current_displacement=current_displacement,
                                                                    current_branch=current_branch,
                                                                    map3D=map3D,
                                                                    last_displacement_index=last_displacement_index,
                                                                    last_branch_index=last_branch_index)

        else:
            raise ValueError("Different direction of motion in branch index and displacement index occured "
                             "- which should not be possible")

        return reference_update

    @staticmethod
    def get_reference_update_if_catheter_left_map_backwards(
            particle,
            current_branch: int,
            map3D: Map3D,
            last_displacement_index: int):
        particle.set_last_reference_index(branch_index=current_branch, displacement_index=0)
        # TODO: adapt to new reference data structure
        reference_update = map3D.get_vessel(current_branch)[0:last_displacement_index][::-1]
        return reference_update

    @staticmethod
    def get_reference_update_if_catheter_left_map_forwards(
            particle,
            current_branch: int,
            map3D: Map3D,
            last_displacement_index: int):
        particle.set_last_reference_index(branch_index=current_branch,
                                          displacement_index=len(map3D.get_vessel(current_branch)) - 1)
        # TODO: adapt to new reference data structure
        reference_update = map3D.get_vessel(current_branch)[last_displacement_index:]
        return reference_update

    @staticmethod
    def get_reference_update_forward_motion_same_branch(current_displacement: int,
                                                        current_branch: int,
                                                        map3D: Map3D,
                                                        last_displacement_index: int):
        reference_update = []
        for index in range(last_displacement_index, current_displacement + 1):
            # TODO: adapt to new reference data structure
            if index < len(map3D.get_vessel(current_branch)):
                # TODO: adapt to new reference data structure
                reference_update.append(map3D.get_vessel(current_branch)[index])
        return reference_update

    @staticmethod
    def get_reference_update_forward_motion_branch_switch(current_displacement: int,
                                                          current_branch: int,
                                                          map3D: Map3D,
                                                          last_displacement_index: int,
                                                          last_branch_index: int):
        branch_path = []
        acc = map3D.get_index_of_predecessor(current_branch)
        while acc > last_branch_index:
            branch_path.append(acc)
            acc = map3D.get_index_of_predecessor(acc)

        branch_path = branch_path[::-1]
        # TODO: adapt to new reference data structure
        reference_update = map3D.get_vessel(last_branch_index)[last_displacement_index:]
        for index in branch_path:
            # TODO: adapt to new reference data structure
            reference_update += map3D.get_vessel(index)
        for index in range(current_displacement):
            if index < len(map3D.get_vessel(current_branch)):
                # TODO: adapt to new reference data structure
                reference_update.append(map3D.get_vessel(current_branch)[index])
        return reference_update

    @staticmethod
    def get_reference_update_backward_motion_same_branch(current_displacement: int,
                                                         current_branch: int,
                                                         map3D: Map3D,
                                                         last_displacement_index: int):
        reference_update = []
        for index in range(last_displacement_index, current_displacement - 1, -1):
            if 0 <= index:
                # TODO: adapt to new reference data structure
                reference_update.append(map3D.get_vessel(current_branch)[index])
        return reference_update

    @staticmethod
    def get_reference_update_backward_motion_branch_switch(current_displacement: int,
                                                           current_branch: int,
                                                           map3D: Map3D,
                                                           last_displacement_index: int,
                                                           last_branch_index: int):
        # TODO: adapt to new reference data structure
        reference_update = map3D.get_vessel(last_branch_index)[:last_displacement_index][::-1]
        last_branch_index -= 1
        while last_branch_index > current_branch:
            # TODO: adapt to new reference data structure
            reference_update += map3D.get_vessel(last_branch_index)[::-1]
            last_branch_index = map3D.get_index_of_predecessor(index=last_branch_index)
        for index in range(len(map3D.get_vessel(current_branch)) - 1, current_displacement - 1, -1):
            if 0 <= index:
                # TODO: adapt to new reference data structure
                reference_update.append(map3D.get_vessel(current_branch)[index])

        return reference_update
