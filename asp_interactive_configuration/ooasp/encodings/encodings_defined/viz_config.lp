% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

#defined ooasp_isa/3.

graph(config).

attr(graph_nodes, config, shape, rectangle).
attr(graph, config, splines, ortho).
attr(graph, config, nodesep, "1").
attr(graph, config, rankdir, "TB").
attr(graph, config, fontsize, 20).
attr(graph, config, (label,0), "Configuration "):-ooasp_configuration(KB,Config).
attr(graph, config, (label,1), Config):-ooasp_configuration(KB,Config).

% Objects without class as Nodes
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

% All nodes
attr(node, Object_id, label, @concat("<<TABLE BORDER='0' CELLBORDER='1' CELLSPACING='0' CELLPADDING='1'>",
                                        "<TR><TD><FONT COLOR='{{color}}'><B>{{isa}} ({{id}})</B><BR/>{{class}}</FONT></TD></TR><TR><TD ALIGN='right'> ",
                                        "{% set attr = attr|default({}) %}{% for k, v in attr.items() %}{{v}} {% endfor %}",
                                        "</TD></TR></TABLE>>")):- any_node(Object_id).
attr(node, Object_id,  (label,class), @stringify(Class,true)):- any_node(Object_id),ooasp_domain(Class,Object_id).
attr(node, Object_id,  (label,isa), @stringify(Class,true)):- any_node(Object_id),isa_smallest(Class,Object_id).
attr(node, Object_id,  (label,color), black):- node(Object_id), not domain_node(_,Object_id).
attr(node, Object_id,  (label,color), grey):- node(Object_id), domain_node(_,Object_id).
attr(node, Object_id,  (label,id), Object_id):- any_node(Object_id).
attr(node, Object_id, style, "filled"):- any_node(Object_id).

% Domain nodes
attr(node, Object_id, fillcolor, "#C4C4C420"):- domain_node(_,Object_id).
attr(node, Object_id, color, "#C4C4C4"):- domain_node(_,Object_id).

% Is a nodes
attr(node, Object_id, fillcolor, "#E7D5EA"):- isa_node(_,Object_id).
% attr(node, Object_id, color, "black"):- isa_node(_,Object_id).

% Leaf nodes
attr(node, T, fillcolor, "#D2D2E0"):- leaf_node(_,T).

% Node border
attr(node, T, color, "black"):- node(T), not domain_node(_,T).
attr(node, T, margin, 0):- node(T).
attr(node, T, width, 0):- node(T).
attr(node, T, hight, 0):- node(T).

% User selections in green
attr(node, Object_id, fontcolor, "#0DB144"):- user(ooasp_isa_leaf(Class,Object_id)).

% Add arguments to nodes
attr(node, Object_id, (label,attr,Attr_name), @argument_str(Attr_name,Value,"black")):-
    ooasp_attr_value(Attr_name,Object_id,Value),
    not user(ooasp_attr_value(Attr_name,Object_id,Value)).
attr(node, Object_id, (label,attr,Attr_name), @argument_str(Attr_name,Value,"#0DB144")):-
    ooasp_attr_value(Attr_name,Object_id,Value),
    user(ooasp_attr_value(Attr_name,Object_id,Value)).


% Associations
edge((Object_id1,Object_id2)) :-ooasp_associated(Name,Object_id1,Object_id2).

attr(edge, (Object_id1,Object_id2), xlabel, Name) :- ooasp_associated(Name,Object_id1,Object_id2).
attr(edge, (Object_id1,Object_id2), color, "#0DB144") :- user(ooasp_associated(Name,Object_id1,Object_id2)).
attr(edge, (Object_id1,Object_id2), fontcolor, "#0DB144") :- user(ooasp_associated(Name,Object_id1,Object_id2)).



#script (python)
from clingo.symbol import String

def argument_str(name,type,color):
    s = f"<FONT COLOR='{color.string}'>" + str(name) + " = " + "<I> "+ str(type)  + "</I></FONT><br ALIGN='left'/> "
    return String(s)

#end.
