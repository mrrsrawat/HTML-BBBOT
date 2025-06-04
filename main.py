
import os
import requests
import random
import asyncio
import subprocess
from vars import OWNER_ID, auth_users
import time
import sys
import motor
from mongo.usersdb import get_users, add_user, get_user
import app
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from mongo.ban_db import is_banned, ban_user_db, unban_user_db, get_ban_list
from mongo.plans_db import premium_users
from pyrogram import Client, filters
from pyrogram.types import Message
from concurrent.futures import ThreadPoolExecutor
THREADPOOL = ThreadPoolExecutor(max_workers=1000)

thumb = os.path.join(os.path.dirname(__file__), "logo.jpg")

# Replace with your API ID, API Hash, and Bot Token
API_ID = "27900743"
API_HASH = "ebb06ea8d41420e60b29140dcee902fc"
BOT_TOKEN = "8109523189:AAEMAxVO7YXl3CVnFeTrQDEocQUO0T2Xn6E"



# Telegram channel where files will be forwarded
CHANNEL_USERNAME = "KRSTXTLOGHUBBBBBBBBB"  # Replace with your channel username

# Initialize Pyrogram Client
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Function to extract names and URLs from the text file
def extract_names_and_urls(file_content):
    lines = file_content.strip().split("\n")
    data = []
    for line in lines:
        if ":" in line:
            name, url = line.split(":", 1)
            data.append((name.strip(), url.strip()))
    return data

# Function to categorize URLs
def categorize_urls(urls):
    videos = []
    pdfs = []
    others = []

    for name, url in urls:
        new_url = url
        if "media-cdn.classplusapp.com/drm" in url or "cpvod.testbook" in url or "media-cdn.classplusapp.com" in url:
            new_url = f"https://api.extractor.workers.dev/player?url={url}"
            videos.append((name, new_url))
            
        elif "media-cdn.classplusapp.com/alisg-cdn-a.classplusapp.com/" in url or "media-cdn.classplusapp.com/1681/" in url or "media-cdn.classplusapp.com/tencent/" in url:
            vid_id = url.split("/")[-2]
            new_url = f"https://api.extractor.workers.dev/player?url={url}"
            videos.append((name, new_url))

        elif "akamaized.net/" in url or "1942403233.rsc.cdn77.org/" in url:
            vid_id = url.split("/")[-2]
            new_url = f"https://www.khanglobalstudies.com/player?src={url}"
            videos.append((name, new_url))


        elif "/master.mpd" in url:
            vid_id = url.split("/")[-2]
            new_url = f"https://player.muftukmall.site/?id={vid_id}"
            videos.append((name, new_url))

        elif ".zip" in url:
            vid_id = url.split("/")[-2]
            new_url = f"https://video.pablocoder.eu.org/appx-zip?url={url}"
            videos.append((name, new_url))

        elif "d1d34p8vz63oiq.cloudfront.net/" in url:
            vid_id = url.split("/")[-2]
            new_url = f"https://anonymouspwplayer-b99f57957198.herokuapp.com/pw?url={video_url}?token={your_working_token}"
            videos.append((name, new_url))

        elif "youtube.com/embed" in url:
            yt_id = url.split("/")[-1]
            new_url = f"https://www.youtube.com/watch?v={yt_id}"
            
        elif ".m3u8" in url:
            videos.append((name, url))
        elif ".mp4" in url:
            videos.append((name, url))
        elif "pdf" in url:
            pdfs.append((name, url))
        else:
            others.append((name, url))

    return videos, pdfs, others

# Function to generate HTML file with Video.js player
def generate_html(file_name, videos, pdfs, others):
    file_name_without_extension = os.path.splitext(file_name)[0]

    video_links = "".join(f'<a href="#" onclick="playVideo(\'{url}\')">{name}</a>' for name, url in videos)
    pdf_links = "".join(f'<a href="{url}" target="_blank">{name}</a>' for name, url in pdfs)
    other_links = "".join(f'<a href="{url}" target="_blank">{name}</a>' for name, url in others)

    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{file_name_without_extension}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
    <link href="https://vjs.zencdn.net/8.10.0/video-js.css" rel="stylesheet" />
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Arial', sans-serif;
        }}

        body {{
            background: #94a0b3;
            color: #333;
            line-height: 1.6;
        }}

        .header {{
            background: #030000;
            color: red;
            padding: 20px;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}

        .subheading {{
            font-size: 16px;
            margin-top: 10px;
            color: #faf5f5;
            font-weight: normal;
        }}

        .subheading a {{
            color: #fafafc;
            text-decoration: none;
            font-weight: bold;
        }}

        #video-player {{
            margin: 20px auto;
            width: 90%;
            max-width: 800px;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            background: #1c1c1c;
            padding: 10px;
        }}

        #url-input-container {{
            display: none;
            margin: 20px auto;
            width: 90%;
            max-width: 600px;
            text-align: center;
        }}

        #url-input-container input {{
            width: 70%;
            padding: 10px;
            border: 2px solid #0a0000;
            border-radius: 5px;
            font-size: 16px;
            margin-right: 10px;
        }}

        #url-input-container button {{
            width: 25%;
            padding: 10px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            background: #050000;
            color: white;
            cursor: pointer;
            transition: background 0.3s ease;
        }}

        #url-input-container button:hover {{
            background: #ff0000;
        }}

        .search-bar {{
            margin: 20px auto;
            width: 90%;
            max-width: 600px;
            text-align: center;
        }}

        .search-bar input {{
            width: 100%;
            padding: 10px;
            border: 2px solid #080000;
            border-radius: 5px;
            font-size: 16px;
        }}

        .no-results {{
            color: red;
            font-weight: bold;
            margin-top: 20px;
            text-align: center;
            display: none;
        }}

        .container {{
            display: flex;
            justify-content: space-around;
            margin: 20px auto;
            width: 90%;
            max-width: 800px;
        }}

        .tab {{
            flex: 1;
            padding: 15px;
            background: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            cursor: pointer;
            transition: all 0.3s ease;
            border-radius: 10px;
            font-size: 18px;
            font-weight: bold;
            text-align: center;
            margin: 0 5px;
        }}

        .tab:hover {{
            background: #ff0000;
            color: white;
            transform: translateY(-5px);
        }}

        .content {{
            display: none;
            margin: 20px auto;
            width: 90%;
            max-width: 800px;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}

        .content h2 {{
            font-size: 22px;
            margin-bottom: 15px;
            color: #ff0000;
        }}

        .video-list, .pdf-list, .other-list {{
            text-align: left;
        }}

        .video-list a, .pdf-list a, .other-list a {{
            display: block;
            padding: 20px;
            background: #050505;
            margin: 5px 0;
            border-radius: 5px;
            text-decoration: none;
            color: #ff0011;
            font-weight: bold;
            transition: all 0.3s ease;
        }}

        .video-list a:hover, .pdf-list a:hover, .other-list a:hover {{
            background: #ff0011;
            color: white;
            transform: translateX(10px);
        }}

        .footer {{
            margin-top: 30px;
            font-size: 16px;
            font-weight: bold;
            padding: 15px;
            background: #1c1c1c;
            color: white;
            text-align: center;
            border-radius: 10px;
        }}

        .footer a {{
            color: #f50202;
            text-decoration: none;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="header">
        {file_name_without_extension}
        <div class="subheading">📥 Extracted By: <a href="https://t.me/="_blank">🚩 𝐉𝐀𝐈 𝐁𝐀𝐉𝐑𝐀𝐍𝐆 𝐁𝐀𝐋𝐈 🚩</a></div>
    </div>

    <div id="video-player">
        <video id="jai-bajrangbali-player" class="video-js vjs-default-skin" controls preload="auto" width="640" height="360">
            <p class="vjs-no-js">
                To view this video please enable JavaScript, and consider upgrading to a web browser that
                <a href="https://videojs.com/html5-video-support/" target="_blank">supports HTML5 video</a>
            </p>
        </video>
    </div>

    <div id="url-input-container">
        <input type="text" id="url-input" placeholder="Enter video URL to play...">
        <button onclick="playCustomUrl()">Play</button>
    </div>

    <button onclick="toggleUrlInput()" style="margin: 20px auto; padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; display: block; width: 90%; max-width: 600px;">Enter Custom URL</button>

    <div class="search-bar">
        <input type="text" id="searchInput" placeholder="Search for videos, PDFs, or other resources..." oninput="filterContent()">
    </div>

    <div id="noResults" class="no-results">No results found.</div>

    <div class="container">
        <div class="tab" onclick="showContent('videos')">Videos</div>
        <div class="tab" onclick="showContent('pdfs')">PDFs</div>
        <div class="tab" onclick="showContent('others')">Others</div>
    </div>

    <div id="videos" class="content">
        <h2>All Video Lectures</h2>
        <div class="video-list">
            {video_links}
        </div>
    </div>

    <div id="pdfs" class="content">
        <h2>All PDFs</h2>
        <div class="pdf-list">
            {pdf_links}
        </div>
    </div>

    <div id="others" class="content">
        <h2>Other Resources</h2>
        <div class="other-list">
            {other_links}
        </div>
    </div>

    <div class="footer">Extracted By - <a href="https://t.me/" target="_blank">🚩 𝐉𝐀𝐈 𝐁𝐀𝐉𝐑𝐀𝐍𝐆 𝐁𝐀𝐋𝐈 🚩</a></div>

    <script src="https://vjs.zencdn.net/8.10.0/video.min.js"></script>
    <script>
        const player = videojs('jai-bajrangbali-player', {{
            controls: true,
            autoplay: false,
            preload: 'auto',
            fluid: true,
            controlBar: {{
                children: [
                    'playToggle',
                    'volumePanel',
                    'currentTimeDisplay',
                    'timeDivider',
                    'durationDisplay',
                    'progressControl',
                    'liveDisplay',
                    'remainingTimeDisplay',
                    'customControlSpacer',
                    'playbackRateMenuButton',
                    'chaptersButton',
                    'descriptionsButton',
                    'subsCapsButton',
                    'audioTrackButton',
                    'fullscreenToggle'
                ]
            }}
        }});

        function playVideo(url) {{
            if (url.includes('.m3u8')) {{
                document.getElementById('video-player').style.display = 'block';
                player.src({{ src: url, type: 'application/x-mpegURL' }});
                player.play().catch(() => {{
                    window.open(url, '_blank');
                }});
            }} else {{
                window.open(url, '_blank');
            }}
        }}

        function toggleUrlInput() {{
            const urlInputContainer = document.getElementById('url-input-container');
            urlInputContainer.style.display = urlInputContainer.style.display === 'none' ? 'block' : 'none';
        }}

        function playCustomUrl() {{
            const url = document.getElementById('url-input').value;
            if (url) {{
                playVideo(url);
            }}
        }}

        function showContent(tabName) {{
            const contents = document.querySelectorAll('.content');
            contents.forEach(content => {{
                content.style.display = 'none';
            }});
            const selectedContent = document.getElementById(tabName);
            if (selectedContent) {{
                selectedContent.style.display = 'block';
            }}
            filterContent();
        }}

        function filterContent() {{
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const categories = ['videos', 'pdfs', 'others'];
            let hasResults = false;

            categories.forEach(category => {{
                const items = document.querySelectorAll(`#${{category}} .${{category}}-list a`);
                let categoryHasResults = false;

                items.forEach(item => {{
                    const itemText = item.textContent.toLowerCase();
                    if (itemText.includes(searchTerm)) {{
                        item.style.display = 'block';
                        categoryHasResults = true;
                        hasResults = true;
                    }} else {{
                        item.style.display = 'none';
                    }}
                }});

                const categoryHeading = document.querySelector(`#${{category}} h2`);
                if (categoryHeading) {{
                    categoryHeading.style.display = categoryHasResults ? 'block' : 'none';
                }}
            }});

            const noResultsMessage = document.getElementById('noResults');
            if (noResultsMessage) {{
                noResultsMessage.style.display = hasResults ? 'none' : 'block';
            }}
        }}

        document.addEventListener('DOMContentLoaded', () => {{
            showContent('videos');
        }});
    </script>
</body>
</html>
    """
    return html_template

# Function to download video using FFmpeg
def download_video(url, output_path):
    command = f"ffmpeg -i {url} -c copy {output_path}"
    subprocess.run(command, shell=True, check=True)

@app.on_message(filters.command("ban"))
async def ban_user(client, message):
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("🚫 ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")

    if len(message.command) != 2:
        return await message.reply_text("❌ ᴜsᴀɢᴇ: /ban user_id", quote=True)

    try:
        user_id = int(message.command[1])
        user = await client.get_users(user_id)
        name = user.first_name or "No Name"
    except Exception:
        name = "No Name"
    except ValueError:
        return await message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ.")

    if user_id == OWNER_ID:
        return await message.reply_text("❌ ʏᴏᴜ ᴄᴀɴɴᴏᴛ ʙᴀɴ ʏᴏᴜʀsᴇʟғ.")

    if await is_banned(user_id):
        return await message.reply_text("⚠️ ᴜsᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ʙᴀɴɴᴇᴅ.")

    await ban_user_db(user_id, name)
    await message.reply_text(f"✅ ᴜsᴇʀ {user_id} ʜᴀs ʙᴇᴇɴ ʙᴀɴɴᴇᴅ.")
        

@app.on_message(filters.command("unban"))
async def unban_user(client, message):
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("🚫 ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")

    if len(message.command) != 2:
        return await message.reply_text("❌ ᴜsᴀɢᴇ: /unban user_id", quote=True)

    try:
        user_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ.")

    if not await is_banned(user_id):
        return await message.reply_text("⚠️ ᴜsᴇʀ ɪs ɴᴏᴛ ɪɴ ʙᴀɴ ʟɪsᴛ.")

    await unban_user_db(user_id)
    await message.reply_text(f"✅ ᴜsᴇʀ {user_id} ʜᴀs ʙᴇᴇɴ ᴜɴʙᴀɴɴᴇᴅ.")


@app.on_message(filters.command("banlist"))
async def banlist(client, message):
    if message.from_user.id != OWNER_ID:
        return

    text = await get_ban_list(client)
    await message.reply_text(
        text,
        disable_web_page_preview=True,
        quote=False
    )

image_list = [
"https://i.ibb.co/XxDwyHJV/file-1258.jpg",
"https://i.ibb.co/XxDwyHJV/file-1258.jpg",
"https://i.ibb.co/XxDwyHJV/file-1258.jpg",
"https://i.ibb.co/XxDwyHJV/file-1258.jpg",
"https://i.ibb.co/XxDwyHJV/file-1258.jpg",
]
print(4321)

@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    # Check if user is banned
    user_id = message.from_user.id
    if await is_banned(user_id):
        await message.reply_text("🚫 ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ꜰʀᴏᴍ ᴜsɪɴɢ ᴛʜɪs ʙᴏᴛ.\nᴄᴏɴᴛᴀᴄᴛ @krs_study_helper_bbot")
        return
    random_image_url = random.choice(image_list)

    keyboard = [
      [
        InlineKeyboardButton("🔘 ᴛxᴛ ᴛᴏ ʜᴛᴍʟ ᴄᴏɴᴠᴇʀᴛ 🔘", callback_data="jaibajrangbali")
      ],
      [
        InlineKeyboardButton(text="📞 Contact", url="http://t.me/krs_study_helper_bbot"),
        InlineKeyboardButton(text="🔍 Channel", url="http://t.me/krs_study_helper_bbot"),
      ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await message.reply_photo(
      photo=random_image_url,
      caption="**👋 𝘏𝘦𝘺! 𝘐'𝘮 HTML 𝘌𝘹𝘵𝘳𝘢𝘤𝘵𝘰𝘳 𝘉𝘰𝘵! \n\n📚 𝘐𝘧 𝘠𝘰𝘶 𝘙𝘶𝘯 𝘐𝘯𝘵𝘰 𝘈𝘯𝘺 𝘐𝘴𝘴𝘶𝘦 𝘖𝘳 𝘏𝘢𝘷𝘦 𝘛𝘳𝘰𝘶𝘣𝘭𝘦 𝘌𝘹𝘵𝘳𝘢𝘤𝘵𝘪𝘯𝘨 𝘈 HTML 𝘍𝘪𝘭𝘦, 𝘍𝘦𝘦𝘭 𝘍𝘳𝘦𝘦 𝘛𝘰 𝘙𝘦𝘢𝘤𝘩 𝘖𝘶𝘵 𝘛𝘰 𝘈𝘥𝘮𝘪𝘯.\n📙 𝘏𝘢𝘷𝘦 𝘈𝘯 𝘈𝘱𝘱 𝘠𝘰𝘶'𝘥 𝘓𝘪𝘬𝘦 𝘛𝘰 𝘈𝘥𝘥? 𝘋𝘰𝘯'𝘵 𝘏𝘦𝘴𝘪𝘵𝘢𝘵𝘦 𝘛𝘰 𝘊𝘰𝘯𝘵𝘢𝘤𝘵 𝘔𝘦 𝘈𝘯𝘺𝘵𝘪𝘮𝘦!\n\n📖 𝘚𝘦𝘭𝘦𝘤𝘵 𝘈𝘯 𝘖𝘱𝘵𝘪𝘰𝘯 𝘉𝘦𝘭𝘰𝘸 𝘛𝘰 𝘎𝘦𝘵 𝘚𝘵𝘢𝘳𝘵𝘦𝘥! [☑️ 𝘑𝘈𝘐 𝘉𝘈𝘑𝘙𝘈𝘕𝘎 𝘉𝘈𝘓𝘐 ☑️](http://t.me/krs_study_helper_bbot)",
      quote=True,
      reply_markup=reply_markup
    )

@app.on_callback_query(filters.regex("^jaibajrangbali$"))
async def jaibajrangbali_callback(app, callback_query):
    #user_id = callback_query.from_user.id
    #user = await premium_users()
    #SUDO_USERS = await premium_users()

    #if user_id not in user or user_id not in SUDO_USERS:
    #    await app.send_message(callback_query.message.chat.id, f"**🔒 ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ ᴛᴏ ᴛʜɪꜱ ʙᴏᴛ🔒\n━━━━━━━━━[ ρєя мσηтн ₹𝟗𝟗 ]━━━━━━━━━\n☑️ ᴘʟᴇᴀꜱᴇ ᴄᴏɴᴛᴀᴄᴛ - @krs_study_helper_bbot ☑️**")
   #     return
    user_id = callback_query.from_user.id
    await callback_query.answer()
    
    auth_user = auth_users[0]
    user = await app.get_users(auth_user)
    owner_username = "@" + user.username

    
    if user_id not in auth_users:
        await app.send_message(callback_query.message.chat.id, f"**🔒 ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ ᴛᴏ ᴛʜɪꜱ ʙᴏᴛ🔒\n━━━━━━━━━[ ρєя мσηтн ₹𝟏𝟗𝟗 ]━━━━━━━━━\n☑️ ᴘʟᴇᴀꜱᴇ ᴄᴏɴᴛᴀᴄᴛ - @krs_study_helper_bbot ☑️**")
        return
    THREADPOOL.submit(asyncio.run, process_jaibajrangbali(app, callback_query.message))

async def process_jaibajrangbali(app: Client, m: Message):

    editable = await m.reply_text("🔘 ʜᴇʏ! ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴍᴇ ᴀ ᴛxᴛ ꜰɪʟᴇ 🔘")


@app.on_callback_query()
async def handle_callback(_, query):
    user_id = query.from_user.id


    # Ban check
    if await is_banned(user_id):
        await query.answer("🚫 ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ꜰʀᴏᴍ ᴜsɪɴɢ ᴛʜɪs ʙᴏᴛ.", show_alert=True)
        return
        
    if query.data == "jaibajrangbali":
      await query.message.edit_text(reply_markup = InlineKeyboardMarkup(keyboard))
    
# Command handler for /start
#@app.on_message(filters.command("jaibajrangbali"))
async def start(client: Client, message: Message):
    await message.reply_text("🔘 ʜᴇʏ! ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴍᴇ ᴀ ᴛxᴛ ꜰɪʟᴇ 🔘")

# Message handler for file uploads
@app.on_message(filters.document)
async def handle_file(client: Client, message: Message):
   # user_id = message.from_user.id
    #user = await premium_users()
    #SUDO_USERS = await premium_users()

    #if user_id not in user or user_id not in SUDO_USERS:
     #   await app.send_message(callback_query.message.chat.id, f"**🔒 ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ ᴛᴏ ᴛʜɪꜱ ʙᴏᴛ🔒\n━━━━━━━━━[ ρєя мσηтн ₹𝟗𝟗 ]━━━━━━━━━\n☑️ ᴘʟᴇᴀꜱᴇ ᴄᴏɴᴛᴀᴄᴛ - @krs_study_helper_bbot ☑️**")
      #  return
    user_id = message.from_user.id
    #await callback_query.answer()
    
    auth_user = auth_users[0]
    user = await app.get_users(auth_user)
    owner_username = "@" + user.username

    
    if user_id not in auth_users:
        await  message.reply_text("**🔒 ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ ᴛᴏ ᴛʜɪꜱ ʙᴏᴛ🔒\n━━━━━━━━━[ ρєя мσηтн ₹𝟏𝟗𝟗 ]━━━━━━━━━\n☑️ ᴘʟᴇᴀꜱᴇ ᴄᴏɴᴛᴀᴄᴛ - @krs_study_helper_bbot ☑️**")
        return
     #Check if the file is a .txt file
    if not message.document.file_name.endswith(".txt"):
        await message.reply_text("Please upload a .txt file.")
        return

    # Download the file
    file_path = await message.download()
    file_name = message.document.file_name

    # Read the file content
    with open(file_path, "r") as f:
        file_content = f.read()

    # Extract names and URLs
    urls = extract_names_and_urls(file_content)

    # Categorize URLs
    videos, pdfs, others = categorize_urls(urls)

    # Generate HTML
    html_content = generate_html(file_name, videos, pdfs, others)
    html_file_path = file_path.replace(".txt", ".html")
    with open(html_file_path, "w") as f:
        f.write(html_content)

    # Send the HTML file to the user

    await message.reply_document(thumb=thumb, document=html_file_path, caption="\n\n☑️ 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲 𝐃𝐨𝐧𝐞!\n\n🔘 𝐄𝐱𝐭𝐫𝐚𝐜𝐭𝐞𝐝 𝐁𝐲 : 🚩 𝐉𝐀𝐈 𝐁𝐀𝐉𝐑𝐀𝐍𝐆 𝐁𝐀𝐋𝐈 🚩\n\n☑️ 𝐅𝐎𝐑 𝐀𝐍𝐘 𝐇𝐄𝐋𝐏 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐇𝐄𝐑𝐄 - [𝗝𝗔𝗜 𝗕𝗔𝗝𝗥𝗔𝗡𝗚 𝗕𝗔𝗟𝗜](http://t.me/krs_study_helper_bbot)")

    # Forward the .txt file to the channel
    await client.send_document(chat_id=CHANNEL_USERNAME, thumb=thumb, document=file_path)
    # Clean up files
    os.remove(file_path)
    os.remove(html_file_path)

# ---------------------------------------------------------------- #

async def send_msg(user_id, message):
    try:
        await message.copy(chat_id=user_id)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        return 400, f"{user_id} : deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id} : blocked the bot\n"
    except PeerIdInvalid:
        return 400, f"{user_id} : user id invalid\n"
    except Exception:
        return 500, f"{user_id} : {traceback.format_exc()}\n"
    

# ----------------------------Broadcast---------------------------- #
    
@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ ɪᴛ.")
        return    
    exmsg = await message.reply_text("sᴛᴀʀᴛᴇᴅ ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ!")
    all_users = (await get_users()) or {}
    done_users = 0
    failed_users = 0
    
    for user in all_users:
        try:
            await send_msg(user, message.reply_to_message)
            done_users += 1
            await asyncio.sleep(0.1)
        except Exception:
            pass
            failed_users += 1
    if failed_users == 0:
        await exmsg.edit_text(
            f"**sᴜᴄᴄᴇssғᴜʟʟʏ ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ✅**\n\n**sᴇɴᴛ ᴍᴇssᴀɢᴇ ᴛᴏ** `{done_users}` **ᴜsᴇʀs**",
        )
    else:
        await exmsg.edit_text(
            f"**sᴜᴄᴄᴇssғᴜʟʟʏ ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ✅**\n\n**sᴇɴᴛ ᴍᴇssᴀɢᴇ ᴛᴏ** `{done_users}` **ᴜsᴇʀs**\n\n**ɴᴏᴛᴇ:-** `ᴅᴜᴇ ᴛᴏ sᴏᴍᴇ ɪssᴜᴇ ᴄᴀɴ'ᴛ ᴀʙʟᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ` `{failed_users}` **ᴜsᴇʀs**",
        )


# ----------------------------Announce---------------------------- #
        
@app.on_message(filters.command("krsrawat") & filters.user(OWNER_ID))
async def announced(_, message):
    if message.reply_to_message:
      to_send=message.reply_to_message.id
    if not message.reply_to_message:
      return await message.reply_text("Reply To Some Post To Broadcast")
    users = await get_users() or []
    print(users)
    failed_user = 0
  
    for user in users:
      try:
        await _.forward_messages(chat_id=int(user), from_chat_id=message.chat.id, message_ids=to_send)
        await asyncio.sleep(1)
      except Exception as e:
        failed_user += 1
          
    if failed_users == 0:
        await exmsg.edit_text(
            f"**sᴜᴄᴄᴇssғᴜʟʟʏ ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ✅**\n\n**sᴇɴᴛ ᴍᴇssᴀɢᴇ ᴛᴏ** `{done_users}` **ᴜsᴇʀs**",
        )
    else:
        await exmsg.edit_text(
            f"**sᴜᴄᴄᴇssғᴜʟʟʏ ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ✅**\n\n**sᴇɴᴛ ᴍᴇssᴀɢᴇ ᴛᴏ** `{done_users}` **ᴜsᴇʀs**\n\n**ɴᴏᴛᴇ:-** `ᴅᴜᴇ ᴛᴏ sᴏᴍᴇ ɪssᴜᴇ ᴄᴀɴ'ᴛ ᴀʙʟᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ` `{failed_users}` **ᴜsᴇʀs**",
        )




start_time = time.time()

@app.on_message(group=10)
async def chat_watcher_func(_, message):
    try:
        if message.from_user:
            us_in_db = await get_user(message.from_user.id)
            if not us_in_db:
                await add_user(message.from_user.id)
    except:
        pass



def time_formatter():
    minutes, seconds = divmod(int(time.time() - start_time), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    tmp = (
        ((str(weeks) + "w:") if weeks else "")
        + ((str(days) + "d:") if days else "")
        + ((str(hours) + "h:") if hours else "")
        + ((str(minutes) + "m:") if minutes else "")
        + ((str(seconds) + "s") if seconds else "")
    )
    if tmp != "":
        if tmp.endswith(":"):
            return tmp[:-1]
        else:
            return tmp
    else:
        return "0 s"
        

@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats(client: Client, message: Message):
    start = time.time()
    users = len(await get_users())
    premium = await premium_users()
    ping = round((time.time() - start) * 1000)
    await message.reply_text(f"""
**Stats of** {(await client.get_me()).mention} :

🏓 **Ping Pong**: {ping}ms

📊 **Total Users** : `{users}`
📈 **Premium Users** : `{len(premium)}`
⚙️ **Bot Uptime** : `{time_formatter()}`
    
🎨 **Python Version**: `{sys.version.split()[0]}`
📑 **Mongo Version**: `{motor.version}`
""")







# Run the bot
if __name__ == "__main__":
    print("Bot is running...")
    app.run()
