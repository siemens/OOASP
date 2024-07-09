% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT


#program domain(new_object, cls).

% Used when getting inferences to minimize on lowerbound errors
:~ ooasp_cv(lowerbound,ID,_,(ASSOC,CMIN,N,C,OPT,new_object)). [CMIN-N@3,(ASSOC,ID)]

% % Penalize the bigger associations

% :~ ooasp_isa_leaf(C1,ID3), % Instanciates ID3
%       ooasp_isa_leaf(C2,ID1),
%       not user(ooasp_associated(A, ID3, ID1)),
%       not ooasp_assoc_specialization(A, _), % Only count the super
%       ooasp_associated(A, ID3, ID1). [ID1@2,(A,ID3)]


% :~ ooasp_isa_leaf(C1,ID3), % Instanciates ID3
%       ooasp_isa_leaf(C2,ID1),
%       not user(ooasp_associated(A, ID1, ID3)),
%       not ooasp_assoc_specialization(A, _), % Only count the super
%       ooasp_associated(A, ID1, ID3). [ID1@1,(A,ID3)]
