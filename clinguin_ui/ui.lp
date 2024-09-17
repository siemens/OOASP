#const show_prg = "#show ooasp_associated(A,ID1,ID2):ooasp_associated(A,ID1,ID2),ooasp_smallest_assoc(A). #show ooasp_attr_value/3. #show ooasp_isa(C,ID):ooasp_isa_leaf(C,ID).".
elem(w,window,root).
attr(w,flex_direction,row).

    #include "clinguin_ui/ui_menu_bar.lp".

elem(window_flex, container,w).
attr(window_flex, flex_direction,column).

    % ================= Clingraph image

    #include "clinguin_ui/ui_clingraph_canvas.lp".

    elem(bottom_container,container,window_flex).
    attr(bottom_container,flex_direction,row).
    attr(bottom_container,class,("fixed-bottom";"justify-content-between";"mh-50")).
    attr(bottom_container,order,3).

    % ================= Add object

    #include "clinguin_ui/ui_add_object.lp".

    % ================= Edit object

    #include "clinguin_ui/ui_edit_object.lp".

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