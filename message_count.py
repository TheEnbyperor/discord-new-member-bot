import discord


class BotClient(discord.Client):
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

        server = discord.utils.get(self.guilds, name="#include")
        me = discord.utils.get(server.members, id=self.user.id)
        data = {}
        for channel in server.channels:
            if not isinstance(channel, discord.TextChannel):
                continue
            if not me.permissions_in(channel).read_message_history:
                continue
            async for message in channel.history():
                if data.get(message.author.name) is None:
                    data[message.author] = {"msg_count": 1}
                else:
                    data[message.author]["msg_count"] += 1

        for user in data.keys():
            if isinstance(user, discord.Member):
                print(user.top_role)
        await self.close()


bot = BotClient()

if __name__ == '__main__':
    with open("q_token") as f:
        token = f.readlines()[0].strip()
        print(token)

    bot.run(token, bot=False)
