Copyright (c) 2022 Siemens AG Oesterreich
SPDX-License-Identifier: MIT

# Documentation of Interactive Configurator

## API classes

### Knowledge Base

The Knowledge Bases are handled using the `OOASPKnowledgeBase` class in [ooasp/kb.py](ooasp/kb.py). This class provides useful functionality to load, edit, and visualize Knowledge Bases. The string representation of the objects of this class are ASP facts.

### Configuration

The Configurations are handled using the `OOASPConfiguration` class in [ooasp/config.py](ooasp/config.py). This class provides useful functionality to load, edit, and visualize Configurations.
Furthermore, it can serve as container for partial configurations, complete configurations, configuration checks and available options for a configuration. The string representation of the objects of this class are ASP facts.


### Interactive Configurator

The interactive Configurator API provides all functionality to create a configuration interactively. This is done by calling the methods provided by the `InteractiveConfigurator` class from [ooasp/interactive.py](ooasp/interactive.py). The process is done in a [multi-shot](#multi-shot-approach) way.


#### Tasks

The following tasks correspond to the only points of the interactive process where solving is performed. They are done for the current domain size and based on a (possibly empty) partial configuration `C`. 

1. *Complete:* Getting a complete configuration extending `C`.
2. *Check:* Checking `C` for errors.
3. *Options:* Obtaining all possible classes for the objects, values for the attributes, and associations to complete `C`. 


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

- **`check`**  The check part is active for [complete constraints](#complete-constraints). This refers only to the integrity constrains, however `ooasp_cv` atoms are always derived, regardless of the external values.
  
	Value of this external for the different tasks:
	Task |  Value |
	-----|---------
	*Complete*     |   `true`     |
	*Check*    |   `false`     |
	*Options*    |   `true`     |

Although this might seam contra-intuitive, this external should be false for the *Checking* task in order to have the `ooasp_cv` atoms as part of a stable model.

- **`check_partial_cv`**  The check part is active for [partial constraints](#partial-constraints). This refers only to the integrity constraints, however `ooasp_cv` atoms are always derived, regardless of the external values.
  
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

The guessing section contains all choices to decide the leaf class of an object, the associations, and the values. Note that the guessing is **grounded incrementally** (See [multi-shot](#multi-shot-approach)).

- [ooasp/encodings/ooasp_guess.lp](ooasp/encodings/ooasp_guess.lp)


### Constraints

Constraints will be **grounded incrementally** (See [multi-shot](#multi-shot-approach)).

- [ooasp/encodings/ooasp_check.lp](ooasp/encodings/ooasp_check.lp)
  
Constraints are defined using predicate:

**`ooasp_cv(CONFIG,CV_NAME,OBJECT,STR,ARGS)`**
- `CONFIG`: The name of the configuration
- `CV_NAME`: The name of the constraint. Should be unique, as it is used for defining partial constraints
- `OBJECT`: The identifier of the object to which this constraint violation refers to. This is used to better visualize constraints and to allow incremental grounding.
- `STR`: A string describing the constraint. It can use place holders `{}`, which are filled with the arguments in `ARGS`.
- `ARGS`: A tuple with the arguments to format `STR`. Note that tuples with a single element need to be written as `(ARG,)`



**Domain specific constrains** are defined by the user in a different file, which can be provided when the [Interactive Configurator](#interactive-configurator) is created. Note that these will also be **grounded incrementally** (See [multi-shot](#multi-shot-approach)).

#### Complete constraints

Those constrains that can not longer be corrected by adding new values and associations. These constraints will make a configuration invalid and thus, are not provided as options for the user. By default all constraints are considered of this type, unless stated otherwise (see bellow [Partial constrains](#partial-constraints)).

*For example: Upper bound constraints or assigning an invalid value*


#### Partial constraints

Those constraints that may be violated in the current (partial) configuration but can become satisfied at a later stage of the configuration process. 

*For example: Lower bound constraints, missing value for an attribute.*

Partial constraints are ignored when using brave reasoning in order to get all possible options for values and associations. They are only checked when the external `ooasp_partial_cv` is true. Nonetheless, the constraint violation atoms `ooasp_cv` for this constrains will still appear when checking the configuration for errors. 

Partial constraints are defined using predicate `ooasp_partial_cv(CV_NAME)`, where `CV_NAME` is the name of the constraint violation appearing as the second argument of predicate `ooasp_cv`.


### User input

The user input corresponds to the current partial configuration `C` that is being constructed. This is added into the encoding using externals and it is **grounded incrementally** (See [multi-shot](#multi-shot-approach)).

- [ooasp/encodings/ooasp_user_input.lp](ooasp/encodings/ooasp_user_input.lp)

**Externals**

- **`user(ooasp_isa_leaf(CONFIG,LEAFCLASS,ID))`**
  The user assigned a leaf class to an object `ID`

- **`user(ooasp_associated(CONFIG,ASSOC,ID1,ID2))`**
  The user associated `ID1` and `ID2`

- **`user(ooasp_attribute_value(CONFIG,N,ID,VALUE))`**
  The user selected a value for object `ID`

The truth value of this externals is defined by the [Interactive Configurator](#interactive-configurator) based on the current (partial) configuration that is being constructed using an object of class [Config](#configuration). 


----

## Multi shot approach

This approach intends to tackle the bottle neck issue of re-grounding rules multiple times after each change. 



The rules are grounded for every new object that is introduced in an incremental way. All encodings that starting with the directive `#program domain(new_id).` will be grounded when a new object is introduced into the configuration. This new object will have the id `new_id`.

### Tips
When using this approach we must make sure that rules are grounded just once. 
This means the `new_id` (which is the parameter of the grounding) must appear in the head of rules. Such requirement will assure that this head was never grounded before.

##### Example

Take for instance the following rule:

```prolog
#program domain(new_id).
ooasp_cv(CONFIG,no_instance_for_attribute,new_id,"Attribute {} not of selected class",(ATTR,)) :- 
	ooasp_attribute(V,C1,ATTR,T),
	ooasp_attribute_value(CONFIG,ATTR,new_id,VALUE),
	not ooasp_isa(CONFIG,C1,new_id).
```

This rule will be grounded for a `new_id`, since this value appears in the head we know it hasn't been grounded before.

##### Example (Multiple positions)

In this example we want to generate the constraint violations when an association is not of the right class, using on predicate `ooasp_associated(CONFIG,ASSOC,ID1,ID2)`. We must notice that our `new_id` could be either of the two values `ID1` or `ID2`, this means that we need two rules considering both cases.

```prolog
ooasp_cv(CONFIG,wrongtypeinassoc,new_id,"Associated by {} but is not of class {}",(ASSOC,C1)) :-
	ooasp_configuration(V,CONFIG),
	ooasp_associated(CONFIG,ASSOC,new_id,_),
	ooasp_assoc(V,ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	not ooasp_isa(CONFIG,C1,new_id).

ooasp_cv(CONFIG,wrongtypeinassoc,new_id,"Associated by {} but is not of class {}",(ASSOC,C2)) :-
	ooasp_configuration(V,CONFIG),
	ooasp_associated(CONFIG,ASSOC,_,new_id),
	ooasp_assoc(V,ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	not ooasp_isa(CONFIG,C2,new_id).
```


### Accumulative values

There are some rules that depend on atoms that are computed an an accumulative way. One of this values is the **arity**. 

Consider the following rule:

```prolog
arity(new_id,ASSOC,ARITY):- ARITY = #count{ID2:ooasp_assoc(V,ASSOC,new_id,_,_,ID2,_,_)}.
```

This rule will gather the number of objects that `new_id` is associated to in association `ASSOC`. While this is correct at the moment you ground `new_id` this value will not longer be correct when new identifiers are grounded. This is because they are were not part of the aggregate `#count` calculated before. Therefore, associations of `new_id` with any `ID>new_id` will not be counted. 

In order to fix this issue we calculate the arity as follows:

```prolog
ooasp_arity(CONFIG, ASSOC, 1, new_id, ARITY, new_id) :-
	ooasp_configuration(V,CONFIG),
	ooasp_assoc(V,ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	ooasp_isa(CONFIG,C1,new_id),
	ARITY = #count { ID2:ooasp_associated(CONFIG,ASSOC,new_id,ID2) }.

ooasp_arity(CONFIG, ASSOC, 2, new_id, ARITY, new_id) :-
	ooasp_configuration(V,CONFIG),
	ooasp_assoc(V,ASSOC,C1,C1MIN,C1MAX,C2,C2MIN,C2MAX),
	ooasp_isa(CONFIG,C2,new_id),
	ARITY = #count { ID1:ooasp_associated(CONFIG,ASSOC,ID1,new_id) }.
```

These rules compute the arity as shown before for the two possible positions of the new ID. The first one for position `1` and the second one for position `2`. Unlike in our previous rule, here, we also include the `new_id` as the last argument of `ooasp_arity`. We do so to identify that this value `ARITY` for the arity is only valid when `new_id` was grounded. This value can be seen as a step.

Next, we include any new associations that this `new_id` might have with previously grounded ids and update their corresponding arity. This is done in the following rules:

```prolog
ooasp_arity(CONFIG, ASSOC, 1, ID1, ARITY+1, new_id) :- 
	ooasp_arity(CONFIG, ASSOC, 1, ID1, ARITY, new_id-1),
	ooasp_associated(CONFIG,ASSOC, ID1, new_id).

ooasp_arity(CONFIG, ASSOC, 2, ID2, ARITY+1, new_id) :- 
	ooasp_arity(CONFIG, ASSOC, 2, ID2, ARITY, new_id-1),
	ooasp_associated(CONFIG,ASSOC, new_id, ID2).

ooasp_arity(CONFIG, ASSOC, 1, ID1, ARITY, new_id) :- 
	ooasp_arity(CONFIG, ASSOC, 1, ID1, ARITY, new_id-1),
	not ooasp_associated(CONFIG,ASSOC, ID1, new_id).

ooasp_arity(CONFIG, ASSOC, 2, ID2, ARITY, new_id) :- 
	ooasp_arity(CONFIG, ASSOC, 2, ID2, ARITY, new_id-1),
	not ooasp_associated(CONFIG,ASSOC, new_id, ID2).
```

These rules update the values like a counter without using `#count`. Note that the last argument of the `ooasp_arity` is `new_id`, serving two proposes: first, to identify that this is a valid arity for that moment, and second to ensure that this is a new head that hasn't been grounded before.


#### Using accumulative values

If we want to use this accumulative values in another rule there is one more detail to consider. 

**Example**

Image the rule:

```prolog
ooasp_cv(CONFIG,wrongass,ID,"Wrong for {}",(ID,)) :- 
    ooasp_arity(CONFIG,assoc1,1,ID,ARITY,STEP), ARITY!=4.
```

This rule is saying that for association `assoc1` any the object `ID` in position `1` should have exactly `4` objects associated. We first notice that this is not using the `new_id`. We can include this by doing:

```prolog
ooasp_cv(CONFIG,wrongass,new_id,"Wrong for {}",(new_id,)) :- 
    ooasp_arity(CONFIG,assoc1,1,new_id,ARITY,STEP), ARITY!=4.
```

However, we also need to make sure that we consider the predicate `ooasp_arity` that is most up to date. Therefore we must know what the current step is. This is done using another external, in our case **`active(STEP)`**. When this external is true it means that we should consider the arity at step `STEP` as follows:

```prolog
ooasp_cv(CONFIG,wrongass,new_id,"Wrong for {}",(new_id,)) :- 
    ooasp_arity(CONFIG,assoc1,1,new_id,ARITY,STEP), ARITY!=4, active(STEP).
```

Notice that we want to ground this rule for the `new_id` this means that `STEP` will be `new_id`. 

```prolog
ooasp_cv(CONFIG,wrongass,new_id,"Wrong for {}",(new_id,)) :- 
    ooasp_arity(CONFIG,assoc1,1,new_id,ARITY,new_id), ARITY!=4, active(new_id).
```

Since we updated the values of `ooasp_arity` of all previous ids as well, we also need to ground the corresponding rules for those, yielding the rule:

```prolog
ooasp_cv(CONFIG,wrongass,ID,"Wrong for {}",(ID,)) :- 
    ooasp_arity(CONFIG,assoc1,1,ID,ARITY,new_id), ARITY!=4, active(new_id).
```

This rule however, remains with the issue of not having `new_id` in the head. We can fix this by just including it in the cv arguments, even if is never used:

```prolog
ooasp_cv(CONFIG,wrongass,ID,"Wrong for {}",(ID,new_id)) :- 
    ooasp_arity(CONFIG,assoc1,1,ID,ARITY,new_id), ARITY!=4, active(new_id).
```

Lastly, we might notice that this constraint is actually considering two different requirements: `ASSOC>=4` and `ASSOC<=4`. Where the first one is a [Partial Constraint](#partial-constraints) since having just `3` associations can still be completed into an accepting configuration, whereas `ASSOC<=4` is a [Complete Constraint](#complete-constraints) since having more than `4` values can not longer be complected into a valid configuration.

Therefore, we arrive at our final rules:

```prolog
ooasp_cv(CONFIG,wrongass_lower,ID,"Wrong < for {}",(ID,new_id)) :- 
    ooasp_arity(CONFIG,assoc1,1,ID,ARITY,new_id), ARITY<4, active(new_id).
ooasp_cv(CONFIG,wrongass_upper,ID,"Wrong > for {}",(ID,new_id)) :- 
    ooasp_arity(CONFIG,assoc1,1,ID,ARITY,new_id), ARITY>4, active(new_id).
```

Where the following fact must also included:

```prolog
ooasp_partial_cv(wrongass_lower).
```

#### Efficiency

Even though the explanation above corresponds to a correct solution, it is not efficient. Generally speaking, using the computed value of an aggregate such as `#count` in the head of the rule accounts for additional grounding. Ideally, this value should be used only in the body of the rule. This observations leads us to a more efficient solution, where the aggregate is used directly in the constraint. 

```prolog
ooasp_cv(CONFIG,upperbound,ID1,"Upperbound wrong",(new_id)):-
	ooasp_configuration(V,CONFIG),
	ooasp_assoc_limit(V,ASSOC,max,OPT,C,CMAX),
	ooasp_isa(CONFIG,C,ID1),
	#count { ID2:ooasp_associated_general(CONFIG,ASSOC,OPT,ID1,ID2) } > CMAX,
	active(new_id).
```

Notice that, as before, this rule must consider the `active(new_id)` to define in which step the constraint is violated. The count, however, does not depend on the `new_id`. 

We use here two axillary predicates to avoid having to repeat the rule:

- **`ooasp_assoc_limit(V,ASSOC,max,OPT,C,CMAX)`**
  The association `ASSOC` has a maximum limit of `MAX` when an object of class `C` is of class type `OPT`, where `OPT` is `1` or `2` .
  *Example: `ooasp_assoc_limit(V,ass,min,1,racks,10)`
	The association `ass` must be from a `racks` element as class `C1` to at least `10` elements*

- **`ooasp_associated_general(CONFIG,ASSOC,OPT,ID1,ID2)`**
  Object `ID1` appearing in position `OPT` of association `ASSOC` is associated to object `ID2`
  *Example: `ooasp_associated_general(c1,ass,2,23,10)` object `23` is the class `C2` of association `ass` with object `10`*

### Incremental solving 

This multi shot encoding can directly be used for incremental solving. With this idea we can ground for id `1` and try to find a configuration using Task 1 *Complete*, if there is no complete configuration (returns UNSAT) with this many object, we ground for the next object `2` and repeat the process until we have a satisfiable answer. 

