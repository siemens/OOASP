from ooasp.kb import OOASPKnowledgeBase
from ooasp.interactive import InteractiveConfigurator
from ooasp import settings


def new_iconf(example="racks"):
    if example == "racks":
        kb = OOASPKnowledgeBase.from_file("racks_v1", settings.racks_example_kb)
        return InteractiveConfigurator(kb, "i1", [settings.racks_example_constraints])
    elif example == "metro":
        kb = OOASPKnowledgeBase.from_file("metro_v1", settings.metro_example_kb)
        return InteractiveConfigurator(kb, "i1", [settings.metro_example_constraints])
    elif example == "metrof":
        kb = OOASPKnowledgeBase.from_file("metro_v1", settings.metrof_example_kb)
        return InteractiveConfigurator(kb, "i1", [settings.metrof_example_constraints])
    elif example == "metro_small":
        kb = OOASPKnowledgeBase.from_file("metro_v1", settings.metro_small_example_kb)
        return InteractiveConfigurator(kb, "i1", [settings.metro_small_example_constraints])
    elif example == "metrof_small":
        kb = OOASPKnowledgeBase.from_file("metro_v1", settings.metrof_small_example_kb)
        return InteractiveConfigurator(kb, "i1", [settings.metrof_small_example_constraints])
    else:
        raise Exception(f"Invalid example name for configuration: {example}")
