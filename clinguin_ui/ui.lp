elem(w,window,root).

elem(menu_bar,menu_bar,w).
attr(menu_bar,title,"OOASP").
attr(menu_bar,icon,"fa-puzzle-piece").

    elem(menu_bar_load, button, menu_bar).
    attr(menu_bar_load,label, "Load Partial Configuration").
    attr(menu_bar_load, icon, "fa-upload").
    attr(menu_bar_load, class, ("btn-outline-primary";"border-0")).

    elem(menu_bar_save, button, menu_bar).
    attr(menu_bar_save,label, "Save Configuration").
    attr(menu_bar_save, icon, "fa-download").
    attr(menu_bar_save, class, ("btn-outline-primary";"border-0")).

    elem(end_btn,button,menu_bar).
    attr(end_btn,label,"End browsing").
    attr(end_btn,icon,"fa-xmark").
    attr(end_btn,class,("btn-warning")).

    elem(find_btn,button,menu_bar).
    attr(find_btn,label,"Find Incrementally").
    attr(find_btn,icon,"fa-gears").
    attr(find_btn,class,("btn-success")).

    elem(next_btn,button,menu_bar).
    attr(next_btn,label,"Next solution").
    attr(next_btn,icon,"fa-forward").
    attr(next_btn,class,("btn-outline-secondary")).

    elem(select_btn,button,menu_bar).
    attr(select_btn,label,"Select configuration"). 
    attr(select_btn,class,("btn-secondary")).

    elem(check_btn,button,menu_bar).
    attr(check_btn,label,"Check").
    attr(check_btn,icon,"fa-magnifying-glass").
    attr(check_btn,class,("btn-outline-success")).

% Canvas
elem(config_viz, canvas,w).
attr(config_viz,class,("vw-75";"vh-75")).
attr(config_viz, image_type, clingraph__config).    #include "ooasp/encodings/viz_config_nodes.lp".

        elem(n(X), svg_node, config_viz) :- node(X).
        attr(n(X), clingraph_id, X) :- node(X).
        when(n(X), click, call, restart):- node(X).

attr(config_viz,order,2).

% Config Container
elem(config_container, container,w).
attr(config_container,flex_direction,row).
attr(config_container,class,("justify-content-evenly";"p-3";"border")).
attr(config_container,order,3).

% Extend container
    elem(extend_container,container,config_container).
    attr(extend_container,flex_direction,column).
    attr(extend_container,class,("col-sm";"flex-column")).

        elem(extend_buttons,container,extend_container).
        attr(extend_buttons,flex_direction,column).
        attr(extend_buttons,class,("col-sm";"flex-column")).
        attr(extend_buttons,order,1).

            elem(extend_domain_button,button,extend_buttons).
            attr(extend_domain_button,label,"Extend Domain").
            attr(extend_domain_button,icon,"fa-plus").
            attr(extend_domain_button,class,("btn-secondary")).
            attr(extend_domain_button,order,1).

            elem(create_required_btn,button,extend_buttons).
            attr(create_required_btn,label,"Create Required").
            attr(create_required_btn,icon,"fa-object-group").
            attr(create_required_btn,class,("btn-outline-secondary")).
            attr(create_required_btn,order,2).
            

        elem(addobject_dd_container,container,extend_container).
        attr(addobject_dd_container,class,("d-flex";"flex-row")).
        attr(addobject_dd_container,order,2).

            elem(addobject_dd_label,label, addobject_dd_container).
            attr(addobject_dd_label,label,"Add a new object").
            attr(addobject_dd_label,class,("p-2")).
            attr(addobject_dd_label,order,1).

            elem(addobject_dd,dropdown_menu,addobject_dd_container).
            attr(addobject_dd,selected,"select class").
            attr(addobject_dd,class,("p-2";"border";"border-1")).
            attr(addobject_dd,order,2).
                
                elem(dd_element(C),dropdown_menu_item,addobject_dd):-ooasp_leafclass(C).
                attr(dd_element(C),label,C):-ooasp_leafclass(C).
                when(dd_element(C),click,context,(class_name,C)):-ooasp_leafclass(C).
                when(dd_element(C),click,update,(addobject_dd,selected,C)):-ooasp_leafclass(C).
            
            elem(addobject_btn,button,addobject_dd_container).
            attr(addobject_btn,icon,"fa-plus").
            attr(addobject_btn,class,("btn-outline-dark")).
            attr(addobject_btn,order,3).
            when(addobject_btn,click,call,add_object(_context_value(class_name))).

                % I Assume backen will have a way to automate this

        elem(addobject_p_dd_container,container,extend_container).
        attr(addobject_p_dd_container,class,("d-flex";"flex-row")).
        attr(addobject_p_dd_container,order,3).

            elem(addobject_p_dd_label,label, addobject_p_dd_container).
            attr(addobject_p_dd_label,label,"Add a new object (propagate)").
            attr(addobject_p_dd_label,class,("p-2")).
            attr(addobject_p_dd_label,order,1).

            elem(addobject_p_dd,dropdown_menu,addobject_p_dd_container).
            attr(addobject_p_dd,selected,"element").
            attr(addobject_p_dd,class,("p-2";"border";"border-1")).
            attr(addobject_p_dd,order,2).
                elem(dd_element,dropdown_menu_item,addobject_p_dd).
                attr(dd_element,label,"element").

                elem(dd_rack,dropdown_menu_item,addobject_p_dd).
                attr(dd_rack,label,"rack").

                elem(dd_frame,dropdown_menu_item,addobject_p_dd).
                attr(dd_frame,label,"frame").
            
            elem(addobject_p_btn,button,addobject_p_dd_container).
            attr(addobject_p_btn,icon,"fa-plus").
            attr(addobject_p_btn,class,("btn-outline-dark")).
            attr(addobject_p_btn,order,3).

% Info container
    elem(info_container,container,config_container).
    attr(info_container,flex_direction,column).
    attr(info_container,class,("col-sm";"flex-column")).
        
        elem(domain_size_txt,label,info_container).
        attr(domain_size_txt,label,"Domain Size:"). %I assume the concat will have to be used here, something like attr(domain_size_txt,label,@concat("Domain Size: ",DS)):-domain_size(DS).
        attr(domain_size_txt,class,("text-start";"fw-semibold";"fs-5")).
        attr(domain_size_txt,order,1).

        elem(config_size_txt,label,info_container).
        attr(config_size_txt,label,"Configuration Size:").
        attr(config_size_txt,class,("text-start";"fw-semibold";"fs-5";"p-1")).
        attr(config_size_txt,order,2).

        elem(extra_opts,container,info_container).
        attr(extra_opts,flex_direction,column).
        attr(extra_opts,class,("d-flex";"flex-row";"justify-content-evenly";"p-2")).
        attr(extra_opts,background_color,"#ededed").
        attr(extra_opts,order,3).

            elem(inferences_btn,button,extra_opts).
            attr(inferences_btn,label,"Add inferences").
            attr(inferences_btn,icon,"fa-plus").
            attr(inferences_btn,class,("btn-outline-secondary")).
            attr(inferences_btn,order,1).

            elem(clear_checks_btn,button,extra_opts).
            attr(clear_checks_btn,label,"Clear checks").
            attr(clear_checks_btn,icon,"fa-eraser").
            attr(clear_checks_btn,class,("btn-outline-danger")).
            attr(clear_checks_btn,order,2).

            elem(clear_config_btn,button,extra_opts).
            attr(clear_config_btn,label,"Clear configuration").
            attr(clear_config_btn,icon,"fa-trash").
            attr(clear_config_btn,class,("btn-danger")).
            attr(clear_config_btn,order,3).

            elem(btn1,button,extra_opts).
            attr(btn1,label,"placeholder").
            attr(btn1,order,4).



% dev borers
%attr(E,class,("border-1";"border";"border-dark")):- elem(E, container, _).