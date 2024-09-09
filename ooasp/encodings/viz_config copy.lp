% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

isa_smallest(SUPER,ID) :-
    _all(ooasp_isa(SUPER,ID)),
	not _all(ooasp_isa(SUB, ID)): ooasp_subclass(SUB,SUPER).

isa_smallest(SUPER,ID) :-
    _clinguin_browsing,
    ooasp_isa(SUPER,ID),
	not ooasp_isa(SUB, ID): ooasp_subclass(SUB,SUPER).

unused_node(Class,ID) :- ooasp_domain(Class,ID), not _all(ooasp_isa(_,ID)).
unused_node(Class,ID) :- ooasp_domain(Class,ID), _clinguin_browsing, not ooasp_isa(_,ID).

assumed_isa(Class,ID) :- ooasp_domain(Class,ID), _all(ooasp_isa_leaf(C,ID)), _clinguin_assume(ooasp_isa(C,ID), true).
suggested_isa(Class,ID) :- ooasp_domain(Class,ID), _all(ooasp_isa_leaf(C,ID)), not _clinguin_assume(ooasp_isa(C,ID), true), not _clinguin_browsing.
browse_isa(Class,ID) :- ooasp_domain(Class,ID), ooasp_isa_leaf(C,ID), not _clinguin_assume(ooasp_isa(C,ID), true), _clinguin_browsing.


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
attr(node, ID, label, @concat("<<TABLE BGCOLOR='{{bgcolor}}' BORDER='0' CELLBORDER='1' CELLSPACING='0' CELLPADDING='5'>",
                                        "<TR><TD BORDER='1'><FONT COLOR='{{color}}' FACE='Helvetica Neue'><B>{{isa}} ({{id}})</B><BR/>{{class}}</FONT></TD></TR><TR><TD ALIGN='right'> ",
                                        "{% set attr = attr|default({}) %}{% for k, v in attr.items() %}{{v}} {% endfor %}",
                                        "{% set cv = cv|default({}) %}{% for k, v in cv.items() %}{{v}} {% endfor %}",
                                        "</TD></TR></TABLE>>")):- any_node(ID).

% -------- Style All nodes
attr(node, ID, color, "black"):- node(ID,_), not unused_node(_,ID).
attr(node, ID, margin, 0):- node(ID,_).
attr(node, ID, width, 0):- node(ID,_).
attr(node, ID, hight, 0):- node(ID,_).
attr(node, ID,  (label,id), ID):- any_node(ID).
attr(node, ID, penwidth, 0):- any_node(ID).

% -------- Class name
attr(node, ID,  (label,class), @stringify(Class,true)):- ooasp_domain(Class,ID).
attr(node, ID,  (label,isa), @stringify(Class,true)):- isa_smallest(Class,ID).
% attr(node, ID,  (label,color), black):- assumed_isa(Class,ID).
% attr(node, ID,  (label,color), black):- suggested_isa(Class,ID).
% attr(node, ID,  (label,color), @color(green)):- browse_isa(Class,ID).

% -------- Background color
% attr(node, ID, (label,bgcolor), "#C4C4C420"):- unused_node(_,ID).
% attr(node, ID, color, "#C4C4C4"):- unused_node(_,ID).
% attr(node, ID, (label,bgcolor), @color(blue,20)):- node(ID,_), not unused_node(_,ID).
% attr(node, T, (label,bgcolor), @color(blue,40)):- leaf_node(_,T).

% -------- Attributes
% browsing
attr(node, ID, (label,attr,Attr_name), @argument_str(Attr_name,Value,@color(green))):-
    ooasp_attr_value(Attr_name,ID,Value),
    _clinguin_browsing.
% inferred input
% attr(node, ID, (label,attr,Attr_name), @argument_str(Attr_name,Value,black)):-
%     not _clinguin_browsing,
%     not _clinguin_assume(ooasp_attr_value(Attr_name,ID,Value),true),
%     _all(ooasp_attr_value(Attr_name,ID,Value)).
% user input
attr(node, ID, (label,attr,Attr_name), @argument_str(Attr_name,Value,black)):-
    ooasp_attr_value(Attr_name,ID,Value),
    _clinguin_assume(ooasp_attr_value(Attr_name,ID,Value),true).

% -------- Add cvs to nodes
% attr(node, ID, (label,cv,(Name,ID,Args)), @cv_str(Name,Mes,Args)):-
%     ooasp_cv(Name,ID,Mes,Args).


% Associations
edge((ID1,ID2),config) :-ooasp_associated(Name,ID1,ID2).

attr(edge,(ID1,ID2), xlabel, "<{{name}} <br/><FONT POINT-SIZE='10' FACE='Helvetica Neue'> {{super}}</FONT>>"):-ooasp_associated(Name,ID1,ID2).
attr(edge,(ID1,ID2), (xlabel,name), Name):-ooasp_associated(Name,ID1,ID2), not ooasp_assoc_specialization(_,Name).
attr(edge,(ID1,ID2), (xlabel,super), Super):-ooasp_associated(Name,ID1,ID2),ooasp_assoc_specialization(Name,Super).

attr(edge, (ID1,ID2), color, @color(green)) :- ooasp_associated(Name,ID1,ID2), not user(ooasp_associated(Name,ID1,ID2)),not ooasp_assoc_specialization(_,Name).
attr(edge, (ID1,ID2), fontcolor, @color(green)) :- ooasp_associated(Name,ID1,ID2), not user(ooasp_associated(Name,ID1,ID2)),not ooasp_assoc_specialization(_,Name).



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
