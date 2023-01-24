% Copyright (c) 2022 Siemens AG Oesterreich
% SPDX-License-Identifier: MIT

% EXAMPLE metro
ooasp_kb(metro_v1).

% classes
ooasp_class(metro_v1,object).

ooasp_class(metro_v1,wagon).
ooasp_subclass(metro_v1,wagon,object).

ooasp_class(metro_v1,handrail).
ooasp_subclass(metro_v1,handrail,object).

ooasp_class(metro_v1,seat).
ooasp_subclass(metro_v1,seat,object).

% associations
% -1 means * i.e. unrestricted

ooasp_assoc(metro_v1,wagon_handrail,wagon,1,1,handrail,0,1).
ooasp_assoc(metro_v1,wagon_seats,wagon,1,1,seat,0,80).

ooasp_attribute(metro_v1,wagon,nr_passengers,int).
ooasp_attribute_minInclusive(metro_v1,wagon,nr_passengers,50).
ooasp_attribute_maxInclusive(metro_v1,wagon,nr_passengers,200).

ooasp_attribute(metro_v1,wagon,nr_seats,int).
ooasp_attribute_minInclusive(metro_v1,wagon,nr_seats,0).
ooasp_attribute_maxInclusive(metro_v1,wagon,nr_seats,200).

ooasp_attribute(metro_v1,wagon,standing_room,int).
ooasp_attribute_minInclusive(metro_v1,wagon,standing_room,0).
ooasp_attribute_maxInclusive(metro_v1,wagon,standing_room,200).

ooasp_attribute(metro_v1,seat,seat_type,str).
ooasp_attribute_enum(metro_v1,seat,seat_type,standard).
ooasp_attribute_enum(metro_v1,seat,seat_type,premium).
ooasp_attribute_enum(metro_v1,seat,seat_type,special).

ooasp_attribute(metro_v1,seat,seat_color,str).
ooasp_attribute_enum(metro_v1,seat,seat_color,blue).
ooasp_attribute_enum(metro_v1,seat,seat_color,red).
ooasp_attribute_enum(metro_v1,seat,seat_color,white).

ooasp_attribute(metro_v1,handrail,handrail_type,str).
ooasp_attribute_enum(metro_v1,handrail,handrail_type,standard).
ooasp_attribute_enum(metro_v1,handrail,handrail_type,premium).
