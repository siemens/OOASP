% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

% TODO: still missing is the length_mm attribute
%
#program domain(new_object, cls).

ooasp_potential_cv(nrofseats_eq_attribute_nrseats).
ooasp_potential_cv(standingroom_iff_handrail).

% Paggensers number is calculated
ooasp_cv(nrpassengers_neq_nrseats_plus_standingroom,new_object,"Number of passenges not adding up",(new_object,)):-
    ooasp_isa(wagon,new_object),
    &fsum{ooasp_attr_fvalue(nr_seats,new_object);
          ooasp_attr_fvalue(standing_room,new_object)}!=
        ooasp_attr_fvalue(nr_passengers,new_object).

%  Only one wagon allowed
ooasp_cv(only_one_wagon,new_object,"Only one wagon allowed, found also wagon {}",(W2,)):-
    ooasp_isa(wagon,new_object),
    ooasp_isa(wagon,W2),
    new_object>W2.

% Handrail required if standing_room>0
ooasp_cv(standingroom_iff_handrail,W,"Handrail required if standing room is larger than 0",(new_object,)):-
    active(new_object),
    ooasp_isa(wagon,W),
    #count{ID2:ooasp_assoc_gen(wagon_handrail,OPT,W,ID2)}=0,
    &fsum{ooasp_attr_fvalue(standing_room,W)}>0.


% the number of associated seats must be equal to the attribute nr_seats
ooasp_cv(nrofseats_eq_attribute_nrseats,W,"Number of seats should be {} ",(S,new_object)):-
    active(new_object),
    ooasp_isa(wagon,W),
    #count{ID2:ooasp_assoc_gen(wagon_seats,OPT,W,ID2)}=S,
    &fsum{ooasp_attr_fvalue(nr_seats,W)}!=S.

% all equal type except special
ooasp_cv(type_equal,W,"All seat types must be equal",(new_object,)):-
    active(new_object),
    ooasp_associated(wagon_seats,W,S1),
    ooasp_associated(wagon_seats,W,S2),
    S1!=S2,
    ooasp_attr_value(seat_type,S1,TYPE1),
    TYPE1!=special,
    ooasp_attr_value(seat_type,S2,TYPE2),
    TYPE2!=special,
    TYPE1!=TYPE2.

ooasp_cv(type_equal,new_object,"All seat and handrail types must be equal",(new_object,)):-
    active(new_object),
    ooasp_associated(wagon_seats,W,S),
    ooasp_associated(wagon_handrail,W,H),
    S!=H,
    ooasp_attr_value(seat_type,S,TYPE1),
    TYPE1!=special,
    ooasp_attr_value(handrail_type,H,TYPE2),
    TYPE2!=special,
    TYPE1!=TYPE2.

% all equal color except special
ooasp_cv(color_equal,W,"All colors must be equal",(new_object,)):-
    active(new_object),
    ooasp_associated(wagon_seats,W,S1),
    ooasp_associated(wagon_seats,W,S2),
    S1!=S2,
    ooasp_attr_value(seat_type,S1,TYPE1),
    ooasp_attr_value(seat_color,S1,COLOR1),
    TYPE1!=special,
    ooasp_attr_value(seat_type,S2,TYPE2),
    ooasp_attr_value(seat_color,S2,COLOR2),
    TYPE2!=special,
    COLOR1!=COLOR2.

ooasp_cv(sepecial_red,new_object,"Sepecial seats should be red",(new_object,)):-
    ooasp_attr_value(seat_type,new_object,special),
    ooasp_attr_value(seat_color,new_object,COLOR),
    COLOR!=red.
