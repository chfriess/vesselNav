# vesselNav
A particle filter implementation for localizing a catheter in the vessel tree during and endovascular intervention. 


## Getting Started

- The particle filter implementation depends on the following libraries
  - numpy version 1.21.6
  - tslearn version 0.5.3.2
  - sklearn version 1.0.2
- The VesselNavigator class acts as interface to using the particle filter.
  - The setup_navigator method allows to specify the parameters of the filter (Number of particles, Measurement Type, Injector type...)
  - The update_step method takes a displacement and impedance measurement value and updates the particle set, and returns an updated position estimate
The filter used a modular concept. Each step of the filter (prediction, weighting, resampling, injection) is performed
by an individual class that respectively implements the motion strategy, measurement strategy, resampling strategy
and injection strategy interface. For each of the steps, individual implementations can be passed to the constructor of the
particle filter, as long as they implement the correct strategy interface.
  

## Particle Filter Concept

The filter combines bioelectric impedance data with data of a displacement sensor. Recorded data of the impedance sensor
is a correlate of the cross-sectional area of the vessel. The data of the displacement sensor indicates the velocity
and the movement direction fo the catheter. The filter combines both sensors into a position estimate. The position 
estimates are located in a pre-interventionally calculated map of vessel centerlines.


### Vessel Centerline Map

The Map3D is a data structure to represent the vessel tree and the position based impedance reference predictions
of the catheter intervention as vessel centerline map.
A Map3D object can load vessel centerlines as .json files with the add_vessel_from_json method. The .json file
is expected to have the format:  
  



    {
        "signal_per_centerline_position":
          [
            {
              "centerline_position": position, 
              "reference_signal": reference
            },
            ...
            {
              "centerline_position": position, 
              "reference_signal": reference
            }
          ]
    }



The method add_vessel_from_json takes a path to the .json file as well as a unique integer vessel index as argument.
The connections between the vessels in the Map3D are set by the add_mapping method. This method takes a list of two
integers [n,m] as argument. The mapping [n,m] indicates that the end of vessel with index n is connected to the 
beginning of the vessel with index m. 


### Particle
Each particle contains a state hypothesis that comprises:


$$ x_{t}^{[m]} = \begin{pmatrix} i_{t}^{[m]} \\ d_{t}^{[m]} \\ \alpha_{t}^{[m]} \end{pmatrix} $$


- current branch position in the vessel tree $i_{t}^{[m]}$
- displacement along the centerline at this branch  $d_{t}^{[m]}$
- estimate for the systematic error of the displacement sensing concept $\alpha_{t}^{[m]}$

The sliding particle object is used for the sliding_dtw weighting step of the filter. This particle also stores
the recent history of reference predictions of this particle. This reference history is required for the DTW comparison 
to the recent impedance measurement history. 

The number of particles used by the filter can be specified when setting up the navigator class.

### Prediction Step



### Weighting Step


### Resampling Step

### Injection Step


## License

