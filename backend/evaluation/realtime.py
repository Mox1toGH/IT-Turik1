from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .consumers import leaderboard_group_name


def emit_tournament_leaderboard_updated(
    *,
    tournament_id: int,
    round_id: int,
    reason: str,
    submission_id: int | None = None,
    evaluation_id: int | None = None,
) -> None:
    channel_layer = get_channel_layer()
    if not channel_layer:
        return

    payload = {
        "tournament_id": tournament_id,
        "round_id": round_id,
        "reason": reason,
    }
    if submission_id is not None:
        payload["submission_id"] = submission_id
    if evaluation_id is not None:
        payload["evaluation_id"] = evaluation_id

    async_to_sync(channel_layer.group_send)(
        leaderboard_group_name(tournament_id),
        {
            "type": "leaderboard_event",
            "event": "leaderboard.updated",
            "payload": payload,
        },
    )

