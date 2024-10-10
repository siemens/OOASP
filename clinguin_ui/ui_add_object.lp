% Copyright (c) 2024 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

elem(config_container, container,bottom_container).
        attr(config_container,flex_direction,column).
        attr(config_container,class,("p-3";"bg-info";"bg-opacity-10";"rounded";"border";"border-3";"m-2";"shadow")).
        attr(config_container,order,1).
        attr(config_container,width,280).

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
                        attr(addobject_dd,class,("m-2";"p-2";"border";"border-1";"bg-primary";"bg-opacity-10")).
                        attr(addobject_dd,class,("disabled")):- _clinguin_browsing.
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
                attr(domain_size_txt,label,@format("Domain Size: {}",DS)) :- domain_size(DS). 
                attr(domain_size_txt,class,("text-start";"fw-semibold";"fs-6")).
                attr(domain_size_txt,order,1).

                assigned_object(ID):- ooasp_isa(_,ID), _clinguin_browsing.
                assigned_object(ID):- _clinguin_assume(ooasp_isa(_,ID),true).
                configuration_size(S):- #count{1,ID:assigned_object(ID)} = S.

                elem(config_size_txt,label,info_container).
                attr(config_size_txt,label,@format("Configuration Size: {}",CS)):-configuration_size(CS).
                attr(config_size_txt,class,("text-start";"fw-semibold";"fs-6")).
                attr(config_size_txt,order,2).

                needed(global,C,N):-  _all(global_ub(C,N,_)), not _clinguin_browsing,
                    #max{ N' : _all(global_ub(C,N',_))} = N.
                needed(global,C,N):-  _all(global_lb(C,N,_)), not _clinguin_browsing,
                    #max{ N' : _all(global_lb(C,N',_))} = N.
                needed(local,C,N):-  _all(object_needed(ID,ASS,N,C,SIDE,_)), not _clinguin_browsing,
                    #max{ N' : _all(object_needed(ID,ASS,N',C,SIDE,_))} = N.
                needed(C,N):-needed(_,C,N).
                elem(global_cv(C),button,info_container):- needed(C,N).
                attr(global_cv(C),label,@format("Needs {} more: {}",(N,@stringify(C,true)))):- needed(C,N).
                attr(global_cv(C),icon,"fa-warning"):- needed(C,N).
                attr(global_cv(C),class,("text-start";"fs-6";"btn-outline-danger";"m-1")):- needed(C,N).
                when(global_cv(C),click,call,add_object(C, N)):- needed(C,N).
                attr(global_cv(C),order,3):- needed(C,N).





