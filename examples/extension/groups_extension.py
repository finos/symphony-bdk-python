import asyncio
import logging.config
from pathlib import Path

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.ext.group import SymphonyGroupBdkExtension, SymphonyGroupService
from symphony.bdk.gen.group_model.base_profile import BaseProfile
from symphony.bdk.gen.group_model.create_group import CreateGroup
from symphony.bdk.gen.group_model.member import Member
from symphony.bdk.gen.group_model.owner import Owner
from symphony.bdk.gen.group_model.status import Status
from symphony.bdk.gen.group_model.update_group import UpdateGroup

logging.config.fileConfig(Path(__file__).parent.parent / "logging.conf", disable_existing_loggers=False)


async def run():
    async with SymphonyBdk(BdkConfigLoader.load_from_symphony_dir("config.yaml")) as bdk:
        bdk.extensions().register(SymphonyGroupBdkExtension)
        group_service: SymphonyGroupService = bdk.extensions().service(SymphonyGroupBdkExtension)

        # list groups
        groups = await group_service.list_groups(status=Status("ACTIVE"))
        logging.debug(f"List groups: {groups}")

        # list groups with cursor based pagination
        groups_generator = await group_service.list_all_groups(status=Status("ACTIVE"), chunk_size=2, max_number=4)
        groups = [group async for group in groups_generator]
        logging.debug(f"List groups: {groups}")

        # create a new group
        profile = BaseProfile(display_name="Mary's SDL")
        member = Member(member_tenant=190, member_id=13056700580915)
        create_group = CreateGroup(type="SDL", owner_type=Owner(value="TENANT"), owner_id=190, name="Another SDL",
                                   members=[member], profile=profile)
        group = await group_service.insert_group(create_group=create_group)
        logging.debug(f"Group created: {group}")

        # update group name
        update_group = UpdateGroup(name="Updated name", type=group.type, owner_type=Owner(value="TENANT"),
                                   owner_id=group.owner_id, id=group.id, e_tag=group.e_tag,
                                   status=Status(value="ACTIVE"), profile=profile, members=[member])
        group = await group_service.update_group(if_match=group.e_tag, group_id=group.id, update_group=update_group)
        logging.debug(f"Group after name update: {group}")

        # add member to a group
        group = await group_service.add_member_to_group(group.id, 13056700580913)
        logging.debug(f"Group after a new member is added: {group}")

        # update group avatar
        image_base_64 = "base_64_format_image"
        group = await group_service.update_avatar(group_id=group.id, image=image_base_64)
        logging.debug(f"Group after avatar update: {group}")

        # get a group by id
        group = await group_service.get_group(group_id=group.id)
        logging.debug(f"Retrieve group by id: {group}")

        # Delete group
        update_group = UpdateGroup(name=group.name, type=group.type, owner_type=Owner(value="TENANT"),
                                   owner_id=group.owner_id, id=group.id, e_tag=group.e_tag,
                                   status=Status(value="DELETED"), profile=profile, members=[member])
        group = await group_service.update_group(if_match=group.e_tag, group_id=group.id, update_group=update_group)
        logging.debug(f"Group removed: {group}")


asyncio.run(run())
