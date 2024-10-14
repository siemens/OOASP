% Copyright (c) 2024 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

isa_smallest(SUPER,ID) :-
    _all(ooasp_isa(SUPER,ID)),
	not _all(ooasp_isa(SUB, ID)): ooasp_subclass(SUB,SUPER).

isa_smallest(SUPER,ID) :-
    _clinguin_browsing,
    ooasp_isa(SUPER,ID),
	not ooasp_isa(SUB, ID): ooasp_subclass(SUB,SUPER).

unused_node(Class,ID) :- ooasp_domain(Class,ID), _clinguin_browsing, not ooasp_isa(_,ID).


#defined ooasp_isa/3.
graph(config).
#const color_green = "#0DB144".
#const my_gray = "#00000020".

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

% ------- All nodes
attr(node, ID, label, @concat("<<TABLE BGCOLOR='{{bgcolor}}' BORDER='0' CELLBORDER='1' CELLSPACING='0' CELLPADDING='5'>",
                                        "<TR><TD BORDER='1'><FONT COLOR='{{color}}' FACE='Helvetica Neue'><B>{{isa}} ({{id}})</B><BR/>{{class}}</FONT></TD></TR><TR><TD ALIGN='right'> ",
                                        "{% set attr = attr|default({}) %}{% for k, v in attr.items() %}{{v}} {% endfor %}",
                                        "{% set cv = cv|default({}) %}{% for k, v in cv.items() %}{{v}} {% endfor %}",
                                        "</TD></TR></TABLE>>")):- any_node(ID).

% ------- Style All nodes
attr(node, ID, color, "black"):- node(ID,_), not unused_node(_,ID).
attr(node, ID, margin, 0):- node(ID,_).
attr(node, ID, width, 0):- node(ID,_).
attr(node, ID, hight, 0):- node(ID,_).
attr(node, ID,  (label,id), ID):- any_node(ID).
attr(node, ID, penwidth, 0):- any_node(ID).

% ------- Class name
attr(node, ID,  (label,class), @stringify(Class,true)):- ooasp_domain(Class,ID).
attr(node, ID,  (label,isa), @stringify(Class,true)):- label_isa(Class,ID).
attr(node, ID,  (label,color), black):- assumed_isa(Class,ID).
attr(node, ID,  (label,color), my_gray):- suggested_isa(Class,ID).
attr(node, ID,  (label,color), @color(green)):- browse_isa(Class,ID).

% ------- Background color
attr(node, ID, (label,bgcolor), "#C4C4C420"):- unused_node(_,ID).
attr(node, ID, color, "#C4C4C4"):- unused_node(_,ID).
attr(node, ID, (label,bgcolor), @color(blue,20)):- node(ID,_), not unused_node(_,ID).

% ------- Attributes
% browsing
attr(node, ID, (label,attr,Attr_name), @argument_str(Attr_name,Value,@color(green))):-
    ooasp_attr_value(Attr_name,ID,Value),
    _clinguin_browsing,
    not _clinguin_assume(ooasp_attr_value(Attr_name,ID,Value),true).

% inferred input
attr(node, ID, (label,attr,Attr_name), @argument_str(Attr_name,Value,my_gray)):-
    not _clinguin_browsing,
    not _clinguin_assume(ooasp_attr_value(Attr_name,ID,Value),true),
    _all(ooasp_attr_value(Attr_name,ID,Value)).
% user input
attr(node, ID, (label,attr,Attr_name), @argument_str(Attr_name,Value,"black")):-
    ooasp_attr_value(Attr_name,ID,Value),
    _clinguin_assume(ooasp_attr_value(Attr_name,ID,Value),true).

% Add cvs to nodes
% This is now in the UI
% attr(node, ID, (label,cv,(MAX,C2,ASSOC)), @cv_str("Needs at least {} more {}s",(MAX,C2,ASSOC))):-
%     not _clinguin_browsing,
%     ooasp_smallest_assoc(ASSOC, _, SIDE),
%     _all(object_needed(ID, ASSOC, _, C2, SIDE, _)),
%     #max{N:_all(object_needed(ID, ASSOC, N, C2, _, _))}=MAX.

attr(node, ID, (label,cv,(ASSOC,CMIN,N,C,SIDE)), @cv_str(M,(ASSOC,CMIN,N,C,SIDE),@color(red))):-
    not _clinguin_browsing,
    _clinguin_assume(ooasp_isa(Class, ID), true), Class!=object,
    _any(ooasp_cv(lowerbound,ID,M,(ASSOC,CMIN,N,C,SIDE,_))),
    #min{N':_any(ooasp_cv(lowerbound,ID,M,(ASSOC,CMIN,N',C,SIDE,_)))}=N.

% Associations

edge((ID1,ID2),config) :-shown_association(_,Name,ID1,ID2).

attr(edge,(ID1,ID2), xlabel, "<{{name}} <br/><FONT POINT-SIZE='10' FACE='Helvetica Neue'> {{super}}</FONT>>"):-shown_association(_,Name,ID1,ID2).
% attr(edge,(ID1,ID2), (xlabel,name), Name):-shown_association(_,Name,ID1,ID2), not ooasp_assoc_specialization(_,Name).
attr(edge,(ID1,ID2), (xlabel,super), Name):-shown_association(_,Name,ID1,ID2).

attr(edge, (ID1,ID2), color, @color(green)) :- shown_association(browse,Name,ID1,ID2).
attr(edge, (ID1,ID2), fontcolor, @color(green)) :- shown_association(browse,Name,ID1,ID2).

attr(edge, (ID1,ID2), color, my_gray) :- shown_association(infer,Name,ID1,ID2).
attr(edge, (ID1,ID2), fontcolor, my_gray) :- shown_association(infer,Name,ID1,ID2).

attr(edge, (ID1,ID2), color, black) :- shown_association(assumed,Name,ID1,ID2).
attr(edge, (ID1,ID2), fontcolor, black) :- shown_association(assumed,Name,ID1,ID2).

#script (python)
from clingo.symbol import String
import textwrap

def argument_str(name,type,color):
    s = f"<FONT FACE='Helvetica Neue' COLOR='{color.string}'>" + str(name) + " = " + "<I> "+ str(type)  + "</I></FONT><br ALIGN='left'/> "
    return String(s)

def cv_str(message,args,color='red'):
    args_symbols = [str(a) for a in args.arguments]
    formatted_message = f"{message.string.format(*args_symbols)}"
    s_wrap_list = textwrap.wrap(formatted_message, 40)
    message_wrapped = "<br ALIGN='left'/>   ".join(s_wrap_list)
    color = (str(color)).strip('"')
    s = f"<FONT FACE='Helvetica Neue' COLOR='{color}' POINT-SIZE='12'><I> "+ message_wrapped  + "</I> </FONT><br ALIGN='left'/> "
    return String(s)

#end.
