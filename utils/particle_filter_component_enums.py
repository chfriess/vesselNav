from enum import Enum


class MeasurementType(Enum):
    AHISTORIC = 0
    SLIDING_DTW = 1
    SLIDING_DERIVATIVE_DTW = 2


class InjectorType(Enum):
    ALPHA_VARIANCE = 0
    RANDOM_PARTICLE = 1
