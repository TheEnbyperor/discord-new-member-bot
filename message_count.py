import discord


class BotClient(discord.Client):
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

        server = discord.utils.get(self.guilds, name="#include Test")
        msg_count = {}
        for channel in server.channels:
            if not isinstance(channel, discord.TextChannel):
                continue
            async for message in channel.history():
                if msg_count.get(message.author.name) is None:
                    msg_count[message.author.name] = 1
                else:
                    msg_count[message.author.name] += 1

        print(msg_count)
        await self.close()


bot = BotClient()

if __name__ == '__main__':
    with open("token") as f:
        token = f.readlines()[0].strip()

    bot.run(token, bot=True)
