# Corner cases for benchmarking and inspecting


## Lowerbound

### The 9 frames

```console
python ooasp/run.py --frame 9
```

This case is similar with 17 frames but in that case it gets really slow.

#### Smart expansion

1. *(object based)* One frame complains about needing a rack. So it is added
2. *(global upper)* The single frames don't know a rack is missing because they all think they can use the existing one. So the global constraint counts that if there is 9 frames the upper bound of the rack is filled and there has to be one more. So a second rack is added
3. Nothing else left to infer because both racks think they can fill their lower bound for frames with the existing ones. But this is not true.
4. We solve and fail so we add one more object
5. We solve and fail so we add one more object
6. We solve and fail so we add one more object
7. Solves and finds configuration!

#### Using bounds

*To be filled*


## Global lowerbound

### 2 frames 2 racks


```console
python ooasp/run.py --frame 2 --rack 2
```

#### Smart expansion

1. *(object based)* One rack requires two more frames, then two more frames are added
2.  *(object based)* The second rack requires two more frames. Can't be the ones that where just added in step 1 because they are associated to the first rack. Notice that both racks think they can use the first two frames.
3.  *(global lower)* The bounds calculation says that we have a 1 to n..m relation so we need at least 8 frames globally to complete it. So it adds two more
4. Nothing else left to infer
5. Solves and finds configuration!

#### Using bounds

*To be filled*

