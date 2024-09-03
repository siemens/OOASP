elem(w,window,root).


% Menu bar placeholder

elem(menu_bar, menu_bar, w).
attr(menu_bar, title, "OOASP UI").
attr(menu_bar,order,1).

    elem(menu_bar_clear, button, menu_bar).
    attr(menu_bar_clear, label, "Clear Configuration").
    attr(menu_bar_clear, icon, "fa-trash").
    attr(menu_bar_clear, class, ("btn-outline-danger";"border-0")).

    elem(menu_bar_load, button, menu_bar).
    attr(menu_bar_load,label, "Load Partial Configuration").
    attr(menu_bar_load, icon, "fa-upload").
    attr(menu_bar_load, class, ("btn-outline-primary";"border-0")).

    elem(menu_bar_save, button, menu_bar).
    attr(menu_bar_save,label, "Save Configuration").
    attr(menu_bar_save, icon, "fa-download").
    attr(menu_bar_save, class, ("btn-outline-primary";"border-0")).

% Canvas Container
elem(config_viz, canvas,w).
attr(config_viz,class,("vw-75";"vh-75")).
attr(config_viz,image,"examples/racks/racks_v1.png").
attr(config_viz,order,2).

% Config container

elem(config_container, container,w).
attr(config_container,flex_direction,row).
attr(config_container,class,("justify-content-evenly")).
attr(config_container,order,3).

    % Extend container

    elem(extend_container,container,config_container).
    attr(extend_container,flex_direction,column).
    attr(extend_container,class,("col-sm";"flex-column")).

        elem(extend_con_label,label,extend_container).
        attr(extend_con_label,label,"Extend").
        attr(extend_con_label,class,("fw-bold")).
        attr(extend_con_label,order,1).

        elem(domain_size_txt,label,extend_container).
        attr(domain_size_txt,label,"Domain Size:"). %I assume the concat will have to be used here, something like attr(domain_size_txt,label,@concat("Domain Size: ",DS)):-domain_size(DS).
        attr(domain_size_txt,order,2).

        elem(extend_domain_button,button,extend_container).
        attr(extend_domain_button,label,"Extend Domain").
        attr(extend_domain_button,icon,"fa-plus").
        attr(extend_domain_button,order,3).

        elem(config_size_txt,label,extend_container).
        attr(config_size_txt,label,"Configuration Size:").
        attr(config_size_txt,order,4).

        elem(addobject_dd_container,container,extend_container).
        attr(addobject_dd_container,class,("d-flex";"flex-row")).
        attr(addobject_dd_container,order,5).

            elem(addobject_dd_label,label, addobject_dd_container).
            attr(addobject_dd_label,label,"Add a new object").
            attr(addobject_dd_label,class,("p-2")).
            attr(addobject_dd_label,order,1).

            elem(addobject_dd,dropdown_menu,addobject_dd_container).
            attr(addobject_dd,selected,"element").
            attr(addobject_dd,class,("p-2";"border";"border-1")).
            attr(addobject_dd,order,2).
                elem(dd_element,dropdown_menu_item,addobject_dd).
                attr(dd_element,label,"element").

                elem(dd_rack,dropdown_menu_item,addobject_dd).
                attr(dd_rack,label,"rack").

                elem(dd_frame,dropdown_menu_item,addobject_dd).
                attr(dd_frame,label,"frame").

                % I Assume backen will have a way to automate this

        elem(addobject_p_dd_container,container,extend_container).
        attr(addobject_p_dd_container,class,("d-flex";"flex-row")).
        attr(addobject_p_dd_container,order,6).

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

    % Edit container

    elem(edit_container,container,config_container).
    attr(edit_container,flex_direction,column).
    attr(edit_container,class,("col-sm";"flex-column")).

        elem(edit_con_label,label,edit_container).
        attr(edit_con_label,label,"Edit").
        attr(edit_con_label,class,("fw-bold")).
        attr(edit_con_label,order,1).


        elem(edit_dd_container,container,edit_container).
        attr(edit_dd_container,class,("d-flex";"flex-row")).
        attr(edit_dd_container,order,2).

            elem(edit_dd_label,label, edit_dd_container).
            attr(edit_dd_label,label,"Object to edit").
            attr(edit_dd_label,class,("p-2")).
            attr(edit_dd_label,order,1).

            elem(edit_dd,dropdown_menu,edit_dd_container).
            attr(edit_dd,selected,"Placeholder Element").
            attr(edit_dd,class,("p-2";"border";"border-1")).
            attr(edit_dd,order,2).
                elem(dd_ph1,dropdown_menu_item,edit_dd).
                attr(dd_ph1,label,"PH 1").

                elem(dd_ph2,dropdown_menu_item,edit_dd).
                attr(dd_ph2,label,"PH 2").


    % Browse container

    elem(browse_container,container, config_container).
    attr(browse_container,flex_direction,column).
    attr(browse_container_container,class,("col-sm";"flex-column")).
        elem(browse_con_label,label, browse_container).
        attr(browse_con_label,label,"Browse").
        attr(browse_con_label,class,("fw-bold")).
        attr(browse_con_label,order,1).

        elem(selection_container,container,browse_container).
        attr(selection_container,class,("d-flex";"flex-row")).
        attr(selection_container,order,2).

            elem(prev_btn,button,selection_container).
            attr(prev_btn,icon,"fa-forward").
            attr(prev_btn,label,"Previous").
            
            elem(select_btn,button,selection_container).
            attr(select_btn,label,"Select").

            elem(next_btn,button,selection_container).
            attr(next_btn,icon,"fa-backward").
            attr(next_btn,label,"Next").

        elem(find_inc_btn,button,browse_container).
        attr(find_inc_btn,label,"Find Incrementally").
        attr(find_inc_btn,icon,"fa-gears").
        attr(find_inc_btn,order,3).

        elem(find_ovs_btn,button,browse_container).
        attr(find_ovs_btn,label,"Find Incrementally (overshoot)").
        attr(find_ovs_btn,order,4).

        elem(end_browsing_btn,button,browse_container).
        attr(end_browsing_btn,label,"End Browsing").
        attr(end_browsing_btn,order,5).

    % Check
    elem(check_container,container, config_container).
    attr(check_container,flex_direction,column).
    attr(check_container_container,class,("d-grid";"gap-2")).
        elem(check_con_label,label, check_container).
        attr(check_con_label,label,"Check").
        attr(check_con_label,class,("fw-bold")).
        attr(check_con_label,order,1).

        elem(check_btn,button,check_container).
        attr(check_btn,label,"Check").
        attr(check_btn,order,2).

        elem(clear_checks_btn,button,check_container).
        attr(clear_checks_btn,label,"Clear Checks").
        attr(clear_checks_btn,order,3).

        elem(add_inferences_btn,button,check_container).
        attr(add_inferences_btn,label,"Add Inferences").
        attr(add_inferences_btn,order,4).

        elem(create_required_btn,button,check_container).
        attr(create_required_btn,label,"Create Required").
        attr(create_required_btn,order,5).
        

% dev borers
% attr(E,class,("border-1";"border";"border-dark")):- elem(E, container, _).
