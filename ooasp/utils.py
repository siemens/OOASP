# Copyright (c) 2024 Siemens AG Oesterreich
# SPDX-License-Identifier: MIT


import json

COLORS = {
    "GREY": "\033[90m",
    "BLUE": "\033[94m",
    "CYAN": "\033[96m",
    "PURPLE": "\033[95m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "RED": "\033[91m",
    "NORMAL": "\033[0m",
}


def title(s) -> str:
    return (
        "\n"
        + COLORS["BLUE"]
        + "=" * 10
        + " "
        + s
        + " "
        + "=" * 10
        + COLORS["NORMAL"]
        + "\n"
    )


def subtitle(s, color="CYAN") -> str:
    return "\n" + COLORS[color] + "-" * 10 + " " + s + " " + "-" * 10 + COLORS["NORMAL"]


def pretty_dict(d) -> str:
    s = json.dumps(d, indent=4)
    return s + "\n"


def red(s) -> str:
    return f"{COLORS['RED']}{s}{COLORS['NORMAL']}"


def colored(color) -> str:
    return f"{COLORS[color]}{s}{COLORS['NORMAL']}"


def green(s) -> str:
    return f"{COLORS['GREEN']}{s}{COLORS['NORMAL']}"


def opt(name: str, args) -> dict:
    """
    Creates an options dictionary entry
    """
    return {"fun_name": name, "args": args, "str": f"{name}{args}".replace(",)", ")")}


def editable_fact_as_select_action(fact, unifiers) -> dict:
    """
    Gets the editable fact (Objects, AttrValue and Associations) as
    a select option.
    """
    if (
        isinstance(fact, unifiers.Object)
        or isinstance(fact, unifiers.Leaf)
        or isinstance(fact, unifiers.ObjectSmallest)
    ):
        return opt("select_object_class", (fact.object_id, fact.class_name))
    elif isinstance(fact, unifiers.AttributeValue):
        return opt("select_value", (fact.object_id, fact.attr_name, fact.attr_value))
    elif isinstance(fact, unifiers.Association):
        return opt(
            "select_association", (fact.assoc_name, fact.object_id1, fact.object_id2)
        )
    else:
        raise RuntimeError(f"Fact {fact} is not an editiable fact")


def editable_fact_as_remove_action(fact, unifiers) -> dict:
    """
    Gets the editable facts (Objects, AttrValue and Associations) as
    a remove option.
    """
    if (
        isinstance(fact, unifiers.Object)
        or isinstance(fact, unifiers.Leaf)
        or isinstance(fact, unifiers.ObjectSmallest)
    ):
        return opt("remove_object_class", (fact.object_id,))
    elif isinstance(fact, unifiers.AttributeValue):
        return opt("remove_value", (fact.object_id, fact.attr_name))
    elif isinstance(fact, unifiers.Association):
        return opt(
            "remove_association", (fact.assoc_name, fact.object_id1, fact.object_id2)
        )
    else:
        raise RuntimeError(f"Fact {fact} is not an editiable fact")
