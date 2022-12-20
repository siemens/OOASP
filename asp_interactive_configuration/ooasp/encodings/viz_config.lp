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
domain_node(Class,Object_id) :- ooasp_domain(_,Class,Object_id), not ooasp_isa_leaf(_,_,Object_id).
node(Object_id) :- domain_node(_,Object_id).
attr(node, Object_id,  (label,-1), @record_label(Class_name,Object_id)):- domain_node(Class_name,Object_id).
attr(node, Object_id, (label,1), @record_end()):- domain_node(Class_name,Object_id).
attr(node, Object_id, style, "filled"):- domain_node(_,Object_id).
attr(node, Object_id, fillcolor, "#E7D5EA"):- domain_node(_,Object_id).
attr(node, Object_id, color, "black"):- domain_node(_,Object_id).

% Objects instanciated 
leaf_node(Class,Object_id) :- ooasp_isa_leaf(_,Class,Object_id), ooasp_leafclass(_,Class).
node(Object_id) :- leaf_node(Class,Object_id).
attr(node, Object_id, (label,-1), @record_label(Class_name,Object_id)):- leaf_node(Class_name,Object_id).
attr(node, Object_id, (label,1), @record_end()):- leaf_node(Class_name,Object_id).
attr(node, T, style, "filled"):- leaf_node(_,T).
attr(node, T, fillcolor, "#D2D2E0"):- leaf_node(_,T).

% Node border
attr(node, T, color, "black"):- node(T).
attr(node, T, margin, 0):- node(T).
attr(node, T, width, 0):- node(T).
attr(node, T, hight, 0):- node(T).

% User selections in green
attr(node, Object_id, fontcolor, "#0DB144"):- user(ooasp_isa_leaf(_,Class,Object_id)).

% Add arguments to nodes
attr(node, Object_id, label, @argument_str(Attr_name,Value,"black")):- 
    ooasp_attribute_value(_,Attr_name,Object_id,Value),
    not user(ooasp_attribute_value(_,Attr_name,Object_id,Value)).
attr(node, Object_id, label, @argument_str(Attr_name,Value,"#0DB144")):- 
    ooasp_attribute_value(_,Attr_name,Object_id,Value),
    user(ooasp_attribute_value(_,Attr_name,Object_id,Value)).


% Associations
edge((Object_id1,Object_id2)) :-ooasp_associated(_,Name,Object_id1,Object_id2).

attr(edge, (Object_id1,Object_id2), xlabel, Name) :- ooasp_associated(_,Name,Object_id1,Object_id2).
attr(edge, (Object_id1,Object_id2), color, "#0DB144") :- user(ooasp_associated(_,Name,Object_id1,Object_id2)).
attr(edge, (Object_id1,Object_id2), fontcolor, "#0DB144") :- user(ooasp_associated(_,Name,Object_id1,Object_id2)).



#script (python)
from clingo.symbol import String

def argument_str(name,type,color):
    s = f"<FONT COLOR='{color.string}'>" + str(name) + " = " + "<I> "+ str(type)  + "</I></FONT><br ALIGN='left'/> "
    return String(s)

def node_title(name,object_id):
    str_name = str(name)[0].upper() + str(name)[1:]
    title = str_name.replace("_"," ")
    s = f"{title} ({str(object_id)})"
    return String(s)

def record_label(name,object_id):
    title = node_title(name,object_id).string
    s = f"<<TABLE BORDER='0' CELLBORDER='1' CELLSPACING='0' CELLPADDING='1'><TR><TD ><B>{title}</B></TD></TR><TR><TD ALIGN='right'>"
    return String(s)

def record_end():
    return String("</TD></TR></TABLE>>")
#end.

