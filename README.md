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
  - The filter does not normalize or process the displacement or impedance values. If normalization is necessary, it must be done before feeding the data into the filter
The filter used a modular concept. Each step of the filter (prediction, weighting, resampling, injection) is performed
by an individual class that respectively implements the motion strategy, measurement strategy, resampling strategy
and injection strategy interface. For each of the steps, individual implementations can be passed to the constructor of the
particle filter, as long as they implement the correct strategy interface.
  

## Particle Filter Concept

The filter combines bioelectric impedance data **[1]** **[2]** with data of a displacement sensor **[3]**. Recorded data of the impedance sensor
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
Complete maps can be stored and reloaded as .json files of the format:


    {
        "vessels": {
            "0" : 
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
                ],
            "1" : 
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
                ],
            ...
        },
        "mappings" : [
            [
                0,
                1
            ],
            ...
        ]
        
    }





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
To read a position estimate from the set of particles, the particles are clustered in space using DBSCAN **[4]**.
The average of the largest cluster is used as position estimate.

### Prediction Step
For the prediction step, the MotionModel class generates the variable $u_t$ from the displacement
measurement $\Delta d_{cath, t}$ recorded with the displacement sensing concept at $t$ and the
estimate for the systematic error of the displacement sensing concept $\alpha_{t}^{[m]}$ of 
particle $m$:
```math 
u_t^{[m]} = \begin{pmatrix}
    0\\ \Delta d_{cath, t} * \alpha_{t-1}^{[m]} \\0
\end{pmatrix} 
```
The variable $u_t$ and the measurement noise of the displacement sensing concept $\epsilon(u_t)$ is used
to determine a normal distribution. The position estimate $d_{t}^{[m]}$ of particle $m$ is drawn from
that distribution. The error is estimated as variance of the previous displacement values.
The predicted position of the particle $m$ is drawn according to:


```math 
\begin{pmatrix} i_{t}^{[m]}\\ d_{t}^{[m]}  \\\alpha_{t}^{[m]} \end{pmatrix} \leftarrow  \mathcal{N}_3(u_t^{[m]} + x_{t-1}^{[m]}, \begin{pmatrix}
    0 & 0 & 0\\
    0 & \epsilon(u_t) & 0\\
    0 & 0 & 0
\end{pmatrix})
```

If $d_{t}^{[m]}<0$, the particle $m$ estimates that the catheter left the current branch in backward direction, 
the position estimate is corrected according to:
```math 
x_{t}^{[m]} = \begin{pmatrix}
    k \\ l_k + d_{t}^{[m]} \\\alpha_{t}^{[m]} 
\end{pmatrix} 
```
$k$ is the index of the predecessor vessel, $l_k$ denotes the length of the predecessor vessel. 
If $l_k + d_{t}^{[m]} <0 $ displacement, the  branch update is recursively repeated until the displacement 
estimate of particle $x_{t}^{[m]} $ is positive. 


If $d_{t}^{[m]}>l_{i_{t-1}^{m}}$, the particle $m$ estimates that the catheter left the current branch in forward direction, 
the position estimate is corrected according to:
```math 
x_{t}^{[m]} = \begin{pmatrix}
    s \in_R  S \\ d_{t}^{[m]}  - l_{i_{t-1}^{m}}  \\\alpha_{t}^{[m]} \end{pmatrix}
```
$s$ is a random index drawn from the successor vessels, $l_{i_{t-1}^{m}}$ denotes the length of the current
vessel. If $d_{t}^{[m]} - l_{i_{t-1}^{m}} > l_{s}$, the branch update is repeated until the displacement 
estimate of particle $x_{t}^{[m]} $ is located between $0$ and the length of the estimated branch.

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
In the resampling step, the particle set is updated by drawing particles with replacement from the previous
particle set. The weight of the particle is proportional to the probability that a particle is drawn.
The resampling is performed by a low-variance-resampler.

### Injection Step
The injection step randomly varies the state estimates the 5% of particles with the lowest weight.


The alpha-variance injector randomly draws a new alpha value from a normal distribution with variance 0.1 centered
around the old alpha estimate. 
```math 
x_{t}^{[m]} = \begin{pmatrix}
    i_{t}^{m} \\ d_{t}^{[m]}   \\\alpha_{t}^{[m]} \leftarrow  \mathcal{N}(\alpha_{t}^{[m]}, 0.1)
\end{pmatrix} 
```

The alpha-variance injector randomly draws a new alpha value from a normal distribution with variance 0.1 centered
around the old alpha estimate and draws a random new location in the map. $I$ denotes the set of centerline indices
in the vessel centerline map, $l_{i_{t}^{m}}$ denotes the length of the vessel segment with index $i_{t}^{m}$.
```math 
x_{t}^{[m]} = \begin{pmatrix}
    i_{t}^{m} \in_R  I \\ d_{t}^{[m]} \in_R [1,..., l_{i_{t}^{m}}]   \\\alpha_{t}^{[m]} \leftarrow  \mathcal{N}(\alpha_{t}^{[m]}, 0.1)
\end{pmatrix} 
```

## License

## references
**[1]** Sutton, Erin E. et al. (2020). “Biologically Inspired Catheter for Endovascular
Sensing and Navigation.” In: Scientific reports 10.1, p. 5643. DOI: 10.1038/
s41598-020-62360-w.

**[2]** Ramadani, Ardit et al. (2022). Bioelectric Registration of Electromagnetic Tracking
and Preoperative Volume Data. DOI: 10.48550/arXiv.2206.10616

**[3]** Maier, Heiko, Heribert Schunkert, and Nassir Navab (2023). “Extending bioelectric
navigation for displacement and direction detection.” In: International
journal of computer assisted radiology and surgery. DOI: 10.1007/s11548-
023-02927-w.

**[4]** Ester, Martin et al. (1996). “A Density-Based Algorithm for Discovering Clus-
ters in Large Spatial Databases with Noise.” In: Knowledge Discovery and Data
Mining.