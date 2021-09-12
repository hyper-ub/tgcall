from ...scaffold import Scaffold


class MtProtoHandler(Scaffold):
    async def _init_mtproto(self):
        if not self._app.is_connected:
            await self._app.start()
        self._my_id = await self._app.get_id()
        self._cache_local_peer = await self._app.resolve_peer(
            self._my_id,
        )

    def _handle_mtproto(self):
        @self._app.on_kicked()
        async def kicked_handler(chat_id: int):
            self._call_holder.remove_call(
                chat_id,
            )
            await self._binding.send({
                'action': 'leave_call',
                'chat_id': chat_id,
                'type': 'kicked_from_group',
            })
            await self._on_event_update.propagate(
                'KICK_HANDLER',
                self,
                chat_id,
            )
            self._cache_user_peer.pop(chat_id)

        @self._app.on_closed_voice_chat()
        async def closed_voice_chat_handler(chat_id: int):
            self._cache_user_peer.pop(chat_id)
            await self._binding.send({
                'action': 'leave_call',
                'chat_id': chat_id,
                'type': 'closed_voice_chat',
            })
            await self._on_event_update.propagate(
                'CLOSED_HANDLER',
                self,
                chat_id,
            )

        @self._app.on_receive_invite()
        async def receive_invite_handler(action):
            await self._on_event_update.propagate(
                'INVITE_HANDLER',
                self,
                action,
            )

        @self._app.on_left_group()
        async def left_handler(chat_id: int):
            await self._on_event_update.propagate(
                'LEFT_HANDLER',
                self,
                chat_id,
            )