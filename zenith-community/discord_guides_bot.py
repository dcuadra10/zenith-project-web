import sys

# Reconfigure standard output to UTF-8 to prevent Windows UnicodeEncodeError on emojis
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

import discord
import json
import os
import aiohttp
from discord.ext import commands
from dotenv import load_dotenv

# Load configuration from .env file
load_dotenv()

# --- CONFIGURATION ---
# Path to save the guides JSON file inside the website assets folder
JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "guides.json")

# Read settings from environment variables
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "YOUR_DISCORD_BOT_TOKEN_HERE")
raw_forum_ids = os.getenv("DISCORD_FORUM_IDS", "")

# Parse comma-separated Forum Channel IDs
FORUM_CHANNEL_IDS = []
for id_str in raw_forum_ids.split(","):
    id_str = id_str.strip()
    if id_str and id_str.isdigit():
        FORUM_CHANNEL_IDS.append(int(id_str))
# ---------------------

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def download_image(url, dest_path):
    """Downloads an image from a URL and saves it to dest_path."""
    if os.path.exists(dest_path):
        return True
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    with open(dest_path, "wb") as f:
                        f.write(await resp.read())
                    return True
    except Exception as e:
        print(f"Error downloading image {url}: {e}")
    return False

async def sync_all_forums():
    """Fetches all threads from the specified forums and saves them to guides.json."""
    if not FORUM_CHANNEL_IDS:
        print("WARNING: No valid Forum Channel IDs specified in DISCORD_FORUM_IDS in the .env file.")
        return
        
    guides = []
    
    for channel_id in FORUM_CHANNEL_IDS:
        channel = bot.get_channel(channel_id)
        if not channel:
            try:
                channel = await bot.fetch_channel(channel_id)
            except Exception as e:
                print(f"Error fetching channel {channel_id}: {e}")
                continue
                
        if not isinstance(channel, discord.ForumChannel):
            print(f"Channel {channel_id} is not a Forum Channel.")
            continue
            
        print(f"Syncing guides from forum: {channel.name}...")
        
        # Get active threads
        threads = list(channel.threads)
        
        # Get archived threads (to make sure old guides are also synchronized)
        try:
            async for thread in channel.archived_threads(limit=100):
                threads.append(thread)
        except Exception as e:
            print(f"Error fetching archived threads for {channel.name}: {e}")

        for thread in threads:
            try:
                # The starter message of a forum thread has the same ID as the thread itself
                try:
                    first_message = await thread.fetch_message(thread.id)
                except Exception as e:
                    first_message = None
                    async for message in thread.history(oldest_first=True, limit=1):
                        first_message = message
                    
                if first_message:
                    # Parse category name (either parent forum name or thread tags if preferred)
                    category = channel.name
                    # Fallback to standard categories if channel names are custom
                    category_map = {
                        "kvk-strategy": "KvK Strategy",
                        "commanders": "Commander Builds",
                        "mge-rules": "MGE & Kingdom Laws",
                        "alliance-ops": "Alliance Operations",
                        "economy": "Growth & Economy",
                        "boot-camp": "Boot Camp (F2P/New)"
                    }
                    category_clean = category_map.get(channel.name.lower(), channel.name)

                    # Download and cache images locally to prevent expiring Discord CDN links
                    images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "guides_images")
                    os.makedirs(images_dir, exist_ok=True)
                    guide_images = []
                    attachment_markdown_images = []

                    # 1. Download message attachments
                    for att in first_message.attachments:
                        if att.content_type and att.content_type.startswith("image/"):
                            # Skip the default Zenith Community logo attachment to prevent giant duplicate logos inside guides
                            if "IMG_7561" in att.filename:
                                continue
                            
                            safe_filename = f"{att.id}_{att.filename}"
                            dest_path = os.path.join(images_dir, safe_filename)
                            relative_path = f"assets/guides_images/{safe_filename}"
                            try:
                                if not os.path.exists(dest_path):
                                    await att.save(dest_path)
                                    print(f"Downloaded attachment image: {safe_filename}")
                                guide_images.append(relative_path)
                                attachment_markdown_images.append(f"![image]({relative_path})")
                            except Exception as e:
                                print(f"Error saving attachment {safe_filename}: {e}")

                    # Extract content from message content and embeds
                    content_parts = []
                    if first_message.content:
                        content_parts.append(first_message.content)
                    
                    if attachment_markdown_images:
                        content_parts.append("\n".join(attachment_markdown_images))
                    
                    for embed_idx, embed in enumerate(first_message.embeds):
                        embed_parts = []
                        if embed.title:
                            embed_parts.append(f"## {embed.title}")
                        if embed.description:
                            embed_parts.append(embed.description)
                        
                        # Download and insert embed image inline
                        if embed.image and embed.image.url:
                            url = embed.image.url
                            clean_name = f"embed_{thread.id}_{embed_idx}_img.png"
                            dest_path = os.path.join(images_dir, clean_name)
                            relative_path = f"assets/guides_images/{clean_name}"
                            if await download_image(url, dest_path):
                                guide_images.append(relative_path)
                                embed_parts.append(f"![image]({relative_path})")

                        # Download and insert embed thumbnail inline
                        if embed.thumbnail and embed.thumbnail.url:
                            url = embed.thumbnail.url
                            clean_name = f"embed_{thread.id}_{embed_idx}_thumb.png"
                            dest_path = os.path.join(images_dir, clean_name)
                            relative_path = f"assets/guides_images/{clean_name}"
                            if await download_image(url, dest_path):
                                guide_images.append(relative_path)
                                embed_parts.append(f"![image]({relative_path})")

                        for field in embed.fields:
                            if field.name and field.value:
                                embed_parts.append(f"### {field.name}\n{field.value}")
                        if embed_parts:
                            content_parts.append("\n\n".join(embed_parts))
                            
                    full_content = "\n\n".join(content_parts)

                    # Download and cache author avatar
                    author_avatar_url = first_message.author.display_avatar.url if first_message.author.display_avatar else None
                    author_avatar_path = None
                    if author_avatar_url:
                        avatar_filename = f"avatar_{first_message.author.id}.png"
                        avatar_dest_path = os.path.join(images_dir, avatar_filename)
                        avatar_relative_path = f"assets/guides_images/{avatar_filename}"
                        if await download_image(author_avatar_url, avatar_dest_path):
                            author_avatar_path = avatar_relative_path

                    guides.append({
                        "id": str(thread.id),
                        "title": thread.name,
                        "category": category_clean,
                        "author": first_message.author.display_name,
                        "author_avatar": author_avatar_path,
                        "date": thread.created_at.strftime("%Y-%m-%d") if thread.created_at else "2026-06-10",
                        "content": full_content,
                        "images": guide_images
                    })
            except Exception as e:
                print(f"Error reading thread {thread.name}: {e}")

    # Write output to JSON
    os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(guides, f, indent=2, ensure_ascii=False)
        
    print(f"Sync complete! Saved {len(guides)} guides to {JSON_PATH}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Running initial guides synchronization...")
    await sync_all_forums()

# Sync in real-time when a thread is created or updated
@bot.event
async def on_thread_create(thread):
    if thread.parent_id in FORUM_CHANNEL_IDS:
        print(f"New guide thread detected: {thread.name}. Syncing...")
        import asyncio
        await asyncio.sleep(2)
        await sync_all_forums()

@bot.event
async def on_thread_update(before, after):
    if after.parent_id in FORUM_CHANNEL_IDS:
        if before.name != after.name or before.archived != after.archived:
            print(f"Guide thread updated: {after.name}. Syncing...")
            await sync_all_forums()

# Sync in real-time when the first message is edited
@bot.event
async def on_message_edit(before, after):
    if isinstance(after.channel, discord.Thread) and after.channel.parent_id in FORUM_CHANNEL_IDS:
        async for message in after.channel.history(oldest_first=True, limit=1):
            if message.id == after.id:
                print(f"Guide content edited in thread {after.channel.name}. Syncing...")
                await sync_all_forums()
                break

# Admin command to manual force sync
@bot.command(name="sync")
@commands.has_permissions(administrator=True)
async def manual_sync(ctx):
    await ctx.send("🔄 Synchronizing guides between Discord forums and website...")
    try:
        await sync_all_forums()
        await ctx.send("✅ Synchronization complete! Website guides updated successfully.")
    except Exception as e:
        await ctx.send(f"❌ Error during synchronization: {e}")

# Run Bot
if __name__ == "__main__":
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_DISCORD_BOT_TOKEN_HERE":
        print("ERROR: Please replace 'YOUR_DISCORD_BOT_TOKEN_HERE' with your actual Bot Token in the .env file.")
    elif not FORUM_CHANNEL_IDS:
        print("ERROR: Please provide at least one valid Forum Channel ID in the .env file.")
    else:
        bot.run(BOT_TOKEN)
