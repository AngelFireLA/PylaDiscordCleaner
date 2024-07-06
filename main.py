import discord
from discord.ext import commands
from discord.ui import View, Button
from datetime import datetime, timedelta, timezone

intents = discord.Intents.all()
GUILD_ID = 1205263029269438574
STAFF_ROLE_IDS = [1245105922146308106, 1219692597333725265, 1211358165451673650, 1229413711916040303]  # Add your staff role IDs here
bot = commands.Bot(command_prefix='/', intents=intents)


@bot.command(name='ticket-clean')
async def ticket_clean(ctx):
    message = await ctx.send("What do you want to do?")
    await message.add_reaction("🗑️")
    await message.add_reaction("🔔")


@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    if not reaction.message.guild:
        return

    member = reaction.message.guild.get_member(user.id)
    if not member.guild_permissions.administrator and not any(role.id in STAFF_ROLE_IDS for role in member.roles):
        return

    message = reaction.message
    if reaction.emoji == "🗑️":
        await delete_closed_and_empty_tickets(message.channel)
    elif reaction.emoji == "🔔":
        await ping_inactive_tickets(message.channel)


async def delete_closed_and_empty_tickets(channel):
    print("Starting to clean")
    guild = bot.get_guild(GUILD_ID)
    for ch in guild.channels:
        if isinstance(ch, discord.TextChannel):  # Check if channel is a text channel
            if ch.name.startswith("closed"):
                await ch.delete()
            elif ch.name.startswith("ticket"):
                empty = True
                async for message in ch.history(limit=10):
                    if message.author.id != bot.user.id:
                        empty = False
                        break
                if empty:
                    print("deleted open ticket", ch.name)
                    await ch.delete()


async def ping_inactive_tickets(channel):
    guild = bot.get_guild(GUILD_ID)
    for ch in guild.channels:
        if ch.name.startswith("ticket") and ch.name != "open-ticket":
            last_message = None
            async for message in ch.history(limit=1):
                last_message = message
                break

            if last_message and (datetime.now(timezone.utc) - last_message.created_at) > timedelta(days=14) and not last_message.author.bot:
                for member in ch.members:
                    if member.bot:
                        continue
                    if not any(role.id in STAFF_ROLE_IDS for role in member.roles):
                        print(ch.name)
                        await ch.send(
                            f"{member.mention} This is an automatic cleaning action. If your issue has been solved, please close the ticket, otherwise please ping one of the staff (we have a lot of tickets and might forget some).")


TOKEN = 'your_token'
bot.run(TOKEN)
