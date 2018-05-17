import discord
import typing

INTRO_MESSAGE = \
    """Welcome to the #include<C++> discord server!
As part of an effort to combat bad players we require that you tell us a little about yourself.

Please send me a quick message with your introduction."""
APPROVAL_MESSAGE = \
    """$NewMember[{0}]
We have a new member: {0}!
Their introduction is as follows:
{1}

Please react to this message with a thumbs up / thumbs down to approve / ban the user."""

AUTHED_ROLE = "authorised"
APPROVALS_CHANNEL = "approvals"


class BotClient(discord.Client):
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def on_member_join(self, member: discord.Member):
        await self.start_private_message(member)
        await self.send_message(member, content=INTRO_MESSAGE)

    def get_member_and_server(self, user: discord.User) -> typing.Tuple[typing.Union[discord.Member, None], typing.Union[discord.Server, None]]:
        for s in self.servers:
            m = discord.utils.get(s.members, id=user.id)
            if m is not None:
                return m, s
        return None, None

    def check_member_has_role(self, member: discord.Member, role: str) -> bool:
        r = discord.utils.get(member.roles, name=role)
        return r is not None

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        if isinstance(message.channel, discord.PrivateChannel):
            user = message.author
            member, server = self.get_member_and_server(user)
            if member is not None:
                if self.check_member_has_role(member, AUTHED_ROLE):
                    return
                chan = discord.utils.get(server.channels, name=APPROVALS_CHANNEL)
                await self.send_message(chan, content=APPROVAL_MESSAGE.format(member.name, message.content))

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        msg = reaction.message
        if not msg.content.startswith("$NewMember"):
            return
        if msg.author != self.user:
            return 
        chan = msg.channel
        if chan.name != APPROVALS_CHANNEL:
            return
        if reaction.custom_emoji:
            return
        if not isinstance(reaction.emoji, str):
            return
        if reaction.emoji == "👍\U0001F44D👍":
            print("Approve")
        if reaction.emoji == "👍\U0001F44E👍":
            print("Reject")


TOKEN = "NDQ2NDAwNzQwNzIyODY4MjMw.Dd4f8g.zMtqCG6oJUE7_6mSwWZXHghp0Sw"
bot = BotClient()


if __name__ == '__main__':
    bot.run(TOKEN)
