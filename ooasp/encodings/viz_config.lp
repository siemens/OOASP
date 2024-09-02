% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

#defined ooasp_isa/3.

graph(config).
#const color_green = "#0DB144".

attr(graph_nodes, config, shape, rectangle).
attr(graph, config, dpi, 300).
attr(graph, config, splines, ortho).
attr(graph, config, nodesep, "1").
attr(graph, config, rankdir, "TB").
attr(graph, config, size, "40,100").
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
                                        "{% set cv = cv|default({}) %}{% for k, v in cv.items() %}{{v}} {% endfor %}",
                                        "</TD></TR></TABLE>>")):- any_node(Object_id).
attr(node, Object_id,  (label,class), @stringify(Class,true)):- any_node(Object_id),ooasp_domain(Class,Object_id).
attr(node, Object_id,  (label,isa), @stringify(Class,true)):- any_node(Object_id),isa_smallest(Class,Object_id).
attr(node, Object_id,  (label,color), black):- node(Object_id), not domain_node(_,Object_id), user(ooasp_isa(_,Object_id)).
% Case for objects not instantiated
attr(node, Object_id,  (label,color), grey):- node(Object_id), domain_node(_,Object_id).
attr(node, Object_id,  (label,color), color_green):- node(Object_id), not user(ooasp_isa(_,Object_id)), ooasp_isa(_,Object_id).
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

% Add arguments to nodes
attr(node, Object_id, (label,attr,Attr_name), @argument_str(Attr_name,Value,"black")):-
    ooasp_attr_value(Attr_name,Object_id,Value),
    user(ooasp_attr_value(Attr_name,Object_id,Value)).
attr(node, Object_id, (label,attr,Attr_name), @argument_str(Attr_name,Value,color_green)):-
    ooasp_attr_value(Attr_name,Object_id,Value),
    not user(ooasp_attr_value(Attr_name,Object_id,Value)).

% Add cvs to nodes
attr(node, Object_id, (label,cv,(Name,Object_id,Args)), @cv_str(Name,Mes,Args)):-
    ooasp_cv(Name,Object_id,Mes,Args).


% Associations
edge((Object_id1,Object_id2)) :-ooasp_associated(Name,Object_id1,Object_id2).

attr(edge,(Object_id1,Object_id2), xlabel, "<{{name}} <br/><FONT POINT-SIZE='10'> {{super}}</FONT>>"):-ooasp_associated(Name,Object_id1,Object_id2).
attr(edge,(Object_id1,Object_id2), (xlabel,name), Name):-ooasp_associated(Name,Object_id1,Object_id2), not ooasp_assoc_specialization(_,Name).
attr(edge,(Object_id1,Object_id2), (xlabel,super), Super):-ooasp_associated(Name,Object_id1,Object_id2),ooasp_assoc_specialization(Name,Super).

attr(edge, (Object_id1,Object_id2), color, color_green) :- ooasp_associated(Name,Object_id1,Object_id2), not user(ooasp_associated(Name,Object_id1,Object_id2)),not ooasp_assoc_specialization(_,Name).
attr(edge, (Object_id1,Object_id2), fontcolor, color_green) :- ooasp_associated(Name,Object_id1,Object_id2), not user(ooasp_associated(Name,Object_id1,Object_id2)),not ooasp_assoc_specialization(_,Name).



#script (python)
from clingo.symbol import String
import textwrap

def argument_str(name,type,color):
    s = f"<FONT COLOR='{color.string}'>" + str(name) + " = " + "<I> "+ str(type)  + "</I></FONT><br ALIGN='left'/> "
    return String(s)

def cv_str(name,message,args):
    args_symbols = [str(a) for a in args.arguments]
    formatted_message = f"{message.string.format(*args_symbols)}"
    s_wrap_list = textwrap.wrap(formatted_message, 40)
    message_wrapped = "<br ALIGN='left'/>   ".join(s_wrap_list)
    s = f"<FONT COLOR='red'><I> "+ message_wrapped  + "</I> (" + str(name) + ") </FONT><br ALIGN='left'/> "
    return String(s)

#end.
