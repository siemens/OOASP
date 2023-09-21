Copyright (c) 2022 Siemens AG Oesterreich
SPDX-License-Identifier: MIT

# Documentation of Interactive Configurator

## API classes

### Knowledge Base

The Knowledge Bases are handled using the `OOASPKnowledgeBase` class in [ooasp/kb.py](ooasp/kb.py). This class provides useful functionality to load, edit, and visualize Knowledge Bases. The string representation of the objects of this class are ASP facts.

### Configuration

The Configurations are handled using the `OOASPConfiguration` class in [ooasp/config.py](ooasp/config.py). This class provides useful functionality to load, edit, and visualize Configurations.
Furthermore, it can serve as container for:
- partial configurations
- complete configurations
- configuration checks (constraint violations)
- available options (brave consequences)
- forced inferences (cautious consequences)

The string representation of the objects of this class are ASP facts.


### Interactive Configurator

The interactive Configurator API provides all functionality to create a configuration interactively. This is done by calling the methods provided by the `InteractiveConfigurator` class from [ooasp/interactive.py](ooasp/interactive.py). The process is done in a [multi-shot](#multi-shot-approach) way.


#### Tasks

The following tasks correspond to the only points of the interactive process where solving is performed. They are done for the current domain size and based on a (possibly empty) partial configuration `C`.

1. *Complete:* Getting a complete configuration extending `C`.
2. *Check:* Checking `C` for errors.
3. *Options:* Obtaining all possible classes, values, and associations to complete `C`.
4. *Inferences:* Obtaining the inferences that are obtained from `C` optimized to minimize errors. This means that it is the intersection of all stable models, where the lower bound constraint violations are minimized so that as many objects are associated as possible.


----
## Encodings

All encodings are put together using a single file:

- [ooasp/encodings/ooasp.lp](ooasp/encodings/ooasp.lp)

This file also introduces **external atoms** to differentiate the task that will be performed without the need for re-grounding. The truth value of those atoms will be defined externally inside the [Interactive Configurator](#interactive-configurator).

**Externals**

- **`guess`**  The [guessing](#guess) part is active. This external is used instead of the old predicate [`ooasp_configure`](../ooasp/ooasp_config.lp).

	Value of this external for the different tasks:
	Task |  Value |
	-----|---------
	*Complete*     |   `true`     |
	*Check*    |   `false`     |
	*Options*    |   `true`     |

- **`check_permanent_cv`**  The check part is active for [permanent constraints](#permanent-constraints). This refers only to the integrity constrains, however `ooasp_cv` atoms are always derived, regardless of the external values.

	Value of this external for the different tasks:
	Task |  Value |
	-----|---------
	*Complete*     |   `true`     |
	*Check*    |   `false`     |
	*Options*    |   `true`     |

Although this might seem contra-intuitive, this external should be false for the *Checking* task in order to have the `ooasp_cv` atoms as part of a stable model.

- **`check_potential_cv`**  The check part is active for [potential constraints](#potential-constraints). This refers only to the integrity constraints, however `ooasp_cv` atoms are always derived, regardless of the external values.

	Value of this external for the different tasks:
	Task |  Value |
	-----|---------
	*Complete*     |   `true`     |
	*Check*    |   `false`     |
	*Options*    |   `false`     |


### Auxiliary predicates

Auxiliary predicates used for both Knowledge Bases and Configurations can be found in the following files. Note that auxiliary predicates for the configuration are **grounded incrementally** (See [multi-shot](#multi-shot-approach)).

- [ooasp/encodings/ooasp_aux_kb.lp](ooasp/encodings/ooasp_aux_kb.lp)
- [ooasp/encodings/ooasp_aux_config.lp](ooasp/encodings/ooasp_aux_config.lp)


### Guess

The guessing section contains all choices to decide the class of an object, the associations, and the values. Note that the guessing is **grounded incrementally** (See [multi-shot](#multi-shot-approach)).

- [ooasp/encodings/ooasp_guess.lp](ooasp/encodings/ooasp_guess.lp)


### Constraints

Constraints will be **grounded incrementally** (See [multi-shot](#multi-shot-approach)).

- [ooasp/encodings/ooasp_check.lp](ooasp/encodings/ooasp_check.lp)

Constraints are defined using the `ooasp_cv/4` predicate:

**`ooasp_cv(CV_NAME,OBJECT,STR,ARGS)`**
- `CV_NAME`: The name of the constraint. Should be unique, as it is used for defining potential constraints
- `OBJECT`: The identifier of the object to which this constraint violation refers to. This is used to better visualize constraints and to allow incremental grounding.
- `STR`: A string describing the constraint. It can use place holders `{}`, which are filled with the arguments in `ARGS`.
- `ARGS`: A tuple with the arguments to format `STR`. Note that tuples with a single element need to be written as `(ARG,)`. 


**Domain specific constraints** are defined by the user in a different file, which can be provided when the [Interactive Configurator](#interactive-configurator) is created. Note that these will also be **grounded incrementally** (see [multi-shot](#multi-shot-approach)).

When writing domain specific constraint violations, one must consider that the grounding is done for each new object, so there needs to be a rule to cover the case of this new object taking the position of any object playing a role in the constraint violation.

#### Permanent constraints

Those constrains that can not longer be corrected by adding new values and associations. These constraints will make a configuration invalid and thus, are not provided as options for the user. By default all constraints are considered of this type, unless stated otherwise (see below [potential constraints](#potential-constraints)).

*For example: Upper-bound constraints or assigning an invalid value.*


#### Potential constraints

Those constraints that may be violated in the current (partial) configuration but can become satisfied at a later stage of the configuration process.

*For example: Lower-bound constraints, missing value for an attribute.*

Potential constraints are ignored when using brave reasoning in order to get all possible options for values and associations. They are only checked when the external `ooasp_potential_cv` is true. Nonetheless, the constraint violation atoms `ooasp_cv` for these constraints will still appear when checking the configuration for errors.

Potential constraints are defined using predicate `ooasp_potential_cv(CV_NAME)`, where `CV_NAME` is the name of the constraint violation appearing as the second argument of predicate `ooasp_cv`.


### User input

The user input corresponds to the current partial configuration `C` that is being constructed. This is added into the encoding using externals and it is **grounded incrementally** (See [multi-shot](#multi-shot-approach)).

- [ooasp/encodings/ooasp_user_input.lp](ooasp/encodings/ooasp_user_input.lp)

**Externals**

- **`user(ooasp_isa(CLASS,ID))`**
  The user assigned class `CLASS` to object `ID`

- **`user(ooasp_associated(ASSOC,ID1,ID2))`**
  The user associated `ID1` and `ID2` via `ASSOC`

- **`user(ooasp_attribute_value(N,ID,VALUE))`**
  The user selected value `VALUE` for attribute `N` of object `ID`

The truth value of these externals is defined by the [Interactive Configurator](#interactive-configurator) based on the current (partial) configuration that is being constructed using an object of class [OOASPConfiguration](#configuration).

The user externals are generated restricted by the possible classes that an object can have. This is defined by the argument `cls` passed in the grounding, which corresponds to the domain defined by `ooasp_domain(_,cls).`. Therefore, if the new object is grounded for a class `cls`, only valid attributes and associations for `cls` and its subclasses will be considered. This is summarized in the auxiliary predicate `counts_as(O,C)`, which states that object `O` can count as class `C`.


## Numerical attributes

Numerical attributes are treated using the system `fclingo`. This systems adds a founded condition while using `clorm` in the background. 
Attributes whose type is `int`, such as `nr_passengers`, `standing_room`, and `nr_seats` in the Metro example, are treated as variables with this system as explained below. Note that numerical values can also be treated as an enumeration using the type `enumint` instead. This option will consider all values in the defined range for predicate `ooasp_attr_value`, such as `frame_position` in the racks example.

### Usage

When an attribute `ATTR` is of type `int`, their value is defined the `fclingo` variable `ooasp_attr_fvalue(ATTR,O)`, which will be associated to the value of `ATTR` for object `O`.
These values can be compared using the theory symbol `&fsum`. For instance, in the following rule we use `&fsum{ooasp_attr_fvalue(A,new_object)}<MIN` to state that the value of `A` is smaller than `MIN` leading to a constraint violation. Notice that the variable `MIN` must be defined in a positive literal of the body.

```
ooasp_cv(value_outside_of_range,new_object,"Value for {} outside min range {}",(A,MIN)) :-
	 ooasp_attr(C,A,int),
	 ooasp_isa(C,new_object),
	 &fsum{ooasp_attr_fvalue(A,new_object)}<MIN,
	 ooasp_attr_minInclusive(C,A,MIN).
```

To check if a value is defined one can do so by checking if it is equal to itself. In the case of the next rule, if no value is defined, then the constraint violation is inferred.

```
ooasp_cv(no_value,new_object,"Missing value for {}",(A,)) :-
	ooasp_attr(C,A,int),
	ooasp_isa(C,new_object),
	not &fsum{ooasp_attr_fvalue(A,new_object)}=ooasp_attr_fvalue(A,new_object).
```

These type of attributes must be treated differently to the rest, therefore they require rules like to ones above to handle each case. Bellow we show the difference of writing a constraint violation using `ooasp_attr_value/3` and `ooasp_attr_fvalue/2`. Notice that in the second case, we directly compare the values by summing them up.

#### `ooasp_attr_value/3`
```
ooasp_cv(nrpassengers_neq_nrseats_plus_standingroom,new_object,"Number of passenges not adding up",(new_object,)):-
    ooasp_isa(wagon,new_object),
    ooasp_attr_value(nr_passengers,new_object,NRP),
    ooasp_attr_value(nr_seats,new_object,NRS),
    ooasp_attr_value(standing_room,new_object,S),
    NRP!=NRS+S.
```

#### `ooasp_attr_fvalue/2`
```
ooasp_cv(nrpassengers_sum,new_object,"Number of passenges not adding up",(new_object,)):-
    ooasp_isa(wagon,new_object),
    &fsum{ooasp_attr_fvalue(nr_seats,new_object);
          ooasp_attr_fvalue(standing_room,new_object)}!=
        ooasp_attr_fvalue(nr_passengers,new_object).
```

### Interactivity

The assigned values for these attributes are handled internally by the `fclingo `system and are only accessed after the models are found. Therefore, they are not considered in any brave or cautious consequences. This means that we do not know in advanced the possible values an attribute can take for a partial configuration. Interactively, this can be solve in different ways, such as using a slider instead of a dropdown or some other numerical input. For convenience, we keep the usage in the jupyter notebooks with dropdowns and add all possible values for the attribute, even though they might create an invalid configuration. Invialid configurations can still be checked and fixed in the UI. 


----

## Multi-shot approach

This approach intends to tackle the bottleneck issue of re-grounding rules multiple times after each change.


The rules are grounded for every new object that is introduced in an incremental way. The subprogram starting with the directive `#program domain(new_object, cls).`, which is split among several encoding files, will be grounded when a new object is introduced into the configuration. This new object will have the id `new_object` and can be instantiated to any subclass of class `cls`.

### Tips
When using this approach we must make sure that rules are grounded just once.
This means the `new_object` (which is the parameter of the grounding) must appear in the head of rules. Such requirement will assure that this head was never grounded before.

##### Example

Take for instance the following rule:

```prolog
#program domain(new_object).
ooasp_cv(no_instance_for_attribute,new_object,"Attribute {} not of selected class",(ATTR,)) :-
	ooasp_attribute(C1,ATTR,T),
	ooasp_attribute_value(ATTR,new_object,VALUE),
	not ooasp_isa(C1,new_object).
```

This rule will be grounded for a `new_object`, since this value appears in the head we know it hasn't been grounded before.

##### Example (Multiple positions)

In this example we want to generate the constraint violations when an association is not of the right class, using predicate `ooasp_associated(ASSOC,ID1,ID2)`. We must notice that our `new_object` could be either of the two values `ID1` or `ID2`, this means that we need two rules considering both cases.

```prolog
ooasp_cv(wrongtypeinassoc,new_object,"Associated by {} but is not of class {}",(ASSOC,C1)) :-
	ooasp_associated(ASSOC,new_object,_),
	ooasp_assoc(ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	not ooasp_isa(C1,new_object).

ooasp_cv(wrongtypeinassoc,new_object,"Associated by {} but is not of class {}",(ASSOC,C2)) :-
	ooasp_associated(ASSOC,_,new_object),
	ooasp_assoc(ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	not ooasp_isa(C2,new_object).
```


### Accumulative values

There are some rules that depend on atoms that are computed in an accumulative way. One of this values is the **arity**.

Consider the following rule:

```prolog
arity(new_object,ASSOC,ARITY):- ARITY = #count{ID2:ooasp_assoc(ASSOC,new_object,_,_,ID2,_,_)}.
```

This rule will gather the number of objects that `new_object` is associated to in association `ASSOC`. While this is correct at the moment you ground `new_object` this value will no longer be correct when new identifiers are grounded. This is because they were not part of the aggregate `#count` calculated before. Therefore, associations of `new_object` with any `ID>new_object` will not be counted.

In order to fix this issue we calculate the arity as follows:

```prolog
ooasp_arity( ASSOC, 1, new_object, ARITY, new_object) :-
	ooasp_assoc(ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	ooasp_isa(C1,new_object),
	ARITY = #count { ID2:ooasp_associated(ASSOC,new_object,ID2) }.

ooasp_arity( ASSOC, 2, new_object, ARITY, new_object) :-
	ooasp_assoc(ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	ooasp_isa(C2,new_object),
	ARITY = #count { ID1:ooasp_associated(ASSOC,ID1,new_object) }.
```

These rules compute the arity as shown before for the two possible positions of the new ID. The first one for position `1` and the second one for position `2`. Unlike in our previous rule, here, we also include the `new_object` as the last argument of `ooasp_arity`. We do so to identify that this value `ARITY` for the arity is only valid when `new_object` was grounded. This value can be seen as a step.

Next, we include any new associations that this `new_object` might have with previously grounded IDs and update their corresponding arity. This is done in the following rules:

```prolog
ooasp_arity( ASSOC, 1, ID1, ARITY+1, new_object) :-
	ooasp_arity( ASSOC, 1, ID1, ARITY, new_object-1),
	ooasp_associated(ASSOC, ID1, new_object).

ooasp_arity( ASSOC, 2, ID2, ARITY+1, new_object) :-
	ooasp_arity( ASSOC, 2, ID2, ARITY, new_object-1),
	ooasp_associated(ASSOC, new_object, ID2).

ooasp_arity( ASSOC, 1, ID1, ARITY, new_object) :-
	ooasp_arity( ASSOC, 1, ID1, ARITY, new_object-1),
	not ooasp_associated(ASSOC, ID1, new_object).

ooasp_arity( ASSOC, 2, ID2, ARITY, new_object) :-
	ooasp_arity( ASSOC, 2, ID2, ARITY, new_object-1),
	not ooasp_associated(ASSOC, new_object, ID2).
```

These rules update the values like a counter without using `#count`. Note that the last argument of the `ooasp_arity` is `new_object`, serving two purposes: first, to identify that this is a valid arity for that moment, and second to ensure that this is a new head that hasn't been grounded before.


#### Using accumulative values

If we want to use these accumulative values in another rule there is one more detail to consider.

**Example**

Imagine the rule:

```prolog
ooasp_cv(wrongass,ID,"Wrong for {}",(ID,)) :-
    ooasp_arity(assoc1,1,ID,ARITY,STEP), ARITY!=4.
```

This rule is saying that for association `assoc1` the object `ID` in position `1` should have exactly `4` objects associated. We first notice that this is not using the `new_object`. We can include this by doing:

```prolog
ooasp_cv(wrongass,new_object,"Wrong for {}",(new_object,)) :-
    ooasp_arity(assoc1,1,new_object,ARITY,STEP), ARITY!=4.
```

However, we also need to make sure that we consider the predicate `ooasp_arity` that is most up to date. Therefore we must know what the current step is. This is done using another external, in our case **`active(STEP)`**. When this external is true it means that we should consider the arity at step `STEP` as follows:

```prolog
ooasp_cv(wrongass,new_object,"Wrong for {}",(new_object,)) :-
    ooasp_arity(assoc1,1,new_object,ARITY,STEP), ARITY!=4, active(STEP).
```

Notice that we want to ground this rule for the `new_object` this means that `STEP` will be `new_object`.

```prolog
ooasp_cv(wrongass,new_object,"Wrong for {}",(new_object,)) :-
    ooasp_arity(assoc1,1,new_object,ARITY,new_object), ARITY!=4, active(new_object).
```

Since we updated the values of `ooasp_arity` of all previous IDs as well, we also need to ground the corresponding rules for those, yielding the rule:

```prolog
ooasp_cv(wrongass,ID,"Wrong for {}",(ID,)) :-
    ooasp_arity(assoc1,1,ID,ARITY,new_object), ARITY!=4, active(new_object).
```

This rule however, remains with the issue of not having `new_object` in the head. We can fix this by just including it in the cv arguments, even if is never used:

```prolog
ooasp_cv(wrongass,ID,"Wrong for {}",(ID,new_object)) :-
    ooasp_arity(assoc1,1,ID,ARITY,new_object), ARITY!=4, active(new_object).
```

Lastly, we might notice that this constraint is actually considering two different requirements: `ASSOC>=4` and `ASSOC<=4`. Where the first one is a [Potential Constraint](#potential-constraints) since having just `3` associations can still be completed into an accepting configuration, whereas `ASSOC<=4` is a [Permanent Constraint](#permanent-constraints) since having more than `4` values can not longer be complected into a valid configuration.

Therefore, we arrive at our final rules:

```prolog
ooasp_cv(wrongass_lower,ID,"Wrong < for {}",(ID,new_object)) :-
    ooasp_arity(assoc1,1,ID,ARITY,new_object), ARITY<4, active(new_object).
ooasp_cv(wrongass_upper,ID,"Wrong > for {}",(ID,new_object)) :-
    ooasp_arity(assoc1,1,ID,ARITY,new_object), ARITY>4, active(new_object).
```

Where the following fact must also included:

```prolog
ooasp_potential_cv(wrongass_lower).
```

#### Efficiency

Even though the explanation above corresponds to a correct solution, it is not efficient. Generally speaking, using the computed value of an aggregate such as `#count` in the head of the rule accounts for additional grounding. Ideally, this value should be used only in the body of the rule. This observation leads us to a more efficient solution, where the aggregate is used directly in the constraint.

```prolog
ooasp_cv(upperbound,ID1,"Upperbound wrong",(new_object)):-
	ooasp_assoc_limit(ASSOC,max,OPT,C,CMAX),
	ooasp_isa(C,ID1),
	#count { ID2:ooasp_associated_general(ASSOC,OPT,ID1,ID2) } > CMAX,
	active(new_object).
```

Notice that, as before, this rule must consider the `active(new_object)` to define in which step the constraint is violated. The count, however, does not depend on the `new_object`.

We use here two auxiliary predicates to avoid having to repeat the rule:

- **`ooasp_assoc_limit(ASSOC,max,POS,C,CMAX,C2)`**
  The association `ASSOC` has a maximum limit of `CMAX` for objects of class `C` at `POS`, where `POS` is `1` or `2` and refers to one end of the association (1: left end, 2: right end), where the other side of the associations are objects of class `C2`.
  *Example: `ooasp_assoc_limit(ass,min,1,racks,10)`:
	In the association `ass`, each `racks` object must be associated to at least `10` elements*

- **`ooasp_associated_general(ASSOC,POS,ID1,ID2)`**
  Object `ID1` appearing in position `POS` of association `ASSOC` is associated to object `ID2`
  *Example: `ooasp_associated_general(c1,ass,2,23,10)`: object `23` of the second class of association `ass` is associated with object `10`*

--- 

## Incremental solving

This multi-shot encoding can directly be used for incremental solving. With this idea we ground for the current objects and try to find a configuration using Task 1 *Complete*, if there is no complete configuration (returns UNSAT) with this number of objects, we ground for one more object and repeat the process until we have a satisfiable answer.

This incremental process find the smallest configuration. However, it has the drawback that right before getting the satisfiable answer the solving time increases since it has to look over the whole search space, which impacts in performance.

###  Create required

Creates all the objects required by the current objects, which is done as follows:

- Gets the cautious consequences for the program where potential cv can be violated
- This gives us the violations that exist in all the models.
- This solve call adds an optimization so that we consider lower bond violations that already associated as many objects as possible
- For every existing objet, we check the lower bound constraint violations associated to that object
- This predicates already have the information of how many objects where associated and what the minimum was
- Based on this information we create and associate the required objects of the specific type

### Smart incremental solving 

In the smart incremental solving the performance issue is tackled by adding inferences in every iteration.

This is done using the create required task in three steps:
- Try to get a solution for the current number of objects, 
- If this is UNSAT then call create required
- If no object is added with the create required, then proceed as in normal incremental by adding one object of type `object``





## Advanced features to simplify writing domain specific constraint violations

### Association specialization

Association specializations will specialize the lower and upper bound of an association for subclasses.

For example, the association `rack_frames` between class `rack` and `frame` is defined by the atom `ooasp_assoc(rack_frames,rack,1,1,frame,4,8)`.
The racks example limits the number of racks associated to the racks subclass `rackSingle` to be exactly `4`. This is achieved by adding an association specialization with name `rack_framesS` which specializes `rack_frames`, by the atom `ooasp_assoc_specialization(rack_framesS,rack_frames)`. This means that all `rack_frameS` associations are also `rack_frames` associations. Then, the upper and lowe bound can be redefined when the association is defined in `ooasp_assoc(rack_framesS,rackSingle,0,1,frame,4,4)`. 

While upper bounds can be restricted, lower bounds are relaxed. So that the lower bounds of an association specialization are smaller or equal to the original one.
Notice that in our example the lower bound of how many racks singles are associated to a frame is now `0`, otherwise frames would be forced to be associated to a `rackSingle`. The requirement of having some rack associated comes from the super association `rack_frames`. 


### Specialized constraint violations

Specialized constraint violations are those used in different instances but not encoded in the knowledge base. Some of them are the following:

- **(unique)** all attribute values of objects in an association are different 
- **(same)** all attribute values of objects in an association are equal (exceptions)
- **(table)** which value combinations are allowed
- **(specialization)** attribute value determines the type of objects

These constraints can be defined in the knowledge base using the predicate `ooasp_special_cv/2`, where the first argument is the name of the constraint and the second one has any additional information needed. To implement a specialized constraint violation, the file [ooasp/encodings/ooa_checksp.lp](ooasp/encodings_check/ooasp.lp) must be extended with the needed constraints.
This process was done for the  **unique** constraint violation. It is used in the knowladge base of the racks example, to make sure that the frame positions of all frames associated to a rack are different. In this case the second argument is a tuple `(ASSOCIATION, CLASS, ATTRIBUTE)`

```
ooasp_special_cv(unique, (rack_frames, frame, frame_position)).
```

The corresponding rules are defined in [ooasp/encodings/ooasp_check.lp](ooasp/encodings/ooasp_check.lp). 





