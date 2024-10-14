% Copyright (c) 2024 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

    elem(config_viz, canvas,window_flex).
    attr(config_viz, image_type, clingraph__config).
            #include "ooasp/encodings/viz_config_nodes.lp".

            elem(n(X), svg_node, config_viz) :- node(X,config).
            attr(n(X), clingraph_id, X) :- node(X,config).
            when(n(X),click,update,(selected_object,label,@format("{} ({})",@stringify(Class,true),X))) :- node(X,config),label_isa(Class,X).
            when(n(X),click,update,(selected_object,label,@format("({})",X))) :- node(X,config),not label_isa(_,X).
            when(n(X),click,update,(selected_object_info,label,@stringify(C,true))) :- node(X,config),ooasp_domain(C, X).

            when(n(X),click,update,(assoc_edit_options(X),visibility,shown)) :- node(X,config).
            when(n(X),click,update,(assoc_edit_options(X'),visibility,hidden)) :- node(X,config), node(X',config), X'!=X.
            when(n(X),click,update,(value_edit_options(X),visibility,shown)) :- node(X,config).
            when(n(X),click,update,(value_edit_options(X'),visibility,hidden)) :- node(X,config), node(X',config), X'!=X.
            when(n(X),click,update,(deselect_btn_c(X),visibility,shown)) :- node(X,config).
            when(n(X),click,update,(deselect_btn_c(X'),visibility,hidden)) :- node(X,config), node(X',config), X'!=X.
            when(n(X),click,update,(n(Y),filter,"grayscale(1)")) :- node(X,config), shown_association(_,_,X,Y).
            when(n(X),click,update,(n(Y),filter,"grayscale(1)")) :- node(X,config), shown_association(_,_,Y,X).
            when(n(X),click,update,(n(X),filter,"hue-rotate(180deg)")) :- node(X,config).
            when(n(X),click,update,(n(X'),filter,"unset")) :- node(X,config), node(X',config), X'!=X, not shown_association(_,_,X,X'), not shown_association(_,_,X',X).
            when(n(X),click,update,(selected_object_cd,visibility,shown)) :- node(X,config).

    attr(config_viz,order,1).