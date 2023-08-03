from ooasp.kb import OOASPKnowledgeBase
from ooasp.interactive import InteractiveConfigurator
from ooasp import settings

def new_racks_iconf():
    racks_kb = OOASPKnowledgeBase.from_file("racks_v1",settings.racks_example_kb)
    return InteractiveConfigurator(racks_kb,"i1",[settings.racks_example_constraints])