from client.PuppetBindEntity import PuppetBindEntity
from common.component.Component import components
from common.component.ComponentSupport import ComponentSupport
from client.component.puppet.CompPuppetTest import CompPuppetTest
from client.BattleEntity import BattleEntity


@components(
    CompPuppetTest
)
class Puppet(BattleEntity, ComponentSupport):

    def __init__(self):
        # super(BattleEntity).__init__()
        # super(ComponentSupport).__init__()

        BattleEntity.__init__(self)
        ComponentSupport.__init__(self)
        self.bind_entity = None  # type: PuppetBindEntity

    def init_from_dict(self, bdict):
        ComponentSupport.init_from_dict(self, bdict)

    def set_bind_entity(self, be: PuppetBindEntity):
        self.bind_entity = be
        self.bind_entity.set_bind_ok()
