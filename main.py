import os
import discord
from discord.ext import commands

# Setup bot permissions
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix="?", intents=intents)

# Memory storage for active sticky messages
# Format: { channel_id: { "message": "text", "last_id": message_id } }
sticky_messages = {}

@bot.event
async def on_ready():
    print(f'🎉 Success! {bot.user.name} is now online and active.')

@bot.command()
@commands.has_permissions(manage_messages=True)
async def stick(ctx, *, content: str):
    """Command to set a sticky message in the current channel (?stick Hello World)"""
    channel_id = ctx.channel.id
    
    # Delete the command trigger message to keep it clean
    await ctx.message.delete()
    
    # Send the initial sticky message
    sticky_msg = await ctx.send(f"📌 **STICKY MESSAGE:**\n\n{content}")
    
    # Save the configuration
    sticky_messages[channel_id] = {
        "message": content,
        "last_id": sticky_msg.id
    }

@bot.command()
@commands.has_permissions(manage_messages=True)
async def unstick(ctx):
    """Command to remove the sticky message from the current channel (?unstick)"""
    channel_id = ctx.channel.id
    if channel_id in sticky_messages:
        # Delete old message if it exists
        try:
            old_msg = await ctx.channel.fetch_message(sticky_messages[channel_id]["last_id"])
            await old_msg.delete()
        except:
            pass
        
        del sticky_messages[channel_id]
        await ctx.send("❌ Sticky message removed from this channel.", delete_after=5)
    else:
        await ctx.send("There is no active sticky message in this channel.", delete_after=5)

@bot.event
async def on_message(message):
    # Ignore messages sent by the bot itself
    if message.author == bot.user:
        return

    channel_id = message.channel.id
    
    # Check if this channel has an active sticky message
    if channel_id in sticky_messages:
        sticky_data = sticky_messages[channel_id]
        
        # Delete the previous sticky message instance
        try:
            old_msg = await message.channel.fetch_message(sticky_data["last_id"])
            await old_msg.delete()
        except:
            pass # Skips if it was already deleted manually
            
        # Re-send the sticky message so it stays at the very bottom
        new_sticky = await message.channel.send(f"📌 **STICKY MESSAGE:**\n\n{sticky_data['message']}")
        sticky_messages[channel_id]["last_id"] = new_sticky.id

    # Allow other commands to continue functioning
    await bot.process_commands(message)

# Start up the bot using your hidden token
bot.run(os.environ['DISCORD_TOKEN'])
