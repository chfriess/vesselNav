# vesselNav
A particle filter implementation for localizing a catheter in the vessel tree during and endovascular intervention. 




## Getting Started

- The particle filter implementation depends on the following libraries
  - numpy version 1.21.6
  - tslearn 
  - sklearn version 1.0.2
- How to use it on data -> navigator class as interface


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

