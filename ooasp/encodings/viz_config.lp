% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

#defined ooasp_isa/3.
graph(config).
#const color_green = "#0DB144".

attr(graph_nodes, config, shape, rectangle).
attr(graph, config, splines, ortho).
attr(graph, config, nodesep, "1").
attr(graph, config, rankdir, "TB").

attr(graph, config, dpi, 65).
% attr(graph, config, size, "40,100").
% attr(graph, config, (label,0), "Configuration "):-ooasp_configuration(KB,Config).
% attr(graph, config, (label,1), Config):-ooasp_configuration(KB,Config).

% Objects without class as Nodes
#include "viz_config_nodes.lp".
#include "ooasp_defined.lp".

% All nodes
attr(node, Object_id, label, @concat("<<TABLE BGCOLOR='{{bgcolor}}' BORDER='0' CELLBORDER='1' CELLSPACING='0' CELLPADDING='5'>",
                                        "<TR><TD BORDER='1'><FONT COLOR='{{color}}' FACE='Helvetica Neue'><B>{{isa}} ({{id}})</B><BR/>{{class}}</FONT></TD></TR><TR><TD ALIGN='right'> ",
                                        "{% set attr = attr|default({}) %}{% for k, v in attr.items() %}{{v}} {% endfor %}",
                                        "{% set cv = cv|default({}) %}{% for k, v in cv.items() %}{{v}} {% endfor %}",
                                        "</TD></TR></TABLE>>")):- any_node(Object_id).
attr(node, Object_id,  (label,class), @stringify(Class,true)):- any_node(Object_id),ooasp_domain(Class,Object_id).
attr(node, Object_id,  (label,isa), @stringify(Class,true)):- any_node(Object_id),isa_smallest(Class,Object_id).
attr(node, Object_id,  (label,color), black):- node(Object_id,_), not domain_node(_,Object_id), user(ooasp_isa(_,Object_id)).
% Case for objects not instantiated
attr(node, Object_id,  (label,color), grey):- node(Object_id,_), domain_node(_,Object_id).
attr(node, Object_id,  (label,color), @color(green)):- node(Object_id,_), not user(ooasp_isa(_,Object_id)), ooasp_isa(_,Object_id).
attr(node, Object_id,  (label,id), Object_id):- any_node(Object_id).
attr(node, Object_id, penwidth, 0):- any_node(Object_id).

% Domain nodes
attr(node, Object_id, (label,bgcolor), "#C4C4C420"):- domain_node(_,Object_id).
attr(node, Object_id, color, "#C4C4C4"):- domain_node(_,Object_id).

% Is a nodes
attr(node, Object_id, (label,bgcolor), @color(blue,20)):- isa_node(_,Object_id).
% attr(node, Object_id, color, "black"):- isa_node(_,Object_id).

% Leaf nodes
attr(node, T, (label,bgcolor), @color(blue,40)):- leaf_node(_,T).

% Node border
attr(node, T, color, "black"):- node(T,_), not domain_node(_,T).
attr(node, T, margin, 0):- node(T,_).
attr(node, T, width, 0):- node(T,_).
attr(node, T, hight, 0):- node(T,_).

% User selections in green

% Add arguments to nodes
attr(node, Object_id, (label,attr,Attr_name), @argument_str(Attr_name,Value,"black")):-
    ooasp_attr_value(Attr_name,Object_id,Value),
    user(ooasp_attr_value(Attr_name,Object_id,Value)).
attr(node, Object_id, (label,attr,Attr_name), @argument_str(Attr_name,Value,@color(green))):-
    ooasp_attr_value(Attr_name,Object_id,Value),
    not user(ooasp_attr_value(Attr_name,Object_id,Value)).

% Add cvs to nodes
attr(node, Object_id, (label,cv,(Name,Object_id,Args)), @cv_str(Name,Mes,Args)):-
    ooasp_cv(Name,Object_id,Mes,Args).


% Associations
edge((Object_id1,Object_id2)) :-ooasp_associated(Name,Object_id1,Object_id2).

attr(edge,(Object_id1,Object_id2), xlabel, "<{{name}} <br/><FONT POINT-SIZE='10' FACE='Helvetica Neue'> {{super}}</FONT>>"):-ooasp_associated(Name,Object_id1,Object_id2).
attr(edge,(Object_id1,Object_id2), (xlabel,name), Name):-ooasp_associated(Name,Object_id1,Object_id2), not ooasp_assoc_specialization(_,Name).
attr(edge,(Object_id1,Object_id2), (xlabel,super), Super):-ooasp_associated(Name,Object_id1,Object_id2),ooasp_assoc_specialization(Name,Super).

attr(edge, (Object_id1,Object_id2), color, @color(green)) :- ooasp_associated(Name,Object_id1,Object_id2), not user(ooasp_associated(Name,Object_id1,Object_id2)),not ooasp_assoc_specialization(_,Name).
attr(edge, (Object_id1,Object_id2), fontcolor, @color(green)) :- ooasp_associated(Name,Object_id1,Object_id2), not user(ooasp_associated(Name,Object_id1,Object_id2)),not ooasp_assoc_specialization(_,Name).



#script (python)
from clingo.symbol import String
import textwrap

def argument_str(name,type,color):
    s = f"<FONT FACE='Helvetica Neue' COLOR='{color.string}'>" + str(name) + " = " + "<I> "+ str(type)  + "</I></FONT><br ALIGN='left'/> "
    return String(s)

def cv_str(name,message,args):
    args_symbols = [str(a) for a in args.arguments]
    formatted_message = f"{message.string.format(*args_symbols)}"
    s_wrap_list = textwrap.wrap(formatted_message, 40)
    message_wrapped = "<br ALIGN='left'/>   ".join(s_wrap_list)
    s = f"<FONT FACE='Helvetica Neue' COLOR='red' POINT-SIZE='12'><I> "+ message_wrapped  + "</I> (" + str(name) + ") </FONT><br ALIGN='left'/> "
    return String(s)

#end.
