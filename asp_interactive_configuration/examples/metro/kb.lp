% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

% EXAMPLE metro
% classes
ooasp_class(object).

ooasp_class(wagon).
ooasp_subclass(wagon,object).

ooasp_class(handrail).
ooasp_subclass(handrail,object).

ooasp_class(seat).
ooasp_subclass(seat,object).

% associations
% -1 means * i.e. unrestricted

ooasp_assoc(wagon_handrail,wagon,1,1,handrail,0,1).
ooasp_assoc(wagon_seats,wagon,1,1,seat,0,80).

ooasp_attribute(wagon,nr_passengers,int).
ooasp_attribute_minInclusive(wagon,nr_passengers,50).
ooasp_attribute_maxInclusive(wagon,nr_passengers,200).

ooasp_attribute(wagon,nr_seats,int).
ooasp_attribute_minInclusive(wagon,nr_seats,0).
ooasp_attribute_maxInclusive(wagon,nr_seats,200).

ooasp_attribute(wagon,standing_room,int).
ooasp_attribute_minInclusive(wagon,standing_room,0).
ooasp_attribute_maxInclusive(wagon,standing_room,200).

ooasp_attribute(seat,seat_type,str).
ooasp_attribute_enum(seat,seat_type,standard).
ooasp_attribute_enum(seat,seat_type,premium).
ooasp_attribute_enum(seat,seat_type,special).

ooasp_attribute(seat,seat_color,str).
ooasp_attribute_enum(seat,seat_color,blue).
ooasp_attribute_enum(seat,seat_color,red).
ooasp_attribute_enum(seat,seat_color,white).

ooasp_attribute(handrail,handrail_type,str).
ooasp_attribute_enum(handrail,handrail_type,standard).
ooasp_attribute_enum(handrail,handrail_type,premium).