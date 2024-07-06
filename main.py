
import discord, asyncio

bot = discord.Bot(intents=discord.Intents.all())

# Sync channel permissions with event subscribers
async def sync(channel, subscriberIds):
    currentIds = []

    # list out who has current access to channel
    for user in channel.members:
        if not user.bot:
            currentIds.append(user.id)

    # remove any users
    for userId in currentIds:
        if userId not in subscriberIds:
            member = await bot.fetch_user(userId)
            try:
                if channel.permissions_for(member).administrator:
                    continue
            except:
                pass
            await channel.set_permissions(member, send_messages=False, read_messages=False, add_reactions=False, 
                                        embed_links=False, attach_files=False, read_message_history=False, external_emojis=False)
            print("Removed " + str(member) + " from event channel")

    # add users to channel
    for userId in subscriberIds:
        if userId not in currentIds:
            member = await bot.fetch_user(userId) 
            await channel.set_permissions(member, send_messages=True, read_messages=True, add_reactions=True, 
                                          embed_links=True, attach_files=True, read_message_history=True, external_emojis=True)
            print("Added " + str(member) + " to event channel")

@bot.event
async def on_ready():
    #await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the Internet"))
    print('=> Logged in as {0.user}'.format(bot))

    for guild in bot.guilds:
        for event in guild.scheduled_events:
            name = event.name

            eventSubscribers = []
            async for user in event.subscribers():
                eventSubscribers.append(user.id)

            channelName = name.replace(" ","_").lower() + str(event.id)[:3]

            # create event channel if it doesn't exist
            channel = discord.utils.get(guild.channels, name=channelName)
            if channel == None:
                print(f"Creating event channel for {name}")

                # create text channel
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                }
                channel = await guild.create_text_channel(channelName, overwrites=overwrites)
                print(f"Creating event channel {channelName}")
                await sync(channel, eventSubscribers)

            else:
                await sync(channel, eventSubscribers)

bot.run("")
