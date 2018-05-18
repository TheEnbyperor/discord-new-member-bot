import discord
import discord.raw_models
import re
import typing

INTRO_MESSAGE = \
    """Welcome to the {0.name} discord server!
As part of an effort to combat bad players we require that you tell us a little about yourself.

Please send me a quick message with your introduction."""
APPROVAL_MESSAGE = \
    """$NewMember[{0.id}]
We have a new member: <@{0.id}>!
Their introduction is as follows:
{1}

Please react to this message with a thumbs up / thumbs down to approve / ban the user."""

APPROVED_CHAN_MESSAGE = """<@{0.id}> has been approved by <@{1.id}>"""
APPROVED_DM_MESSAGE = """<@{0.id}> has approved you into {1.name}"""
REJECTED_CHAN_MESSAGE = """<@{0.id}> has been rejected by <@{1.id}>"""
REJECTED_DM_MESSAGE = """<@{0.id}> has deemed that you should not be in {1.name}"""

AUTHED_ROLE = "authorised"
APPROVALS_CHANNEL = "approvals"


class BotClient(discord.Client):
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def on_member_join(self, member: discord.Member):
        server = member.guild
        await member.send(content=INTRO_MESSAGE.format(server))

    def get_member_and_server(self, user_id) -> typing.Tuple[typing.Union[discord.Member, None], typing.Union[discord.Guild, None]]:
        for s in self.guilds:
            m = discord.utils.get(s.members, id=user_id)
            if m is not None:
                if self.check_member_has_role(m, AUTHED_ROLE):
                    continue
                return m, s
        return None, None

    def check_member_has_role(self, member: discord.Member, role: str) -> bool:
        r = discord.utils.get(member.roles, name=role)
        return r is not None

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        if isinstance(message.channel, discord.DMChannel):
            user = message.author
            member, server = self.get_member_and_server(user.id)
            if member is not None:
                chan = discord.utils.get(server.channels, name=APPROVALS_CHANNEL)
                await chan.send(content=APPROVAL_MESSAGE.format(member, message.content))

    async def on_raw_reaction_add(self, evt: discord.raw_models.RawReactionActionEvent):
        chan = self.get_channel(evt.channel_id)
        msg = await chan.get_message(evt.message_id)
        if not msg.content.startswith("$NewMember"):
            return
        if msg.author != self.user:
            return
        if chan.name != APPROVALS_CHANNEL:
            return
        emoji = self._connection._upgrade_partial_emoji(evt.emoji)
        if not isinstance(emoji, str):
            return

        member_id_match = re.match("^\$NewMember\[(.+)\]", msg.content)
        if member_id_match is None:
            return
        member_id = member_id_match.group(1)
        member, server = self.get_member_and_server(int(member_id))
        if member is None:
            return

        user = server.get_member(evt.user_id)

        if emoji == "\U0001F44D":
            await self.approve_member(member, server, user)
        if emoji == "\U0001F44E":
            await self.reject_member(member, server, user)

    async def approve_member(self, member: discord.Member, server: discord.Guild, user: discord.Member):
        chan = discord.utils.get(server.channels, name=APPROVALS_CHANNEL)
        await chan.send(content=APPROVED_CHAN_MESSAGE.format(member, user))
        await member.send(content=APPROVED_DM_MESSAGE.format(user, server))
        role = discord.utils.get(server.roles, name=AUTHED_ROLE)
        await member.add_roles(role, reason="{0.name} approved user".format(user))

    async def reject_member(self, member: discord.Member, server: discord.Guild, user: discord.Member):
        chan = discord.utils.get(server.channels, name=APPROVALS_CHANNEL)
        await chan.send(content=REJECTED_CHAN_MESSAGE.format(member, user))
        await member.send(content=REJECTED_DM_MESSAGE.format(user, server))
        await server.ban(member, reason="{0.name} rejected user".format(user), delete_message_days=7)


bot = BotClient()

if __name__ == '__main__':
    with open("token") as f:
        token = f.readlines()[0].strip()

    bot.run(token)
