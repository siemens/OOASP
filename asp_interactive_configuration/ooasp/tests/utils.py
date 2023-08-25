from ooasp.kb import OOASPKnowledgeBase
from ooasp.interactive import InteractiveConfigurator
from ooasp import settings

def new_racks_iconf():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    return InteractiveConfigurator(racks_kb,"i1",[settings.racks_example_constraints])

def new_metro_iconf():
    metro_kb = OOASPKnowledgeBase.from_file("metro_v1",settings.metro_example_kb)
    return InteractiveConfigurator(metro_kb,"i1",[settings.metro_example_constraints])