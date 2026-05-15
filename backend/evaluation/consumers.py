from channels.generic.websocket import AsyncJsonWebsocketConsumer


def leaderboard_group_name(tournament_id: int) -> str:
    return f"leaderboard.tournament.{tournament_id}"


class LeaderboardConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return

        self.subscribed_tournaments: set[int] = set()
        await self.accept()

    async def disconnect(self, code):
        for tournament_id in list(getattr(self, "subscribed_tournaments", set())):
            await self.channel_layer.group_discard(
                leaderboard_group_name(tournament_id),
                self.channel_name,
            )
        self.subscribed_tournaments = set()

    async def receive_json(self, content, **kwargs):
        action = content.get("action")
        tournament_id = content.get("tournament_id")
        if action not in {"subscribe", "unsubscribe"} or not isinstance(tournament_id, int):
            await self.send_json(
                {
                    "event": "leaderboard.error",
                    "payload": {"message": "Expected action and integer tournament_id."},
                }
            )
            return

        if action == "subscribe":
            if tournament_id not in self.subscribed_tournaments:
                await self.channel_layer.group_add(
                    leaderboard_group_name(tournament_id),
                    self.channel_name,
                )
                self.subscribed_tournaments.add(tournament_id)
            await self.send_json(
                {
                    "event": "leaderboard.subscribed",
                    "payload": {"tournament_id": tournament_id},
                }
            )
            return

        if tournament_id in self.subscribed_tournaments:
            await self.channel_layer.group_discard(
                leaderboard_group_name(tournament_id),
                self.channel_name,
            )
            self.subscribed_tournaments.remove(tournament_id)
        await self.send_json(
            {
                "event": "leaderboard.unsubscribed",
                "payload": {"tournament_id": tournament_id},
            }
        )

    async def leaderboard_event(self, event):
        await self.send_json(
            {
                "event": event["event"],
                "payload": event["payload"],
            }
        )

