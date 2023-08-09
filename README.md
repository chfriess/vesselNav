# vesselNav
A particle filter implementation for localizing a catheter in the vessel tree during and endovascular intervention. 

The filter combines bioelectric impedance data with data of a displacement sensor. Recorded data of the impedance sensor
is a correlate of the cross-sectional area of the vessel. The data of the displacement sensor indicates the velocity
and the movement direction fo the catheter. The filter combines both sensors into a position estimate. The position 
estimates are located in a pre-interventionally calculated map of vessel centerlines.




## Getting Started

- The particle filter implementation depends on the following libraries
  - numpy version 1.21.6
  - tslearn version 0.5.3.2
  - sklearn version 1.0.2
- The VesselNavigator class acts as interface to using the particle filter.
  - The setup_navigator method allows to specifiy the parameters of the filter (Number of particles, Measurement Type, Injector type...)
  - The update_step method takes a displacement and impedance measurement value and updates the particle set, and returns a updated position estimate
  

## Particle Filter Concept

- based on bioelectric navigation and displacement sensor; maybe cite?



### Vessel Centerline Map

### Particle
Each particle contains a hypothesis of:
- current branch position in the vessel tree
- displacement along the centerline at this branch
- estimate for the systematic error of the displacement sensing concept

The number of particles used by the filter can be specified when setting up the navigator class

### Prediction Step



### Weighting Step


### Resampling Step

### Injection Step


## License

