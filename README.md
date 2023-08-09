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
Each particle $m$ contains a state hypothesis that comprises:


```math 
x_{t}^{[m]} = \begin{pmatrix} i_{t}^{[m]}, \\ d_{t}^{[m]}, \\ \alpha_{t}^{[m]} \end{pmatrix} 

```

- current branch position in the vessel tree $i_{t}^{[m]}$
- displacement along the centerline at this branch $d_{t}^{[m]}$
- estimate for the systematic error of the displacement sensing concept $\alpha_{t}^{[m]}$

The sliding particle object is used for the sliding_dtw weighting step of the filter. This particle also stores
the recent history of reference predictions of this particle. This reference history is required for the DTW comparison 
to the recent impedance measurement history. 

The number of particles used by the filter can be specified when setting up the navigator class.

### Prediction Step

```math 
u_t^{[m]} = \begin{pmatrix}
    0\\ \Delta d_{cath, t} * \alpha_{t}^{[m]} \\0
\end{pmatrix} 
```



```math 
p(x_t|x_{t-1}^{[m]}, u_t) = \mathcal{N}_3(u_t^{[m]} + x_{t-1}^{[m]}, \begin{pmatrix}
    0 & 0 & 0\\
    0 & \epsilon(u_t) & 0\\
    0 & 0 & 0
\end{pmatrix})
```

branch switch backward
```math 
x_{t}^{[m]} = \begin{pmatrix}
    k \\ l_k + d_{t}^{[m]} \\\alpha_{t}^{[m]} 
\end{pmatrix} 
```

branch switch forward
```math 
x_{t}^{[m]} = \begin{pmatrix}
    s \in_R  S \\ l_{i_{t-1}^{m}} - d_{t}^{[m]}  \\\alpha_{t}^{[m]} \end{pmatrix}
```


### Weighting Step
In the weighting step of the particle filter, each particle receives a weight. 
Therefore, a measurement strategy class calculates the measurement likelihood $p( z_t | x_{t}^{[m]})$,
which denotes the probability of observing the impedance measurement $z_t$ at time step $t$ if the
position estimate of the particle $m$ is correct.

The ahistoric measurement model class determines measurement likelihood according to:

```math 
p( z_t | x_{t}^{[m]}) \propto \biggl(\Bigl(z_t - ref_{t}^{[m]}\Bigr)^2\biggr)^{-1}
```
Thereby, the ahistoric measurement model compares the measurement $z_t$ to the reference prediction
$ref_{t}^{[m]}$ which is predicted based on the position estimate of particle $m$.

The sliding_dtw measurement model class determines measurement likelihood according to:
```math 
p( z_{t} | x_{t-n:t}^{[m]}, z_{t-n:t-1})  \propto \biggl(CW_{\beta}\Bigl(z_{t-n:t}, ref_{t-n:t}^{[m]}\Bigr)\biggr)^{-1}
```
Thereby, the sliding_dtw measurement model compares the previous $n$ measurement $z_{t-n:t-1}$ 
to the previous $n$ reference predictions $ref_{t-n:t}^{[m]}$  which is predicted based on the position estimate 
of particle $m$. The comparison of measurement and reference history is calculated as convex combination
of a standard DTW and a derivative DTW algorithm: 

```math 
CW_\beta(z_{t-n:t-1}, ref_{t-n:t}^{[m]}) = (1-\beta) * DTW(z_{t-n:t-1},ref_{t-n:t}^{[m]}) + \beta * DDTW(z_{t-n:t-1},ref_{t-n:t}^{[m]})
```

### Resampling Step

### Injection Step
alpha-variance injector
```math 
x_{t}^{[m]} = \begin{pmatrix}
    i_{t}^{m} \\ d_{t}^{[m]}   \\\alpha_{t}^{[m]} \leftarrow  \mathcal{N}(\alpha_{t}^{[m]}, 0.1)
\end{pmatrix} 
```

random particle injector
```math 
x_{t}^{[m]} = \begin{pmatrix}
    i_{t}^{m} \in_R  I \\ d_{t}^{[m]} \in_R [1,..., l_{i_{t}^{m}}]   \\\alpha_{t}^{[m]} \leftarrow  \mathcal{N}(\alpha_{t}^{[m]}, 0.1)
\end{pmatrix} 
```

## License

