% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

% TODO: still missing is the length_mm attribute
%
#program domain(new_object).

ooasp_cv_ignore_for_brave(nrofseats_eq_attribute_nrseats).
ooasp_cv_ignore_for_brave(standingroom_iff_handrail).

% deactivated because of performance
%ooasp_cv_ignore_for_brave(nrpassengers_neq_nrseats_plus_standingroom).

% currently only one wagon allowed

ooasp_cv(C,only_one_wagon,W1,"Only one wagon allowed {} {}",(new_object,W2)):-
    active(new_object),
    ooasp_isa(C,wagon,W1),
    ooasp_isa(C,wagon,W2),
    W1!=W2.

% standingroom > 0 -> count(handrail)>0
ooasp_cv(C,standingroom_iff_handrail,W,"Standing room > 0 iff there is a handrail v1 {} {} {} {}",(new_object,W,STANDINGROOM,COUNT)):-
    active(new_object),
    ooasp_arity(C,wagon_handrail,1,W,COUNT,new_object),
    ooasp_attribute_value(C,standing_room,W,STANDINGROOM),
    COUNT=0,
    STANDINGROOM>0.

ooasp_cv(C,standingroom_iff_handrail,W,"Standing room > 0 iff there is a handrail {} {} {} {}",(new_object,W,STANDINGROOM,COUNT)):-
    active(new_object),
    ooasp_arity(C,wagon_handrail,1,W,COUNT,new_object),
    ooasp_attribute_value(C,standing_room,W,STANDINGROOM),
    COUNT>0,
    STANDINGROOM=0.


% the number of associated seats must be equal to the attribute nr_seats
ooasp_cv(C,nrofseats_eq_attribute_nrseats,W,"nr of seats = attribute nr_seats {} {} {} {}",(new_object,W,NRSEATS,COUNT)):-
    active(new_object),
    ooasp_arity(C,wagon_seats,1,W,COUNT,new_object),
    ooasp_attribute_value(C,nr_seats,W,NRSEATS),
    COUNT!=NRSEATS.

% all equal type except special
ooasp_cv(CONFIG,type_mustbe_equal_except_special,W,"type_mustbe_equal_except_special {} {} {} {}",(new_object,W,S1,S2)):-
    active(new_object),
    ooasp_associated(CONFIG,wagon_seats,W,S1),
    ooasp_associated(CONFIG,wagon_seats,W,S2),
    S1!=S2,
    ooasp_attribute_value(CONFIG,seat_type,S1,TYPE1),
    TYPE1!=special,
    ooasp_attribute_value(CONFIG,seat_type,S2,TYPE2),
    TYPE2!=special,
    TYPE1!=TYPE2.

ooasp_cv(CONFIG,type_mustbe_equal_except_special,new_object,"type_mustbe_equal_except_special {} {} {} {}",(new_object,W,S,H)):-
    active(new_object),
    ooasp_associated(CONFIG,wagon_seats,W,S),
    ooasp_associated(CONFIG,wagon_handrail,W,H),
    S!=H,
    ooasp_attribute_value(CONFIG,seat_type,S,TYPE1),
    TYPE1!=special,
    ooasp_attribute_value(CONFIG,handrail_type,H,TYPE2),
    TYPE2!=special,
    TYPE1!=TYPE2.

% all equal color except special
ooasp_cv(CONFIG,color_mustbe_equal_except_special,W,"color_mustbe_equal_except_special {} {} {} {}",(new_object,W,S1,S2)):-
    active(new_object),
    ooasp_associated(CONFIG,wagon_seats,W,S1),
    ooasp_associated(CONFIG,wagon_seats,W,S2),
    S1!=S2,
    ooasp_attribute_value(CONFIG,seat_type,S1,TYPE1),
    ooasp_attribute_value(CONFIG,seat_color,S1,COLOR1),
    TYPE1!=special,
    ooasp_attribute_value(CONFIG,seat_type,S2,TYPE2),
    ooasp_attribute_value(CONFIG,seat_color,S2,COLOR2),
    TYPE2!=special,
    COLOR1!=COLOR2.

ooasp_cv(CONFIG,new_object,special_seats_color_mustbe_red,"special_seats_color_mustbe_red {}",(new_object,S)):-
    active(new_object),
    ooasp_attribute_value(CONFIG,seat_type,S,TYPE),
    TYPE=special,
    ooasp_attribute_value(CONFIG,seat_color,S,COLOR),
    COLOR!=red.

%*
deactivated because of performance
ooasp_cv(C,nrpassengers_neq_nrseats_plus_standingroom,W,"{} nr_passengers {} = nr_seats {} = standingroom {}",(new_object,W,NRPASSENGERS,NRSEATS,STANDINGROOM)):-
    active(new_object),
    ooasp_attribute_value(C,nr_seats,W,NRSEATS),
    ooasp_attribute_value(C,standing_room,W,STANDINGROOM),
    ooasp_attribute_value(C,nr_passengers,W,NRPASSENGERS),
    NRPASSENGERS != NRSEATS + STANDINGROOM.
*%

%
%* all equal type except special
ooasp_cv(CONFIG,seat_type_mustbe_equal_except_special,"seat types must be equal {} {} {}",(new_object,S1,S2)):-
    active(new_object),
    ooasp_associated(CONFIG,wagon_seats,W,S1),
    ooasp_associated(CONFIG,wagon_seats,W,S2),
    S1!=S2,
    ooasp_attribute_value(CONFIG,seat_type,S1,TYPE1),
    TYPE1!=special,
    ooasp_attribute_value(CONFIG,seat_type,S1,TYPE2),
    TYPE2!=special,
    TYPE1!=TYPE2.

%
ooasp_cv(CONFIG,type_mustbe_equal_except_special(W,S,H)):-
    ooasp_associated(CONFIG,wagon_seats,W,S),
    ooasp_associated(CONFIG,wagon_handrail,W,H),
    S!=H,
    ooasp_attribute_value(CONFIG,seat_type,S,TYPE1),
    TYPE1!=special,
    ooasp_attribute_value(CONFIG,handrail_type,H,TYPE2),
    TYPE2!=special,
    TYPE1!=TYPE2.

% all equal color except special
ooasp_cv(CONFIG,color_mustbe_equal_except_special(W,S1,S2)):-
    ooasp_associated(CONFIG,wagon_seats,W,S1),
    ooasp_associated(CONFIG,wagon_seats,W,S2),
    S1!=S2,
    ooasp_attribute_value(CONFIG,seat_type,S1,TYPE1),
    ooasp_attribute_value(CONFIG,seat_color,S1,COLOR1),
    TYPE1!=special,
    ooasp_attribute_value(CONFIG,seat_type,S2,TYPE2),
    ooasp_attribute_value(CONFIG,seat_color,S2,COLOR2),
    TYPE2!=special,
    COLOR1!=COLOR2.

ooasp_cv(CONFIG,special_seats_color_mustbe_red(S)):-
    ooasp_associated(CONFIG,wagon_seats,W,S),
    ooasp_attribute_value(CONFIG,seat_type,S,TYPE),
    TYPE=special,
    ooasp_attribute_value(CONFIG,seat_color,S,COLOR),
    COLOR!=red.

% experimental - derive values
ooas_cv(CONFIG,nrpassengers_neq_nrseats_plus_standingroom(W)):-
    ooasp_attribute_value(CONFIG,nr_seats,W,NRSEATS),
    ooasp_attribute_value(CONFIG,standing_room,W,STANDINGROOM),
    ooasp_attribute_value(CONFIG,nr_passengers,W,NRPASSENGERS),
    NRPASSENGERS != NRSEATS + STANDINGROOM,
    % only for checking
    not ooasp_configure(CONFIG).

%ooasp_attribute_value(C,nr_passengers,W,NRPASSENGERS):-
%    ooasp_attribute_value(C,nr_seats,W,NRSEATS),
%    ooasp_attribute_value(C,standing_room,W,STANDINGROOM),
%    NRPASSENGERS = NRSEATS + STANDINGROOM.

%ooasp_attribute_value(C,nr_seats,W,NRSEATS):-
%    ooasp_attribute_value(C,nr_passengers,W,NRPASSENGERS),
%    ooasp_attribute_value(C,standing_room,W,STANDINGROOM),
%    NRSEATS = NRPASSENGERS - STANDINGROOM.

ooasp_attribute_value(C,standing_room,W,STANDINGROOM):-
    ooasp_attribute_value(C,nr_passengers,W,NRPASSENGERS),
    ooasp_attribute_value(C,nr_seats,W,NRSEATS),
    STANDINGROOM = NRPASSENGERS - NRSEATS.

*%
