domain_node(Class,Object_id) :- ooasp_domain(Class,Object_id), not ooasp_isa(_,Object_id).
isa_node(ClassIsA,Object_id) :- ooasp_domain(Class,Object_id), ooasp_isa(ClassIsA,Object_id), not ooasp_isa_leaf(_,Object_id).
leaf_node(Class,Object_id) :- ooasp_isa_leaf(Class,Object_id), ooasp_class(Class).
isa_smallest(SUPER,Object_id) :-
    ooasp_isa(SUPER,Object_id),
	not ooasp_isa(SUB, Object_id): ooasp_subclass(SUB,SUPER).
ooasp_isa_leaf(C,Object_id) :-
    ooasp_isa(C,Object_id),
	ooasp_leafclass(C).

any_node(Object_id):- domain_node(Class,Object_id).
any_node(Object_id):- leaf_node(Class,Object_id).
any_node(Object_id):- isa_node(Class,Object_id).
node(Object_id) :- any_node(Object_id).
