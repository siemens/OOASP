#const show_prg = "#show ooasp_associated/3. #show ooasp_attr_value/3. #show ooasp_isa(C,ID):ooasp_isa_leaf(C,ID).".
elem(w,window,root).
attr(w,flex_direction,row).


% ================= Menu bar

elem(menu_bar,menu_bar,w).
attr(menu_bar,title,"OOASP").
attr(menu_bar,icon,"fa-puzzle-piece").

    % ---------- Help ----------
    elem(help_btn,button,menu_bar).
    attr(help_btn,icon,"fa-circle-question").
    attr(help_btn,class,("btn-light")).
    when(help_btn,click,update,(help_modal,visibility,shown)).

        elem(help_modal,modal,w).
        attr(help_modal,title,"Help").
        attr(help_modal,size,"xl").
        attr(help_modal,class,("justify-content-start")). %Check if this actually does anything.

            elem(help_text,label,help_modal).
            attr(help_text,label,"TBA (help text)").

    % ------------ Restart button ----------

    elem(restart_btn,button,menu_bar).
    attr(restart_btn,label,"Restart").
    attr(restart_btn,icon,"fa-trash").
    attr(restart_btn,class,("btn-danger")).
    when(restart_btn,click,update,(restart_confirmation,visibility,shown)).

        % ----------- Restart confirmation
        elem(restart_confirmation,modal,w).
        attr(restart_confirmation,title,"Restart configuration?").
        attr(restart_confirmation,size,"lg").

            elem(modal_content,container,restart_confirmation).
            attr(modal_content,class,("d-flex";"flex-column")).

                elem(restart_btn_container,container,modal_content).
                attr(restart_btn_container,flex_direction,row).
                attr(restart_btn_container,class,("d-flex";"flex-row")).
                attr(restart_btn_container,order,2).

                    elem(restart_yes,button,restart_btn_container).
                    attr(restart_yes,label,"Yes").
                    attr(restart_yes,icon,"fa-trash").
                    attr(restart_yes,class,"btn-primary").
                    attr(restart_yes,order,2).
                    when(restart_yes,click,call,restart).


                    elem(restart_no,button,restart_btn_container).
                    attr(restart_no,label,"No").
                    attr(restart_no,icon,"fa-x").
                    attr(restart_no,class,"btn-outline-primary").
                    attr(restart_no,order,1).
                    when(restart_no,click,update,(restart_confirmation,visibility,hidden)).

                elem(restart_msg,label,modal_content).
                attr(restart_msg,label,"This action cannot be undone, are you sure you want to proceed?").
                attr(restart_msg,class,"text-danger").
                attr(restart_msg,order,1).



    %----------ENFORCEMENT SWITCH----------
    elem(next_btn,button,menu_bar).
    attr(next_btn,label,"Enforce Complete Configuration") :- _clinguin_external(check_potential_cv,false).
    attr(next_btn,label,"Allow partial configuration.") :- _clinguin_external(check_potential_cv,true).

    attr(next_btn,icon,"fa-circle") :- _clinguin_external(check_potential_cv,false).
    attr(next_btn,icon,"fa-circle-half-stroke") :- _clinguin_external(check_potential_cv,true).

    attr(next_btn,class,("btn-outline-primary")):- _clinguin_external(check_potential_cv,false).
    attr(next_btn,class,("btn-primary")):- _clinguin_external(check_potential_cv,true).
    when(next_btn,click,call,(set_external(check_potential_cv,true))):- _clinguin_external(check_potential_cv,false).
    when(next_btn,click,call,(set_external(check_potential_cv,false))):- _clinguin_external(check_potential_cv,true).

    %-------------------------------------

    elem(menu_bar_load, button, menu_bar).
    attr(menu_bar_load,label, "Load").
    attr(menu_bar_load, icon, "fa-upload").
    attr(menu_bar_load, class, ("btn-outline-primary";"border-0")).
    when(menu_bar_load,click,call,import_solution).

    elem(menu_bar_save, button, menu_bar).
    attr(menu_bar_save,label, "Save").
    attr(menu_bar_save, icon, "fa-download").
    attr(menu_bar_save, class, ("btn-outline-primary";"border-0")).
    % when(menu_bar_save,click,call,export_solution).
    when(menu_bar_save,click,update,(save_modal,visibility,shown)).

        %TODO on click show modal with entry option to select a file path


        elem(save_modal,modal,w).
        attr(save_modal,title,"Save file").
        % attr(save_modal,size,"sm").
            elem(c_save, container, save_modal).
            attr(c_save, flex_direction, "column").
            attr(c_save, class, "align-items-end").

                elem(b1, button, c_save).
                when(b1, click, call, download(show_prg,_context_value(file_name,str,"ooasp_configuration.lp"))).
                attr(b1, label, "Save").
                attr(b1, class, "m-1").
                attr(b1, class, "btn-success").
                attr(b1, icon, "fa-download").

                elem(t1, textfield, c_save).
                attr(t1, placeholder, "Optional file name").
                attr(t1, width, 450).
                when(t1, input, context, (file_name, _value)).

    elem(end_btn,button,menu_bar):-_clinguin_browsing.
    attr(end_btn,label,"End browsing"):-_clinguin_browsing.
    attr(end_btn,icon,"fa-xmark"):-_clinguin_browsing.
    attr(end_btn,class,("btn-warning")):-_clinguin_browsing.
    when(end_btn,click,call,stop_browsing):-_clinguin_browsing.

    elem(find_btn,button,menu_bar).
    attr(find_btn,label,"Find Incrementally").
    attr(find_btn,icon,"fa-gears").
    attr(find_btn,class,("btn-outline-secondary")).
    when(find_btn,click,call,find_incrementally).

    elem(suggest_btn,button,menu_bar).
    attr(suggest_btn,label,"Next Solution") :- _clinguin_external(check_potential_cv,true).
    attr(suggest_btn,label,"Make suggestion") :- _clinguin_external(check_potential_cv,false), not _clinguin_browsing.
    attr(suggest_btn,label,"Next suggestion") :- _clinguin_external(check_potential_cv,false),_clinguin_browsing.
    attr(suggest_btn,icon,"fa-forward") :- _clinguin_external(check_potential_cv,true).
    attr(suggest_btn,icon,"fa-border-top-left") :- _clinguin_external(check_potential_cv,false).
    attr(suggest_btn,class,("btn-outline-success")) :- _clinguin_external(check_potential_cv,false).
    attr(suggest_btn,class,("btn-success")) :- _clinguin_external(check_potential_cv,true).
    when(suggest_btn,click,call, next_solution).

    elem(select_btn,button,menu_bar) :- _clinguin_browsing.
    attr(select_btn,label,"Select solution") :- _clinguin_browsing, _clinguin_external(check_potential_cv,true).
    attr(select_btn,label,"Select suggestion") :- _clinguin_browsing, _clinguin_external(check_potential_cv,false).
    attr(select_btn,class,("btn-outline-success")) :- _clinguin_browsing.
    attr(select_btn, icon, "fa-hand-pointer") :- _clinguin_browsing.
    when(select_btn, click, call, select(show_prg)) :- _clinguin_browsing.

elem(unsat_msg, message, w):-_clinguin_unsat.
attr(unsat_msg, message, "No solution with the current objects"):-_clinguin_unsat.
attr(unsat_msg, type, "error"):-_clinguin_unsat.
attr(unsat_msg, title, "Unsatisfiable"):-_clinguin_unsat.

    % elem(check_btn,button,menu_bar).
    % attr(check_btn,label,"Check").
    % attr(check_btn,icon,"fa-magnifying-glass").
    % attr(check_btn,class,("btn-outline-danger")).

elem(window_flex, container,w).
attr(window_flex, flex_direction,column).

    % ================= Clingraph image

    elem(config_viz, canvas,window_flex).
    % attr(config_viz,class,("vw-75";"vh-75")).
    attr(config_viz, image_type, clingraph__config).
            #include "ooasp/encodings/viz_config_nodes.lp".

            elem(n(X), svg_node, config_viz) :- node(X,config).
            attr(n(X), clingraph_id, X) :- node(X,config).
            % when(n(ID), click, update, (edit_context(ID), visibility, shown)):- node(ID,config).
            % when(n(ID), click, update, (edit_context(ID), visibility, shown)):- node(ID,config).
            when(n(X),click,update,(selected_object,label,@format("{}",X))) :- node(X,config).
            when(n(X),click,update,(assoc_edit_options(X),visibility,shown)) :- node(X,config).
            when(n(X),click,update,(assoc_edit_options(X'),visibility,hidden)) :- node(X,config), node(X',config), X'!=X.
            when(n(X),click,update,(value_edit_options(X),visibility,shown)) :- node(X,config).
            when(n(X),click,update,(value_edit_options(X'),visibility,hidden)) :- node(X,config), node(X',config), X'!=X.
            when(n(X),click,update,(deselect_btn_c(X),visibility,shown)) :- node(X,config).
            when(n(X),click,update,(deselect_btn_c(X'),visibility,hidden)) :- node(X,config), node(X',config), X'!=X.

    attr(config_viz,order,1).

    elem(bottom_container,container,window_flex).
    attr(bottom_container,flex_direction,row).
    attr(bottom_container,class,("fixed-bottom";"justify-content-between";"mh-50")).
    attr(bottom_container,order,3).

        % ================= Add object

        elem(config_container, container,bottom_container).
        attr(config_container,flex_direction,column).
        attr(config_container,class,("p-3";"bg-info";"bg-opacity-10";"rounded";"border";"border-3";"m-2";"shadow")).
        attr(config_container,order,1).
        attr(config_container,width,250).

            elem(extend_container,container,config_container).
            attr(extend_container,flex_direction,column).
            attr(extend_container,class,("col-sm";"flex-column")).
            attr(extend_container,order,2).

                elem(addobject_dd_container,container,extend_container).
                attr(addobject_dd_container,class,("d-flex";"flex-col";"mt-5";"align-items-start")).
                attr(addobject_dd_container,order,2).

                    elem(addobject_dd_label,label, addobject_dd_container).
                    attr(addobject_dd_label,label,"Add object").
                    attr(addobject_dd_label,class,("fw-semibold";"fs-5")).
                    attr(addobject_dd_label,order,1).

                    elem(addobject_dd_c,container,addobject_dd_container).
                    attr(addobject_dd_c,class,("d-flex";"flex-row";"mt-1")).
                    attr(addobject_dd_c,class,("opacity-20")):- _clinguin_browsing.
                    attr(addobject_dd_c,order,2).

                        elem(addobject_dd,dropdown_menu,addobject_dd_c).
                        attr(addobject_dd,selected,"object").
                        % attr(addobject_dd,class,("m-2";"p-2";"border";"border-1")).
                        attr(addobject_dd,class,("m-2";"p-2";"border";"border-1";"bg-primary";"bg-opacity-10")).
                        attr(class,class,("disabled")):- _clinguin_browsing.
                        attr(addobject_dd,order,1).

                        class_to_add(C) :- ooasp_leafclass(C).

                            elem(dd_element(C),dropdown_menu_item,addobject_dd):-class_to_add(C).
                            attr(dd_element(C),label,C):-class_to_add(C).
                            when(dd_element(C),click,context,(class_name,C)):-class_to_add(C).
                            when(dd_element(C),click,update,(addobject_dd,selected,C)):-class_to_add(C).


                        elem(addobject_dd_amount,dropdown_menu,addobject_dd_c).
                        attr(addobject_dd_amount,selected,"1").
                        attr(addobject_dd_amount,class,("m-2";"p-2";"border";"border-1";"bg-primary";"bg-opacity-10")).
                        attr(addobject_dd_amount,class,("disabled")):- _clinguin_browsing.
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
                        attr(addobject_btn,class,("opacity-25")):- _clinguin_browsing.
                        attr(addobject_btn,order,3).
                        when(addobject_btn,click,call,add_object(_context_value(class_name,const,object),_context_value(amount,int,1))):- not _clinguin_browsing.
                        when(addobject_btn,mouseenter,update,(add_warning,visibility,shown)):- _clinguin_browsing.

                            elem(add_warning, message, w).
                            attr(add_warning, message, "Adding objects is disabled while browsing").
                            attr(add_warning, type, "warning").
                            attr(add_warning, title, "Adding deactivated").
                            attr(add_warning, visibility, hidden).

            % Info container
            elem(info_container,container,config_container).
            attr(info_container,flex_direction,column).
            attr(info_container,class,("col-sm";"flex-column")).
            attr(info_container,order,1).

                domain_size(S):- #count{1,ID:ooasp_domain(_,ID)} = S.
                elem(domain_size_txt,label,info_container).
                attr(domain_size_txt,label,@format("Domain Size: {}",DS)) :- domain_size(DS). %TODO fix sizing
                attr(domain_size_txt,class,("text-start";"fw-semibold";"fs-6")).
                attr(domain_size_txt,order,1).

                assigned_object(ID):- ooasp_isa(_,ID), _clinguin_browsing.
                assigned_object(ID):- _clinguin_assume(ooasp_isa(_,ID),true).
                configuration_size(S):- #count{1,ID:assigned_object(ID)} = S.

                elem(config_size_txt,label,info_container).
                attr(config_size_txt,label,@format("Configuration Size: {}",CS)):-configuration_size(CS).
                attr(config_size_txt,class,("text-start";"fw-semibold";"fs-6")).
                attr(config_size_txt,order,2).

    % ================= Edit object
    elem(edit_c, container,bottom_container).
    attr(edit_c,flex_direction,row).
    attr(edit_c,class,("justify-content-evenly";"p-3";"bg-info";"bg-opacity-10";"rounded";"border";"border-3";"m-2";"shadow")).
    attr(edit_c,order,1).

        elem(selected_object_c,container,edit_c).
        attr(selected_object_c,flex_direction,column).
        attr(selected_object_c,class,("p-3";"align-items-center")).
        attr(selected_object_c,order,1).

            elem(selected_object_cd,container,selected_object_c).
            attr(selected_object_cd,flex_direction,row).
            attr(selected_object_cd,class,("p-3")).
            attr(selected_object_cd,order,1).

                elem(selected_object_info,label,selected_object_cd).
                attr(selected_object_info,label,"Selected Object: ").
                attr(selected_object_info,class,("h3")).
                attr(selected_object_info,order,1).

                elem(selected_object,label,selected_object_cd).
                attr(selected_object,label,"None").
                attr(selected_object,class,("text-primary";"h3";"p-2")).
                attr(selected_object,order,2).

            elem(deselect_c, container, selected_object_c).
            attr(deselect_c, child_layout, absstatic).
            attr(deselect_c,order,2).

                elem(deselect_btn_c(ID),container, deselect_c):-_clinguin_assume(ooasp_isa(C, ID),true).
                attr(deselect_btn_c(ID),pos_x, 0):-_clinguin_assume(ooasp_isa(C, ID),true).
                attr(deselect_btn_c(ID),pos_y, 0):-_clinguin_assume(ooasp_isa(C, ID),true).
                attr(deselect_btn_c(ID),visibility, hidden):-_clinguin_assume(ooasp_isa(C, ID),true).

                    elem(deselect_btn(ID),button, deselect_btn_c(ID)):-_clinguin_assume(ooasp_isa(C, ID),true).
                    attr(deselect_btn(ID),label,"Remove"):-_clinguin_assume(ooasp_isa(C, ID),true).
                    attr(deselect_btn(ID),icon,"fa-trash"):-_clinguin_assume(ooasp_isa(C, ID),true).
                    % when(deselect_btn(ID),click,update,(selected_object, label, "None")):-node(ID,_).
                    when(deselect_btn(ID),click,call,remove_assumption(ooasp_isa(C,ID))) :- _clinguin_assume(ooasp_isa(C, ID),true).


    % isa_remove(ID) :- _clinguin_assume(ooasp_isa(C, ID),true).
    % elem(remove_isa(ID),button,edit_context(ID)) :- isa_remove(ID).
    % attr(remove_isa(ID),icon,"fa-trash") :- isa_remove(ID).
    % attr(remove_isa(ID),label,"Un-assign class.") :- isa_remove(ID).
    % attr(remove_isa(ID),class,("text-white";"bg-danger")) :- isa_remove(ID).
    % when(remove_isa(ID),click,call,remove_assumption(ooasp_isa(C,ID))) :- isa_remove(ID), _clinguin_assume(ooasp_isa(C, ID),true).


        elem(edit_value,container,edit_c).
        attr(edit_value,flex_direction,column).
        attr(edit_value,class,("overflow-auto";"p-3";"bg-primary";"bg-opacity-25";"rounded-start";"border";"border-2";"border-end-0";"border-secondary")).
        attr(edit_value,order,2).
        attr(edit_value,width,400).

            elem(edit_value_label,label,edit_value).
            attr(edit_value_label,label,"Attribute Values").
            attr(edit_value_label,order,2).

            elem(all_edit_opts,container,edit_value) :- ooasp_domain(_,ID).
            attr(all_edit_opts,child_layout,absstatic).
            attr(all_edit_opts,order,1).


                elem(value_edit_options(ID),container,all_edit_opts) :- ooasp_domain(_,ID).
                attr(value_edit_options(ID),visibility,hidden) :- ooasp_domain(_,ID).
                attr(value_edit_options(ID),order,2) :- ooasp_domain(_,ID).
                attr(value_edit_options(ID),pos_x,20) :- ooasp_domain(_,ID).
                attr(value_edit_options(ID),pos_y,20) :- ooasp_domain(_,ID).

                    value_assume(NAME,VALUE,ID) :- _any(ooasp_attr_value(NAME,ID,VALUE)), not _clinguin_assume(ooasp_attr_value(NAME,ID,VALUE),true).
                    elem(add_assumption(NAME,VALUE,ID),button,value_edit_options(ID)) :- value_assume(NAME,VALUE,ID).
                    attr(add_assumption(NAME,VALUE,ID),label,@format("{} := {}",NAME,VALUE)) :- value_assume(NAME,VALUE,ID).
                    attr(add_assumption(NAME,VALUE,ID),class,("text-white";"bg-primary")) :- value_assume(NAME,VALUE,ID).
                    when(add_assumption(NAME,VALUE,ID),click,call,add_assumption(ooasp_attr_value(NAME,ID,VALUE))) :- value_assume(NAME,VALUE,ID).

                    value_remove_assume(NAME,VALUE,ID) :- _clinguin_assume(ooasp_attr_value(NAME,ID,VALUE),true).
                    elem(remove_assumption(NAME,VALUE,ID),button,value_edit_options(ID)) :-value_remove_assume(NAME,VALUE,ID).
                    attr(remove_assumption(NAME,VALUE,ID),icon,"fa-trash") :-value_remove_assume(NAME,VALUE,ID).
                    attr(remove_assumption(NAME,VALUE,ID),label,@format("{} := {}",NAME,VALUE)) :-value_remove_assume(NAME,VALUE,ID).
                    attr(remove_assumption(NAME,VALUE,ID),class,("text-white";"bg-danger")) :-value_remove_assume(NAME,VALUE,ID).
                    when(remove_assumption(NAME,VALUE,ID),click,call,remove_assumption(ooasp_attr_value(NAME,ID,VALUE))) :-value_remove_assume(NAME,VALUE,ID).



        elem(edit_assoc,container,edit_c).
        attr(edit_assoc,flex_direction,column).
        attr(edit_assoc,class,("overflow-auto";"p-3";"bg-secondary";"bg-opacity-25";"rounded-end";"border";"border-2";"border-start-0";"border-secondary")).
        attr(edit_assoc,order,3).
        attr(edit_assoc,width,400).

            elem(edit_assoc_label,label,edit_assoc).
            attr(edit_assoc_label,label,"Object Associations").
            attr(edit_assoc_label,order,2).

            elem(all_assoc_opts,container,edit_assoc) :- ooasp_domain(_,ID).
            attr(all_assoc_opts,child_layout,absstatic).
            attr(all_assoc_opts,order,1).

                elem(assoc_edit_options(ID),container,all_assoc_opts) :- ooasp_domain(_,ID).
                attr(assoc_edit_options(ID),visibility,hidden) :- ooasp_domain(_,ID).
                attr(assoc_edit_options(ID),order,2) :- ooasp_domain(_,ID).
                attr(assoc_edit_options(ID),pos_x,20) :- ooasp_domain(_,ID).
                attr(assoc_edit_options(ID),pos_y,20) :- ooasp_domain(_,ID).

                    assoc_assume(ASSOC,ID_FROM,ID_TO) :- _any(ooasp_associated(ASSOC,ID_FROM,ID_TO)), not _clinguin_assume(ooasp_associated(ASSOC,ID_FROM,ID_TO),true), ooasp_smallest_assoc(ASSOC).
                    elem(add_association(ASSOC,ID_FROM,ID_TO),button,assoc_edit_options(ID_FROM)) :- assoc_assume(ASSOC,ID_FROM,ID_TO).
                    attr(add_association(ASSOC,ID_FROM,ID_TO),label,@format("{} → {}",ASSOC,ID_TO)) :- assoc_assume(ASSOC,ID_FROM,ID_TO).
                    attr(add_association(ASSOC,ID_FROM,ID_TO),class,("text-white";"bg-secondary")) :- assoc_assume(ASSOC,ID_FROM,ID_TO).
                    when(add_association(ASSOC,ID_FROM,ID_TO),click,call,add_assumption(ooasp_associated(ASSOC,ID_FROM,ID_TO))) :- assoc_assume(ASSOC,ID_FROM,ID_TO).

                    assoc_remove(ASSOC, ID_FROM, ID_TO) :- _clinguin_assume(ooasp_associated(ASSOC,ID_FROM,ID_TO),true).
                    elem(remove_association(ASSOC,ID_FROM,ID_TO),button,assoc_edit_options(ID_FROM)) :- assoc_remove(ASSOC, ID_FROM, ID_TO).
                    attr(remove_association(ASSOC,ID_FROM,ID_TO),icon,"fa-trash") :- assoc_remove(ASSOC, ID_FROM, ID_TO).
                    attr(remove_association(ASSOC,ID_FROM,ID_TO),label,@format("{} → {}",ASSOC,ID_TO)) :- assoc_remove(ASSOC, ID_FROM, ID_TO).
                    attr(remove_association(ASSOC,ID_FROM,ID_TO),class,("text-white";"bg-danger")) :- assoc_remove(ASSOC, ID_FROM, ID_TO).
                    when(remove_association(ASSOC,ID_FROM,ID_TO),click,call,remove_assumption(ooasp_associated(ASSOC,ID_FROM,ID_TO))) :- assoc_remove(ASSOC, ID_FROM, ID_TO).


    % ================= Context menu

% elem(edit_context(ID),context_menu,w) :- ooasp_domain(_,ID).
%     elem(selector(ID),button,edit_context(ID)) :- ooasp_domain(_,ID).
%     attr(selector(ID),label,"Select for editing") :- ooasp_domain(_,ID).
%     attr(selector(ID),class,("bg-success")) :- ooasp_domain(_,ID).

    % when(selector(ID),click,update,(selected_object,label,@format("{}",ID))) :- ooasp_domain(_,ID).
    % when(selector(ID),click,update,(assoc_edit_options(ID),visibility,shown)) :- ooasp_domain(_,ID).
    % when(selector(ID),click,update,(value_edit_options(ID),visibility,shown)) :- ooasp_domain(_,ID).
    %when(selector(ID),click,update,(selector(ID),label,"Deselect")) :- ooasp_domain(_,ID).
    %when(selector(ID),click,update,(selector(ID),class,("bg-warning"))) :- ooasp_domain(_,ID).

    %elem(attr_context_menu(ID),context_menu, w) :- ooasp_isa(_,ID).

        %elem(attribute_context(ID),button, edit_context(ID)) :- ooasp_isa(_,ID).
        %attr(attribute_context(ID),label, "Set Attributes") :- ooasp_isa(_,ID).
        %when(attribute_context(ID),click,update,(attr_context_menu(ID),visibility, shown)) :- ooasp_isa(_,ID).





    % isa_remove(ID) :- _clinguin_assume(ooasp_isa(C, ID),true).
    % elem(remove_isa(ID),button,edit_context(ID)) :- isa_remove(ID).
    % attr(remove_isa(ID),icon,"fa-trash") :- isa_remove(ID).
    % attr(remove_isa(ID),label,"Un-assign class.") :- isa_remove(ID).
    % attr(remove_isa(ID),class,("text-white";"bg-danger")) :- isa_remove(ID).
    % when(remove_isa(ID),click,call,remove_assumption(ooasp_isa(C,ID))) :- isa_remove(ID), _clinguin_assume(ooasp_isa(C, ID),true).

    % dev borers
% attr(E,class,("border-1";"border";"border-dark")):- elem(E, container, _).