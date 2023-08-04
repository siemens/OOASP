% Copyright (c) 2023 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

% EXAMPLE puzzles
% object oriented modelling of various square-based number puzzles
ooasp_kb(puzzles_v1).

% classes
ooasp_class(puzzles_v1,object).

ooasp_class(puzzles_v1,numberPuzzle).
ooasp_subclass(puzzles_v1,numberPuzzle,object).

ooasp_class(puzzles_v1,unconstrainedSquare).
ooasp_subclass(puzzles_v1,unconstrainedSquare,numberPuzzle).

ooasp_class(puzzles_v1,latinSquareOrSudoku).
ooasp_subclass(puzzles_v1,latinSquareOrSudoku,numberPuzzle).

ooasp_class(puzzles_v1,latinSquare).
ooasp_subclass(puzzles_v1,latinSquare,latinSquareOrSudoku).

ooasp_class(puzzles_v1,sudoku).
ooasp_subclass(puzzles_v1,sudoku,latinSquareOrSudoku).

ooasp_class(puzzles_v1,cell).
ooasp_subclass(puzzles_v1,cell,object).

ooasp_class(puzzles_v1,row).
ooasp_subclass(puzzles_v1,row,object).

ooasp_class(puzzles_v1,column).
ooasp_subclass(puzzles_v1,column,object).

ooasp_class(puzzles_v1,block).
ooasp_subclass(puzzles_v1,block,object).

% associations
% -1 means * i.e. unrestricted
% TODO: -1 does not work in interactive mode apparently

% currently max 9x9
ooasp_assoc(puzzles_v1,puzzle_cells,numberPuzzle,1,1,cell,1,81).
ooasp_assoc(puzzles_v1,puzzle_rows,numberPuzzle,1,1,row,1,9).
ooasp_assoc(puzzles_v1,puzzle_columns,numberPuzzle,1,1,column,1,9).
ooasp_assoc(puzzles_v1,row_cells,row,1,1,cell,1,9).
ooasp_assoc(puzzles_v1,column_cells,column,1,1,cell,1,9).
% optional for sudoku
ooasp_assoc(puzzles_v1,block_cells,block,0,1,cell,1,9).

ooasp_attribute(puzzles_v1,numberPuzzle,grid_size,int).
ooasp_attribute_minInclusive(puzzles_v1,numberPuzzle,grid_size,1).
ooasp_attribute_maxInclusive(puzzles_v1,numberPuzzle,grid_size,9).

ooasp_attribute(puzzles_v1,row,row_nr,int).
ooasp_attribute_minInclusive(puzzles_v1,row,row_nr,1).
ooasp_attribute_maxInclusive(puzzles_v1,row,row_nr,9).

ooasp_attribute(puzzles_v1,column,column_nr,int).
ooasp_attribute_minInclusive(puzzles_v1,column,column_nr,1).
ooasp_attribute_maxInclusive(puzzles_v1,column,column_nr,9).

% TODO: increase allowed numbers
ooasp_attribute(puzzles_v1,cell,cell_value,int).
ooasp_attribute_minInclusive(puzzles_v1,cell,cell_value,1).
ooasp_attribute_maxInclusive(puzzles_v1,cell,cell_value,9).

