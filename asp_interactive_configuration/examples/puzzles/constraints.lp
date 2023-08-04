% Copyright (c) 2023 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT


ooasp_potential_cv(equal_nrofrows_gridsize).
ooasp_potential_cv(equal_nrofcolumns_gridsize).
ooasp_potential_cv(equal_nrofcellsinrow_gridsize).
ooasp_potential_cv(equal_nrofcellsincolumn_gridsize).
ooasp_potential_cv(missing_row_nr).
ooasp_potential_cv(missing_column_nr).
ooasp_potential_cv(cell_value_domain).

#program domain(new_object).

ooasp_cv(C,equal_nrofrows_gridsize,PUZZLE,"nrofrows must be equal to gridsize new {} puzzle {} gridsize {} nrofrows {}",(new_object,PUZZLE,GRIDSIZE,NROFROWS)):-
    ooasp_attribute_value(C,grid_size,PUZZLE,GRIDSIZE),
    NROFROWS = #count { ID2:ooasp_associated_general(C,puzzle_rows,1,PUZZLE,ID2) },
    NROFROWS!=GRIDSIZE,
    active(new_object).

ooasp_cv(C,equal_nrofcolumns_gridsize,PUZZLE,"nrofcolumns must be equal to gridsize new {} puzzle {} gridsize {} nrofrows {}",(new_object,PUZZLE,GRIDSIZE,NROFCOLUMNS)):-
    ooasp_attribute_value(C,grid_size,PUZZLE,GRIDSIZE),
    NROFCOLUMNS = #count { ID2:ooasp_associated_general(C,puzzle_columns,1,PUZZLE,ID2) },
    NROFCOLUMNS!=GRIDSIZE,
    active(new_object).

ooasp_cv(C,equal_nrofcellsinrow_gridsize,PUZZLE,"nrofcells in row must be equal to gridsize new {} row {} gridsize {} nrofrows {}",(new_object,ROW,GRIDSIZE,NROFCELLS)):-
    ooasp_attribute_value(C,grid_size,PUZZLE,GRIDSIZE),
    ooasp_associated(C,puzzle_rows,PUZZLE,ROW),
    NROFCELLS = #count { ID2:ooasp_associated_general(C,row_cells,1,ROW,ID2) },
    NROFCELLS!=GRIDSIZE,
    active(new_object).

ooasp_cv(C,equal_nrofcellsincolumn_gridsize,PUZZLE,"nrofcells in column must be equal to gridsize new {} row {} gridsize {} nrofrows {}",(new_object,COLUMN,GRIDSIZE,NROFCELLS)):-
   ooasp_attribute_value(C,grid_size,PUZZLE,GRIDSIZE),
   ooasp_associated(C,puzzle_columns,PUZZLE,COLUMN),
    NROFCELLS = #count { ID2:ooasp_associated_general(C,column_cells,1,COLUMN,ID2) },
    NROFCELLS!=GRIDSIZE,
    active(new_object).

ooasp_cv(C,missing_row_nr,PUZZLE,"missing row_nr new {} puzzle {} value {} count {}",(new_object,PUZZLE,VALUE,COUNT)):-
    ooasp_attribute_value(C,grid_size,PUZZLE,GRIDSIZE),
    COUNT!=1,
    COUNT = #count { NROFROW:NROFROW=VALUE,ooasp_attribute_value(C,row_nr,ROW,NROFROW),ooasp_associated(C,puzzle_rows,PUZZLE,ROW) },
    VALUE=1..GRIDSIZE,
    active(new_object).

ooasp_cv(C,missing_column_nr,PUZZLE,"missing column_nr new {} puzzle {} value {} count {}",(new_object,PUZZLE,VALUE,COUNT)):-
    ooasp_attribute_value(C,grid_size,PUZZLE,GRIDSIZE),
    COUNT!=1,
    COUNT = #count { NROFCOLUMN:NROFCOLUMN=VALUE,ooasp_attribute_value(C,column_nr,ROW,NROFCOLUMN),ooasp_associated(C,puzzle_columns,PUZZLE,ROW) },
    VALUE=1..GRIDSIZE,
    active(new_object).

% latinsquare or sudoko have domain 1..GRIDSIZE
ooasp_cv(C,cell_value_domain,PUZZLE,"cell value = 1..GRIDSIZE {} puzzle {} cell {} value {}",(new_object,PUZZLE,CELL,VALUE)):-
    ooasp_isa(C,latinSquareOrSudoku,PUZZLE),
    ooasp_attribute_value(C,grid_size,PUZZLE,GRIDSIZE),
    ooasp_attribute_value(C,cell_value,CELL,VALUE),
    VALUE>GRIDSIZE,
    active(new_object).
