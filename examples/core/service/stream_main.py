import asyncio

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.gen.agent_model.share_article import ShareArticle
from symphony.bdk.gen.agent_model.share_content import ShareContent
from symphony.bdk.gen.pod_model.room_tag import RoomTag
from symphony.bdk.gen.pod_model.stream_filter import StreamFilter
from symphony.bdk.gen.pod_model.stream_type import StreamType
from symphony.bdk.gen.pod_model.user_id import UserId
from symphony.bdk.gen.pod_model.v2_admin_stream_filter import V2AdminStreamFilter
from symphony.bdk.gen.pod_model.v2_room_search_criteria import V2RoomSearchCriteria
from symphony.bdk.gen.pod_model.v3_room_attributes import V3RoomAttributes


class MessageMain:

    @staticmethod
    async def run():
        stream_id = "ubaSiuUsc_j-_lVQ8vhAz3___opSJdJZdA"

        config = BdkConfigLoader.load_from_symphony_dir("config.yaml")

        async with SymphonyBdk(config) as bdk:
            streams = bdk.streams()

            stream = await streams.get_stream(stream_id)
            list_streams = await streams.list_streams(StreamFilter(stream_types=[StreamType(type="ROOM")],
                                                                   include_inactive_streams=False))

            await streams.add_member_to_room(13056700579859, stream_id)
            await streams.remove_member_from_room(13056700579859, stream_id)

            article = ShareArticle(title="Article Title", sub_title="Subtitle", message="Hence my shared article",
                                   publisher="Capital Markets Laboratories", author="Gottlieb",
                                   thumbnail_url="http://www.cmlviz.com/cmld3b/images/tesla-supercharger-stop.jpg",
                                   article_url="https://ophirgottlieb.tumblr.com/post/146623530819/the-secrets-out-tesla-enters-china-and-is",
                                   summary="Tesla Motors Inc. (NASDAQ:TSLA) has a CEO more famous than the firm itself, perhaps. Elon Musk has made some bold predictions, first stating that the firm would grow sales from 50,000 units in 2015 to 500,000 by 2020 powered by the less expensive Model 3 and the massive manufacturing capability of the Gigafactory.",
                                   app_id="unknown")

            message = await streams.share(stream_id,
                                          ShareContent(type="com.symphony.sharing.article", content=article))

            await streams.promote_user_to_room_owner(13056700579891, stream_id)
            await streams.demote_owner_to_room_participant(13056700579891, stream_id)

            stream = await streams.create_im_or_mim([13056700579872, 13056700579891, 13056700579850])
            room = await streams.create_room(V3RoomAttributes(name="New fancy room", description="test room"))

            results = await streams.search_rooms(V2RoomSearchCriteria(query="bot", member=UserId(id=13056700579891)))
            room_info = await streams.get_room_info(stream_id)

            room = await streams.set_room_active(stream_id, True)
            room = await streams.update_room(
                stream_id,
                V3RoomAttributes(name="New room name", description="new description",
                                 keywords=[RoomTag("fancyLabel", "fancyValue")]))

            room = await streams.create_im_admin([13056700579860, 13056700579872])
            room = await streams.set_room_active_admin(stream_id, True)

            streams = await streams.list_streams_admin(V2AdminStreamFilter())

            members = await streams.list_stream_members(stream_id)
            members = await streams.list_room_members(stream_id)


if __name__ == "__main__":
    asyncio.run(MessageMain.run())
