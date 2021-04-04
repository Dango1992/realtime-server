# from RpcHandler import RpcReplyError
from common.component.Component import Component
from core.common.RpcMethodArgs import Dict
from core.common.RpcSupport import rpc_method, CLIENT_ONLY, CLIENT_STUB
from core.util.UtilApi import wait_or_not


class CompPuppetTest(Component):

    VAR_NAME = 'CompPuppetTest'

    def __init__(self):
        super().__init__()
        self._cnt = 1000000

    def puppet_chat_to_channel(self, chat_info):
        print("call puppet_chat_to_channel")
        self.call_server_comp_method(
            self.VAR_NAME, 'puppet_chat_to_channel', {'i': "mmp"})

    def puppet_chat_to_ppt(self, chat_info):
        print("call puppet_chat_to_ppt")
        self.call_server_comp_method(
            self.VAR_NAME, 'puppet_chat_to_ppt', {'p': chat_info})

    def test_reload(self):
        print("call test_reload")
        self.call_server_comp_method(
            self.VAR_NAME, 'test_reload')

    def make_server_reload(self):
        print("call make server reload")
        self.call_server_comp_method(
            self.VAR_NAME, 'make_server_reload')

    # @rpc_method(CLIENT_STUB, (Dict('i'),))
    # @rpc_method(CLIENT_STUB, Dict('i'))
    @rpc_method(CLIENT_STUB, [Dict('i')])
    # @rpc_method(CLIENT_STUB, {Dict('i')})
    def puppet_chat_from_srv(self, chat_info):
        print(chat_info)
        self._cnt -= 1
        if self._cnt > 0:
            self.puppet_chat_to_ppt({'content': 'puppet_chat_to_ppt'})

    @wait_or_not
    async def test_response_rpc(self):

        print("callll test_response_rpc")
        self.remote_comp.make_server_reload()
        # try:
        # err = None
        # # gg = await self.remote_entity.CompPuppetTest.test_response_rpc(997)
        self.remote_entity.CompPuppetTest.test_response_rpc(
            997,
            # need_reply=True, reply_timeout=1
        )
        # # except RpcReplyError as e:
        # #     print("rpc reply errr")
        # #     print(e)
        # # self.remote_entity.CompPuppetTest.test_response_rpc(997)
        # print(f"gg={gg}, err={err}")
        err, hh = await self.remote_comp.test_response_rpc(
            886, need_reply=True, reply_timeout=10)
        print(f"hh={hh}, err={err}")

        # self.remote_comp.test_response_rpc(886)
        # print("testttt")
        # final_rpc_name = "CompPuppetTest.test_response_rpc"
        # args = [110]
        # need_reply = False
        # reply_timeout = 2
        # self.entity.call_remote_method(
        #     final_rpc_name, [*args], need_reply, reply_timeout)
