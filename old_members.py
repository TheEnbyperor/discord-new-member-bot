import discord
import datetime


class BotClient(discord.Client):
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

        server = discord.utils.get(self.servers, name="#include")
        me = discord.utils.get(server.members, id=self.user.id)
        seen_users = []
        for channel in server.channels:
            if not channel.type == discord.ChannelType.text:
                continue
            if not me.permissions_in(channel).read_message_history:
                continue
            last_message_time = datetime.datetime.utcnow()
            last_message = None
            while last_message_time + datetime.timedelta(days=10) > datetime.datetime.utcnow():
                async for message in self.logs_from(channel, limit=10, before=last_message):
                    if message.timestamp < last_message_time:
                        last_message_time = message.timestamp
                        last_message = message
                    if isinstance(message.author, discord.Member):
                        user = message.author
                        if user.joined_at <= datetime.datetime.utcnow() - datetime.timedelta(days=30):
                            if user.id not in seen_users:
                                seen_users.append(user.id)
                                print(f"{user.id},{user.name},{user.nick},{user.top_role}")

        await self.close()


bot = BotClient()

if __name__ == '__main__':
    with open("token") as f:
        token = f.readlines()[0].strip()
        print(token)

    bot.run(token, bot=False)
