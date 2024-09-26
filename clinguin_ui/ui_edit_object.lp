elem(edit_c, container,bottom_container).
    attr(edit_c,flex_direction,row).
    attr(edit_c,class,("justify-content-evenly";"p-2";"bg-info";"bg-opacity-10";"rounded";"border";"border-3";"m-2";"shadow")).
    attr(edit_c,order,1).

        elem(selected_object_c,container,edit_c).
        attr(selected_object_c,flex_direction,column).
        attr(selected_object_c,class,("p-3";"align-items-center")).
        attr(selected_object_c,order,1).

            elem(selected_object_cd,container,selected_object_c).
            attr(selected_object_cd,flex_direction,column).
            attr(selected_object_cd,class,"p-3").
            attr(selected_object_cd,class,("bg-warning";"bg-opacity-10";"border";"border-dark";"border-2")).
            attr(selected_object_cd,visibility,hidden).
            attr(selected_object_cd,order,1).
            attr(selected_object_cd,width,200).

                elem(selected_object_info,label,selected_object_cd).
                attr(selected_object_info,class,("h6";"p-1";"fw-light")).
                attr(selected_object_info,order,2).

                elem(selected_object,label,selected_object_cd).
                attr(selected_object,class,("h5")).
                attr(selected_object,order,1).

            elem(deselect_c, container, selected_object_c).
            attr(deselect_c, child_layout, absstatic).
            attr(deselect_c, class, ("bg-primary")).
            attr(deselect_c, width, 100).
            attr(deselect_c, order,1).

                isa_remove(ID) :- ooasp_domain(_, ID), not ooasp_must_be_included(_,ID).

                elem(deselect_btn_c(ID),container, deselect_c):-ooasp_domain(_,ID).
                attr(deselect_btn_c(ID),pos_x, 0):-ooasp_domain(_,ID).
                attr(deselect_btn_c(ID),pos_y, 100):-ooasp_domain(_,ID).
                attr(deselect_btn_c(ID),visibility, hidden):-ooasp_domain(_,ID).
                attr(deselect_btn_c(ID),width, 100):-ooasp_domain(_,ID).


                    elem(deselect_btn(ID),button, deselect_btn_c(ID)):-ooasp_domain(_,ID).
                    attr(deselect_btn(ID),label,"Clear"):-ooasp_domain(_,ID).
                    attr(deselect_btn(ID),icon,"fa-ban"):-ooasp_domain(_,ID).
                    attr(deselect_btn(ID),class,("btn-sm";"btn-danger")):-ooasp_domain(_,ID).
                    when(deselect_btn(ID),click,call,remove_assumption(ooasp_isa(C,ID))) :- isa_remove(ID), _clinguin_assume(ooasp_isa(C, ID),true).
                    when(deselect_btn(ID),click,call,remove_assumption(ooasp_associated(A, ID, ID'))) :- ooasp_domain(_,ID), _clinguin_assume(ooasp_associated(A, ID, ID'),true).
                    when(deselect_btn(ID),click,call,remove_assumption(ooasp_associated(A, ID', ID))) :- ooasp_domain(_,ID), _clinguin_assume(ooasp_associated(A, ID', ID),true).
                    when(deselect_btn(ID),click,call,remove_assumption(ooasp_attr_value(N, ID, V))) :- ooasp_domain(_,ID), _clinguin_assume(ooasp_attr_value(N, ID, V),true).


        elem(edit_value,container,edit_c).
        attr(edit_value,flex_direction,column).
        attr(edit_value,class,("overflow-auto";"p-2";"bg-primary";"bg-opacity-10";"rounded-start";"border";"border-2";"border-end-0";"border-secondary")).
        attr(edit_value,order,2).
        attr(edit_value,width,400).

            elem(edit_value_label,label,edit_value).
            attr(edit_value_label,label,"Attribute Values").
            attr(edit_value_label,order,2).
            attr(edit_value_label,class,"h6").


            elem(all_edit_opts,container,edit_value) :- ooasp_domain(_,ID).
            attr(all_edit_opts,child_layout,absstatic).
            attr(all_edit_opts,order,1).


                elem(value_edit_options(ID),container,all_edit_opts) :- ooasp_domain(_,ID).
                attr(value_edit_options(ID),visibility,hidden) :- ooasp_domain(_,ID).
                attr(value_edit_options(ID),order,2) :- ooasp_domain(_,ID).
                attr(value_edit_options(ID),pos_x,30) :- ooasp_domain(_,ID).
                attr(value_edit_options(ID),pos_y,30) :- ooasp_domain(_,ID).

                    value_assume(NAME,VALUE,ID) :- _any(ooasp_attr_value(NAME,ID,VALUE)), not _clinguin_assume(ooasp_attr_value(NAME,ID,VALUE),true).
                    elem(add_assumption(NAME,VALUE,ID),button,value_edit_options(ID)) :- value_assume(NAME,VALUE,ID).
                    attr(add_assumption(NAME,VALUE,ID),label,@format("{} := {}",NAME,VALUE)) :- value_assume(NAME,VALUE,ID).
                    attr(add_assumption(NAME,VALUE,ID),class,("btn-outline-primary";"m-1")) :- value_assume(NAME,VALUE,ID).
                    when(add_assumption(NAME,VALUE,ID),click,call,add_assumption(ooasp_attr_value(NAME,ID,VALUE))) :- value_assume(NAME,VALUE,ID).

                    value_remove_assume(NAME,VALUE,ID) :- _clinguin_assume(ooasp_attr_value(NAME,ID,VALUE),true).
                    elem(remove_assumption(NAME,VALUE,ID),button,value_edit_options(ID)) :-value_remove_assume(NAME,VALUE,ID).
                    attr(remove_assumption(NAME,VALUE,ID),icon,"fa-trash") :-value_remove_assume(NAME,VALUE,ID).
                    attr(remove_assumption(NAME,VALUE,ID),label,@format("{} := {}",NAME,VALUE)) :-value_remove_assume(NAME,VALUE,ID).
                    attr(remove_assumption(NAME,VALUE,ID),class,("btn-outline-danger";"m-1")) :-value_remove_assume(NAME,VALUE,ID).
                    when(remove_assumption(NAME,VALUE,ID),click,call,remove_assumption(ooasp_attr_value(NAME,ID,VALUE))) :-value_remove_assume(NAME,VALUE,ID).



        elem(edit_assoc,container,edit_c).
        attr(edit_assoc,flex_direction,column).
        attr(edit_assoc,class,("overflow-auto";"p-2";"bg-secondary";"bg-opacity-10";"rounded-end";"border";"border-2";"border-start-0";"border-secondary")).
        attr(edit_assoc,order,3).
        attr(edit_assoc,width,400).

            elem(edit_assoc_label,label,edit_assoc).
            attr(edit_assoc_label,label,"Object Associations").
            attr(edit_assoc_label,order,2).
            attr(edit_assoc_label,class,"h6").

            elem(all_assoc_opts,container,edit_assoc) :- ooasp_domain(_,ID).
            attr(all_assoc_opts,child_layout,absstatic).
            attr(all_assoc_opts,order,1).

                elem(assoc_edit_options(ID),container,all_assoc_opts) :- ooasp_domain(_,ID).
                attr(assoc_edit_options(ID),visibility,hidden) :- ooasp_domain(_,ID).
                attr(assoc_edit_options(ID),order,2) :- ooasp_domain(_,ID).
                attr(assoc_edit_options(ID),pos_x,30) :- ooasp_domain(_,ID).
                attr(assoc_edit_options(ID),pos_y,30) :- ooasp_domain(_,ID).


                    assoc_assume(ASSOC,ID_FROM,ID_TO,left) :- _any(ooasp_associated(ASSOC,ID_FROM,ID_TO)), not _clinguin_assume(ooasp_associated(ASSOC,ID_FROM,ID_TO),true), ooasp_smallest_assoc(ASSOC).
                    assoc_assume(ASSOC,ID_TO,ID_FROM,right) :- _any(ooasp_associated(ASSOC,ID_FROM,ID_TO)), not _clinguin_assume(ooasp_associated(ASSOC,ID_FROM,ID_TO),true), ooasp_smallest_assoc(ASSOC).
                    elem(add_association(ASSOC,ID_FROM,ID_TO,L_OR_R),button,assoc_edit_options(ID_FROM)) :- assoc_assume(ASSOC,ID_FROM,ID_TO,L_OR_R).
                    attr(add_association(ASSOC,ID_FROM,ID_TO,left),label,@format("{} → {}",ASSOC,ID_TO)) :- assoc_assume(ASSOC,ID_FROM,ID_TO,left).
                    attr(add_association(ASSOC,ID_FROM,ID_TO,right),label,@format("{} ← {}",ASSOC,ID_TO)) :- assoc_assume(ASSOC,ID_FROM,ID_TO,right).
                    attr(add_association(ASSOC,ID_FROM,ID_TO,L_OR_R),class,("btn-outline-secondary";"m-1")) :- assoc_assume(ASSOC,ID_FROM,ID_TO,L_OR_R).
                    when(add_association(ASSOC,ID_FROM,ID_TO,left),click,call,add_assumption(ooasp_associated(ASSOC,ID_FROM,ID_TO))) :- assoc_assume(ASSOC,ID_FROM,ID_TO,left).
                    when(add_association(ASSOC,ID_FROM,ID_TO,right),click,call,add_assumption(ooasp_associated(ASSOC,ID_TO,ID_FROM))) :- assoc_assume(ASSOC,ID_FROM,ID_TO,right).

                    assoc_remove(ASSOC, ID_FROM, ID_TO,left) :- _clinguin_assume(ooasp_associated(ASSOC,ID_FROM,ID_TO),true), ooasp_smallest_assoc(ASSOC).
                    assoc_remove(ASSOC, ID_TO, ID_FROM,right) :- _clinguin_assume(ooasp_associated(ASSOC,ID_FROM,ID_TO),true), ooasp_smallest_assoc(ASSOC).
                    elem(remove_association(ASSOC,ID_FROM,ID_TO),button,assoc_edit_options(ID_FROM)) :- assoc_remove(ASSOC, ID_FROM, ID_TO,_).
                    attr(remove_association(ASSOC,ID_FROM,ID_TO),icon,"fa-trash") :- assoc_remove(ASSOC, ID_FROM, ID_TO,_).
                    attr(remove_association(ASSOC,ID_FROM,ID_TO),label,@format("{} → {}",ASSOC,ID_TO)) :- assoc_remove(ASSOC, ID_FROM, ID_TO,_).
                    attr(remove_association(ASSOC,ID_FROM,ID_TO),class,("btn-outline-danger";"m-1")) :- assoc_remove(ASSOC, ID_FROM, ID_TO,_).
                    when(remove_association(ASSOC,ID_FROM,ID_TO),click,call,remove_assumption(ooasp_associated(ASSOC,ID_FROM,ID_TO))) :- assoc_remove(ASSOC, ID_FROM, ID_TO,left).
                    when(remove_association(ASSOC,ID_FROM,ID_TO),click,call,remove_assumption(ooasp_associated(ASSOC,ID_TO,ID_FROM))) :- assoc_remove(ASSOC, ID_FROM, ID_TO,right).


