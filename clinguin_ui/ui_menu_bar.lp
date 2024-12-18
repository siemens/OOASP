% Copyright (c) 2024 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

#const help_message = @concat(
    "<p><i>This UI allows the user to create a configuration in an interactive manner.</i></p>",
    "<h5>Add objects</h5>",
    "<p>In the 'Add object' section, the user can add a new object to the system. Only leaf classes can be added as objects. Click on the [+] button to add the object.</p>",
    "<h5>Edit objects</h5>",
    "<p>Click on the node in the configuration graph to edit the object. The lower right panel will show the selected node and possible changes.</p>",
    "<h5>Partial and full configuration</h5>",
    "<p>The yellow button on the menu can toggle between a partial and a full configuration. In a partial configuration, objects might not have values for attributes, and lower bounds might not be filled. In a full configuration, the system will enforce the complete configuration.</p>",
    "<h5>Find incrementally</h5>",
    "<p>Click on the 'Find incrementally' button to allow the system to create all the required objects and to complete the configuration.</p>",
    "<h5>Next solution</h5>",
    "<p>Browse the solutions for a complete configuration. The new information is highlighted in green.</p>",
    "<h5>Select a solution</h5>",
    "<p>When browsing the solutions, select the one that you want to keep.</p>",
    ""
).
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
        attr(help_modal,class,("justify-content-start")).

            elem(help_text,label,help_modal).
            attr(help_text,label,help_message).
            attr(help_text,class,("text-start";"fw-light";"lh-sm")).

    % ------------ Restart button ----------

    elem(restart_btn,button,menu_bar).
    attr(restart_btn,label,"Restart").
    attr(restart_btn,icon,"fa-trash").
    attr(restart_btn,class,("btn-danger")).
    when(restart_btn,click,update,(restart_confirmation,visibility,shown)).

        % ----------- Restart confirmation
        elem(restart_confirmation,modal,w).
        attr(restart_confirmation,title,"Restart configuration").
        attr(restart_confirmation,size,"lg").

            elem(modal_content,container,restart_confirmation).
            attr(modal_content,class,("d-flex";"flex-column")).

                elem(restart_btn_container,container,modal_content).
                attr(restart_btn_container,flex_direction,row).
                attr(restart_btn_container,class,("d-flex";"flex-row";"justify-content-end";"m-3")).
                attr(restart_btn_container,order,2).

                    elem(restart_yes,button,restart_btn_container).
                    attr(restart_yes,label,"Yes").
                    attr(restart_yes,icon,"fa-trash").
                    attr(restart_yes,class,("btn-danger";"m-1")).
                    attr(restart_yes,order,2).
                    when(restart_yes,click,call,restart).


                    elem(restart_no,button,restart_btn_container).
                    attr(restart_no,label,"No").
                    attr(restart_no,icon,"fa-x").
                    attr(restart_no,class,("btn-outline-danger";"m-1")).
                    attr(restart_no,order,1).
                    when(restart_no,click,update,(restart_confirmation,visibility,hidden)).

                elem(restart_msg,label,modal_content).
                attr(restart_msg,label,"This action will remove everything and cannot be undone, are you sure you want to proceed?").
                attr(restart_msg,order,1).



    %----------ENFORCEMENT SWITCH----------
    elem(enforce_btn,button,menu_bar).
    attr(enforce_btn,label,"Enforce Complete Configuration") :- _clinguin_external(check_potential_cv,false).
    attr(enforce_btn,label,"Allow partial configuration.") :- _clinguin_external(check_potential_cv,true).

    attr(enforce_btn,icon,"fa-circle") :- _clinguin_external(check_potential_cv,false).
    attr(enforce_btn,icon,"fa-circle-half-stroke") :- _clinguin_external(check_potential_cv,true).

    attr(enforce_btn,class,("btn-outline-warning")):- _clinguin_external(check_potential_cv,false).
    attr(enforce_btn,class,("btn-warning")):- _clinguin_external(check_potential_cv,true).
    when(enforce_btn,click,call,(set_external(check_potential_cv,true))):- _clinguin_external(check_potential_cv,false).
    when(enforce_btn,click,call,(set_external(check_potential_cv,false))):- _clinguin_external(check_potential_cv,true).

    %-------------------------------------

    elem(menu_bar_load, button, menu_bar).
    attr(menu_bar_load,label, "Load").
    attr(menu_bar_load, icon, "fa-upload").
    attr(menu_bar_load, class, ("btn-outline-primary";"border-0")).
    when(menu_bar_load,click,update,(load_modal,visibility,shown)).

        elem(load_modal,modal,w).
        attr(load_modal,title,"Load file").
            elem(c_load, container, load_modal).
            attr(c_load, flex_direction, "column").
            attr(c_load, class, "align-items-end").

                elem(b2, button, c_load).
                when(b2, click, call, import_solution(_context_value(file_name,str,"ooasp_configuration.lp"))).
                attr(b2, label, "Load").
                attr(b2, class, "m-1").
                attr(b2, class, "btn-primary").
                attr(b2, icon, "fa-file-code").

                elem(t2, textfield, c_load).
                attr(t2, placeholder, "ooasp_configuration.lp").
                attr(t2, width, 450).
                when(t2, input, context, (file_name, _value)).

    elem(menu_bar_save, button, menu_bar).
    attr(menu_bar_save,label, "Save").
    attr(menu_bar_save, icon, "fa-download").
    attr(menu_bar_save, class, ("btn-outline-primary";"border-0")).
    when(menu_bar_save,click,update,(save_modal,visibility,shown)).

        elem(save_modal,modal,w).
        attr(save_modal,title,"Save file").
            elem(c_save, container, save_modal).
            attr(c_save, flex_direction, "column").
            attr(c_save, class, "align-items-end").

                elem(b1, button, c_save).
                when(b1, click, call, download(show_prg,_context_value(file_name,str,"ooasp_configuration.lp"))).
                attr(b1, label, "Save").
                attr(b1, class, "m-1").
                attr(b1, class, "btn-primary").
                attr(b1, icon, "fa-download").

                elem(t1, textfield, c_save).
                attr(t1, placeholder, "ooasp_configuration.lp").
                attr(t1, width, 450).
                when(t1, input, context, (file_name, _value)).

    elem(end_btn,button,menu_bar):-_clinguin_browsing.
    attr(end_btn,label,"End browsing"):-_clinguin_browsing.
    attr(end_btn,icon,"fa-xmark"):-_clinguin_browsing.
    attr(end_btn,class,("btn-success")):-_clinguin_browsing.
    when(end_btn,click,call,stop_browsing):-_clinguin_browsing.

    elem(find_btn,button,menu_bar).
    attr(find_btn,label,"Find Incrementally").
    attr(find_btn,icon,"fa-gears").
    attr(find_btn,class,("btn-outline-secondary")).
    when(find_btn,click,call,find_incrementally).

    elem(suggest_btn,button,menu_bar):- _clinguin_external(check_potential_cv,true).
    attr(suggest_btn,label,"Next Solution") :- _clinguin_external(check_potential_cv,true).
    attr(suggest_btn,icon,"fa-forward") :- _clinguin_external(check_potential_cv,true).
    attr(suggest_btn,class,("btn-outline-success")):- _clinguin_external(check_potential_cv,true).
    when(suggest_btn,click,call, next_solution):- _clinguin_external(check_potential_cv,true).

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