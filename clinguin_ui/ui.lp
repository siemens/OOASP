elem(w,window,root).
attr(w,flex_direction,row).


elem(menu_bar,menu_bar,w).
attr(menu_bar,title,"OOASP").
attr(menu_bar,icon,"fa-puzzle-piece").

    elem(menu_bar_load, button, menu_bar).
    attr(menu_bar_load,label, "Load").
    attr(menu_bar_load, icon, "fa-upload").
    attr(menu_bar_load, class, ("btn-outline-primary";"border-0")).

    elem(menu_bar_save, button, menu_bar).
    attr(menu_bar_save,label, "Save").
    attr(menu_bar_save, icon, "fa-download").
    attr(menu_bar_save, class, ("btn-outline-primary";"border-0")).

    elem(end_btn,button,menu_bar).
    attr(end_btn,label,"End browsing").
    attr(end_btn,icon,"fa-xmark").
    attr(end_btn,class,("btn-warning")).

    elem(find_btn,button,menu_bar).
    attr(find_btn,label,"Find Incrementally").
    attr(find_btn,icon,"fa-gears").
    attr(find_btn,class,("btn-outline-secondary")).

    elem(next_btn,button,menu_bar).
    attr(next_btn,label,"Enforce Complete Configuration") :- _clinguin_external(check_potential_cv,false).
    attr(next_btn,label,"Allow partial configuration.") :- _clinguin_external(check_potential_cv,true).
    %attr(next_btn,icon,"fa-forward").
    attr(next_btn,class,("btn-outline-success")):- _clinguin_external(check_potential_cv,false).
    when(next_btn,click,call,(set_external(check_potential_cv,true))):- _clinguin_external(check_potential_cv,false).
    when(next_btn,click,call,(set_external(check_potential_cv,false))):- _clinguin_external(check_potential_cv,true).

    elem(suggest_btn,button,menu_bar).
    attr(suggest_btn,label,"Next Solution").
    attr(suggest_btn,icon,"fa-forward").
    attr(suggest_btn,class,("btn-outline-success")).
    when(suggest_btn,click,call, next_solution).

    elem(select_btn,button,menu_bar) :- _clinguin_browsing.
    attr(select_btn,label,"Select solution") :- _clinguin_browsing.
    attr(select_btn,class,("btn-outline-success")) :- _clinguin_browsing.
    attr(select_btn, icon, "fa-hand-pointer") :- _clinguin_browsing.
    when(select_btn, click, call, select("#show ooasp_associated/3. #show ooasp_attr_value/3.")) :- _clinguin_browsing.


    elem(check_btn,button,menu_bar).
    attr(check_btn,label,"Check").
    attr(check_btn,icon,"fa-magnifying-glass").
    attr(check_btn,class,("btn-outline-danger")).


    elem(restart_btn,button,menu_bar).
    attr(restart_btn,label,"Restart").
    attr(restart_btn,icon,"fa-trash").
    attr(restart_btn,class,("btn-danger")).


% Canvas
elem(config_viz, canvas,w).
% attr(config_viz,class,("vw-75";"vh-75")).
attr(config_viz, image_type, clingraph__config).
        #include "ooasp/encodings/viz_config_nodes.lp".

        elem(n(X), svg_node, config_viz) :- node(X,config).
        attr(n(X), clingraph_id, X) :- node(X,config).
        when(n(ID), click, update, (edit_context(ID), visibility, shown)):- node(ID,config).

attr(config_viz,order,2).

% Config Container
elem(config_container, container,w).
attr(config_container,flex_direction,column).
attr(config_container,class,("p-3";"bg-info";"bg-opacity-10")).
attr(config_container,order,1).
attr(config_container,width,250).

% Extend container
    elem(extend_container,container,config_container).
    attr(extend_container,flex_direction,column).
    attr(extend_container,class,("col-sm";"flex-column")).
    attr(extend_container,order,2).

        % elem(extend_buttons,container,extend_container).
        % attr(extend_buttons,flex_direction,column).
        % attr(extend_buttons,class,("col-sm";"flex-column")).
        % attr(extend_buttons,order,1).

            % elem(extend_domain_button,button,extend_buttons).
            % attr(extend_domain_button,label,"Extend Domain").
            % attr(extend_domain_button,icon,"fa-plus").
            % attr(extend_domain_button,class,("btn-secondary")).
            % attr(extend_domain_button,order,1).

            % elem(create_required_btn,button,extend_buttons).
            % attr(create_required_btn,label,"Create Required").
            % attr(create_required_btn,icon,"fa-object-group").
            % attr(create_required_btn,class,("btn-outline-secondary")).
            % attr(create_required_btn,order,2).


        elem(addobject_dd_container,container,extend_container).
        attr(addobject_dd_container,class,("d-flex";"flex-col";"mt-5";"align-items-start")).
        % attr(addobject_dd_container,class,("d-flex";"flex-row";"bg-primary";"bg-opacity-75";"rounded";"p-2")).
        attr(addobject_dd_container,order,2).

            elem(addobject_dd_label,label, addobject_dd_container).
            attr(addobject_dd_label,label,"Add object").
            attr(addobject_dd_label,class,("fw-semibold";"fs-5")).
            attr(addobject_dd_label,order,1).

            elem(addobject_dd_c,container,addobject_dd_container).
            attr(addobject_dd_c,class,("d-flex";"flex-row";"mt-1")).
            attr(addobject_dd_c,order,2).


            elem(addobject_dd,dropdown_menu,addobject_dd_c).
            attr(addobject_dd,selected,"object").
            % attr(addobject_dd,class,("m-2";"p-2";"border";"border-1")).
            attr(addobject_dd,class,("m-2";"p-2";"border";"border-1";"bg-primary";"bg-opacity-10")).
            attr(addobject_dd,order,1).
            
            class_to_add(C) :- ooasp_leafclass(C).
            %class_to_add(object).

                elem(dd_element(C),dropdown_menu_item,addobject_dd):-class_to_add(C).
                attr(dd_element(C),label,C):-class_to_add(C).
                when(dd_element(C),click,context,(class_name,C)):-class_to_add(C).
                when(dd_element(C),click,update,(addobject_dd,selected,C)):-class_to_add(C).


            elem(addobject_dd_amount,dropdown_menu,addobject_dd_c).
            attr(addobject_dd_amount,selected,"1").
            % attr(addobject_dd_amount,class,("m-2";"p-2";"border";"border-1")).
            attr(addobject_dd_amount,class,("m-2";"p-2";"border";"border-1";"bg-primary";"bg-opacity-10")).
            attr(addobject_dd_amount,order,1).

                amount(1..10).
                elem(dd_element(C),dropdown_menu_item,addobject_dd_amount):-amount(C).
                attr(dd_element(C),label,C):-amount(C).
                attr(dd_element(C),order,10-C):-amount(C).
                when(dd_element(C),click,context,(amount,C)):-amount(C).
                when(dd_element(C),click,update,(addobject_dd_amount,selected,C)):-amount(C).

            elem(addobject_btn,button,addobject_dd_c).
            attr(addobject_btn,icon,"fa-plus").
            attr(addobject_btn,class,("btn-primary";"m-2";"border";"border-dark";"border-2")).
            attr(addobject_btn,order,3).
            when(addobject_btn,click,call,add_object(_context_value(class_name,const,object),_context_value(amount,str,1))).

                % I Assume backen will have a way to automate this

        % elem(addobject_p_dd_container,container,extend_container).
        % attr(addobject_p_dd_container,class,("d-flex";"flex-row")).
        % attr(addobject_p_dd_container,order,3).

            % elem(addobject_p_dd_label,label, addobject_p_dd_container).
            % attr(addobject_p_dd_label,label,"Add a new object (propagate)").
            % attr(addobject_p_dd_label,class,("p-2")).
            % attr(addobject_p_dd_label,order,1).

            % elem(addobject_p_dd,dropdown_menu,addobject_p_dd_container).
            % attr(addobject_p_dd,selected,"element").
            % attr(addobject_p_dd,class,("p-2";"border";"border-1")).
            % attr(addobject_p_dd,order,2).
            %     elem(dd_element,dropdown_menu_item,addobject_p_dd).
            %     attr(dd_element,label,"element").

            %     elem(dd_rack,dropdown_menu_item,addobject_p_dd).
            %     attr(dd_rack,label,"rack").

            %     elem(dd_frame,dropdown_menu_item,addobject_p_dd).
            %     attr(dd_frame,label,"frame").

            % elem(addobject_p_btn,button,addobject_p_dd_container).
            % attr(addobject_p_btn,icon,"fa-plus").
            % attr(addobject_p_btn,class,("btn-outline-dark")).
            % attr(addobject_p_btn,order,3).

% Info container
    elem(info_container,container,config_container).
    attr(info_container,flex_direction,column).
    attr(info_container,class,("col-sm";"flex-column")).
    attr(info_container,order,1).

        elem(domain_size_txt,label,info_container).
        attr(domain_size_txt,label,"Domain Size:"). %I assume the concat will have to be used here, something like attr(domain_size_txt,label,@concat("Domain Size: ",DS)):-domain_size(DS).
        attr(domain_size_txt,class,("text-start";"fw-semibold";"fs-6")).
        attr(domain_size_txt,order,1).

        elem(config_size_txt,label,info_container).
        attr(config_size_txt,label,"Configuration Size:").
        attr(config_size_txt,class,("text-start";"fw-semibold";"fs-6")).
        attr(config_size_txt,order,2).

        % elem(extra_opts,container,info_container).
        % attr(extra_opts,flex_direction,column).
        % attr(extra_opts,class,("d-flex";"flex-row";"justify-content-evenly";"p-2")).
        % attr(extra_opts,background_color,"#ededed").
        % attr(extra_opts,order,3).

        %     elem(inferences_btn,button,extra_opts).
        %     attr(inferences_btn,label,"Add inferences").
        %     attr(inferences_btn,icon,"fa-plus").
        %     attr(inferences_btn,class,("btn-outline-secondary")).
        %     attr(inferences_btn,order,1).

        %     elem(clear_checks_btn,button,extra_opts).
        %     attr(clear_checks_btn,label,"Clear checks").
        %     attr(clear_checks_btn,icon,"fa-eraser").
        %     attr(clear_checks_btn,class,("btn-outline-danger")).
        %     attr(clear_checks_btn,order,2).

        %     elem(clear_config_btn,button,extra_opts).
        %     attr(clear_config_btn,label,"Clear configuration").
        %     attr(clear_config_btn,icon,"fa-trash").
        %     attr(clear_config_btn,class,("btn-danger")).
        %     attr(clear_config_btn,order,3).

        %     elem(btn1,button,extra_opts).
        %     attr(btn1,label,"placeholder").
        %     attr(btn1,order,4).

% Contex menu
elem(edit_context(ID),context_menu,w) :- ooasp_isa(_,ID).
    %elem(attr_context_menu(ID),context_menu, w) :- ooasp_isa(_,ID).

        %elem(attribute_context(ID),button, edit_context(ID)) :- ooasp_isa(_,ID).
        %attr(attribute_context(ID),label, "Set Attributes") :- ooasp_isa(_,ID).
        %when(attribute_context(ID),click,update,(attr_context_menu(ID),visibility, shown)) :- ooasp_isa(_,ID).

    elem(add_assumption(NAME,VALUE,ID),button,edit_context(ID)) :- _any(ooasp_attr_value(NAME,ID,VALUE)), not _clinguin_assume(ooasp_attr_value(NAME,ID,VALUE),true).
    attr(add_assumption(NAME,VALUE,ID),label,@format("Assign {}:{}",NAME,VALUE)) :- _any(ooasp_attr_value(NAME,ID,VALUE)), not _clinguin_assume(ooasp_attr_value(NAME,ID,VALUE),true).
    attr(add_assumption(NAME,VALUE,ID),class,("bg-primary")) :- _any(ooasp_attr_value(NAME,ID,VALUE)), not _clinguin_assume(ooasp_attr_value(NAME,ID,VALUE),true).
    when(add_assumption(NAME,VALUE,ID),click,call,add_assumption(ooasp_attr_value(NAME,ID,VALUE))) :- _any(ooasp_attr_value(NAME,ID,VALUE)), not _clinguin_assume(ooasp_attr_value(NAME,ID,VALUE),true).

    elem(remove_assumption(NAME,VALUE,ID),button,edit_context(ID)) :- _clinguin_assume(ooasp_attr_value(NAME,ID,VALUE),true).
    attr(remove_assumption(NAME,VALUE,ID),label,@format("Remove assumption {}:{}",NAME,VALUE)) :- _clinguin_assume(ooasp_attr_value(NAME,ID,VALUE),true).
    attr(remove_assumption(NAME,VALUE,ID),class,("bg-warning")) :- _clinguin_assume(ooasp_attr_value(NAME,ID,VALUE),true).
    when(remove_assumption(NAME,VALUE,ID),click,call,remove_assumption(ooasp_attr_value(NAME,ID,VALUE))) :- _clinguin_assume(ooasp_attr_value(NAME,ID,VALUE),true).

    elem(add_association(NAME_FROM,NAME_TO),button,edit_context(NAME_FROM)) :- _any(ooasp_associated(NAME,NAME_FROM,NAME_TO)), not _clinguin_assume(ooasp_associated(NAME,NAME_FROM,NAME_TO),true).
    attr(add_association(NAME_FROM,NAME_TO),label,@format("Associate to {} via {}",NAME_TO,NAME)) :- _any(ooasp_associated(NAME,NAME_FROM,NAME_TO)), not _clinguin_assume(ooasp_associated(NAME,NAME_FROM,NAME_TO),true).
    attr(add_association(NAME_FROM,NAME_TO),class,("bg-secondary")) :- _any(ooasp_associated(NAME,NAME_FROM,NAME_TO)), not _clinguin_assume(ooasp_associated(NAME,NAME_FROM,NAME_TO),true).
    when(add_association(NAME_FROM,NAME_TO),click,call,add_assumption(ooasp_associated(NAME,NAME_FROM,NAME_TO))) :- _any(ooasp_associated(NAME,NAME_FROM,NAME_TO)), not _clinguin_assume(ooasp_associated(NAME,NAME_FROM,NAME_TO),true).

    elem(remove_association(NAME_FROM,NAME_TO),button,edit_context(NAME_FROM)) :- _clinguin_assume(ooasp_associated(NAME,NAME_FROM,NAME_TO),true).
    attr(remove_association(NAME_FROM,NAME_TO),label,@format("Remove association {}:{}",NAME_TO,NAME)) :- _clinguin_assume(ooasp_associated(NAME,NAME_FROM,NAME_TO),true).
    attr(remove_association(NAME_FROM,NAME_TO),class,("bg-warning")) :- _clinguin_assume(ooasp_associated(NAME,NAME_FROM,NAME_TO),true).
    when(remove_association(NAME_FROM,NAME_TO),click,call,remove_assumption(ooasp_associated(NAME,NAME_FROM,NAME_TO))) :- _clinguin_assume(ooasp_associated(NAME,NAME_FROM,NAME_TO),true).
    
% dev borers
%attr(E,class,("border-1";"border";"border-dark")):- elem(E, container, _).