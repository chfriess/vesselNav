from map.map import Position


class PositionEstimate:
    def __init__(self, center: Position, error: float) -> None:
        self.center = center
        self.error = error

    def __str__(self):
        return f'[center: {str(self.center)} | error: {str(self.error)}]'

    def get_center(self) -> Position:
        return self.center

    def get_error(self) -> float:
        return self.error
