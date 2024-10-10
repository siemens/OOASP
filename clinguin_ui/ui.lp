% Copyright (c) 2024 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

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
