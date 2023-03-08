% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

graph(kb).

attr(graph_nodes, kb, shape, rectangle).
attr(graph, kb, splines, ortho).
attr(graph, kb, nodesep, "1").
attr(graph, kb, rankdir, "TB").
attr(graph, kb, fontsize, 20).
attr(graph, kb, (label,0), "Knowledge Base "):-ooasp_class(object).


% Classes as Nodes
node(Name) :- ooasp_class(Name).

attr(node, Class_name, label, @concat("<<TABLE BORDER='0' CELLBORDER='1' CELLSPACING='0' CELLPADDING='1'>",
                                        "<TR><TD><B>{{class}}</B></TD></TR><TR><TD ALIGN='right'> ",
                                        "{% set attr = attr|default({}) %}{% for k, v in attr.items() %}{{v}} {% endfor %}",
                                        "</TD></TR></TABLE>>")):- ooasp_class(Class_name).
attr(node,Class_name,(label,attr,Name),@argument_str(Name,Type)):-ooasp_attribute(Class_name,Name,Type).
attr(node,Class_name,(label,class),Class_name):-ooasp_class(Class_name).
attr(node, T, style, "filled"):- node(T).
attr(node, T, fillcolor, "#FFFFCE"):- node(T).
attr(node, T, color, "black"):- node(T).
attr(node, T, margin, 0):- node(T).
attr(node, T, width, 0):- node(T).
attr(node, T, hight, 0):- node(T).


% Associations
edge((Class1,Class2)):-ooasp_assoc(Name,Class1,Min1,Max1,Class2,Min2,Max2).

attr(edge,(Class1,Class2), dir, back):-ooasp_assoc(Name,Class1,Min1,Max1,Class2,Min2,Max2).
attr(edge,(Class1,Class2), arrowtail, odiamond):-ooasp_assoc(Name,Class1,Min1,Max1,Class2,Min2,Max2).
attr(edge,(Class1,Class2), arrowhead, odiamond):-ooasp_assoc(Name,Class1,Min1,Max1,Class2,Min2,Max2).
attr(edge,(Class1,Class2), xlabel, Name):-ooasp_assoc(Name,Class1,Min1,Max1,Class2,Min2,Max2).

cardinality((Class1,Class2),taillabel,Min1,Max1):-ooasp_assoc(Name,Class1,Min1,Max1,Class2,Min2,Max2).
cardinality((Class1,Class2),headlabel,Min2,Max2):-ooasp_assoc(Name,Class1,Min1,Max1,Class2,Min2,Max2).
% attr(edge,ID, (Propery,0), "<<TABLE BGCOLOR='grey' BORDER='0'><TR><TD><FONT POINT-SIZE='8'>"):-
    % cardinality(ID,Propery,Min,Max).
attr(edge,ID, (Propery,1), Min):- cardinality(ID,Propery,Min,Max).
attr(edge,ID, (Propery,2), "..."):- cardinality(ID,Propery,Min,Max).
attr(edge,ID, (Propery,3), Max):- cardinality(ID,Propery,Min,Max).
% attr(edge,ID, (Propery,4), "</FONT></TD></TR></TABLE>>"):- cardinality(ID,Propery,Min,Max).



% Subclass
edge((Sup,Sub)):-ooasp_subclass(Sub,Sup).

attr(edge,(Sup,Sub),color,"#888889"):-ooasp_subclass(Sub,Sup).
attr(edge,(Sup,Sub),dir,back):-ooasp_subclass(Sub,Sup).
attr(edge,(Sup,Sub),arrowtail,open):-ooasp_subclass(Sub,Sup).
attr(edge,(Sup,Sub),arrowsize,"0.5"):-ooasp_subclass(Sub,Sup).

#script (python)
from clingo.symbol import String

def argument_str(name,type):
    s = str(name) + " : " + "<I> "+ str(type)  + "</I><br ALIGN='left' />"
    return String(s)

def record_label(name):
    str_name = str(name)[0].upper() + str(name)[1:]
    title = str_name.replace("_"," ")
    s = "<<TABLE BORDER='0' CELLBORDER='1' CELLSPACING='0' CELLPADDING='1'><TR><TD ><B>"+title+"</B></TD></TR><TR><TD ALIGN='right'>"
    return String(s)

def record_end():
    return String("</TD></TR></TABLE>>")
#end.