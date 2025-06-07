import os
import html
import subprocess
from collections import defaultdict

from pyrogram import Client, filters
from pyrogram.types import Message
from vars import HTML_LOG_CHANNEL


def extract_names_and_urls(file_content):
    lines = file_content.strip().split("\n")
    data = []
    for line in lines:
        if ":" in line:
            name, url = line.split(":", 1)
            data.append((name.strip(), url.strip()))
    return data


def categorize_urls(urls):
    videos, pdfs, others = [], [], []

    for name, url in urls:
        url = url.strip()
        if "media-cdn.classplusapp.com/drm" in url or "cpvod.testbook" in url:
            new_url = f"https://api.extractor.workers.dev/player?url={url}"
            videos.append((name, new_url))

        elif any(x in url for x in ["alisg-cdn-a.classplusapp.com", "1681", "tencent"]):
            new_url = f"https://api.extractor.workers.dev/player?url={url}"
            videos.append((name, new_url))

        elif any(x in url for x in ["akamaized.net", "cdn77.org"]):
            new_url = f"https://www.khanglobalstudies.com/player?src={url}"
            videos.append((name, new_url))

        elif "/master.mpd" in url:
            video_id = url.split("/")[-2]
            new_url = f"https://player.muftukmall.site/?id={video_id}"
            videos.append((name, new_url))

        elif ".zip" in url:
            new_url = f"https://video.pablocoder.eu.org/appx-zip?url={url}"
            videos.append((name, new_url))

        elif "d1d34p8vz63oiq.cloudfront.net" in url:
            # Replace with a working token if needed
            token = "your_working_token"
            new_url = f"https://anonymouspwplayer-b99f57957198.herokuapp.com/pw?url={url}?token={token}"
            videos.append((name, new_url))

        elif "youtube.com/embed" in url:
            yt_id = url.split("/")[-1]
            new_url = f"https://www.youtube.com/watch?v={yt_id}"
            videos.append((name, new_url))

        elif any(x in url for x in [".pdf", "drive.google.com/file", "mediafire"]):
            pdfs.append((name, url))

        else:
            others.append((name, url))

    return videos, pdfs, others


def group_by_topic(file_list):
    grouped = defaultdict(list)
    for name, url in file_list:
        if ' - ' in name:
            topic, title = name.split(' - ', 1)
        else:
            topic = "Miscellaneous"
            title = name
        grouped[html.escape(topic.strip())].append((html.escape(title.strip()), url))
    return dict(grouped)


def generate_html(file_name, videos, pdfs, others):
    name = os.path.splitext(file_name)[0]
    videos_grouped = group_by_topic(videos)
    pdfs_grouped = group_by_topic(pdfs)

    def build_links(grouped, is_video=False):
        html_block = ""
        for topic, items in grouped.items():
            html_block += f'<h3 style="color:#0a0;">{topic}</h3>'
            for title, url in items:
                if is_video:
                    html_block += f'<a href="#" onclick="playVideo(\'{url}\')">{title}</a>'
                else:
                    html_block += f'<a href="{url}" target="_blank">{title}</a>'
        return html_block

    video_links = build_links(videos_grouped, is_video=True)
    pdf_links = build_links(pdfs_grouped)
    other_links = "".join(f'<a href="{url}" target="_blank">{name}</a>' for name, url in others)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{name}</title>
  <link href="https://vjs.zencdn.net/8.10.0/video-js.css" rel="stylesheet">
  <style>
    body {{
      background: #e9ecef;
      font-family: Arial;
      margin: 0;
      color: #333;
    }}
    .header {{
      background: #000;
      color: #ff0000;
      text-align: center;
      padding: 20px;
      font-size: 24px;
    }}
    .subheading {{ color: white; font-size: 14px; }}
    .tab {{
      display: inline-block; margin: 5px; padding: 15px;
      border-radius: 5px; background: white; cursor: pointer; font-weight: bold;
    }}
    .tab:hover {{ background: red; color: white; }}
    .content {{ display: none; padding: 20px; }}
    .video-list a, .pdf-list a, .other-list a {{
      display: block; margin: 5px 0; padding: 10px;
      background: #000; color: #ff0000; border-radius: 5px; text-decoration: none;
    }}
    .video-list a:hover, .pdf-list a:hover, .other-list a:hover {{
      background: red; color: white;
    }}
    #video-player {{ width: 90%; max-width: 800px; margin: 20px auto; }}
    .footer {{
      margin-top: 30px; padding: 10px; text-align: center;
      background: #1c1c1c; color: white;
    }}
  </style>
</head>
<body>

<div class="header">
  {name}
  <div class="subheading">📥 Extracted By: <a href="https://t.me/" target="_blank">🚩 𝐉𝐀𝐈 𝐁𝐀𝐉𝐑𝐀𝐍𝐆 𝐁𝐀𝐋𝐈 🚩</a></div>
</div>

<div id="video-player">
  <video id="jai-bajrangbali-player" class="video-js" controls preload="auto" width="100%" height="360">
    <source src="" type="application/x-mpegURL" />
  </video>
</div>

<div style="text-align:center;">
  <input type="text" id="url-input" placeholder="Enter video URL" style="width:60%; padding:8px;">
  <button onclick="playCustomUrl()" style="padding:8px 16px;">Play</button>
</div>

<div class="tabs" style="text-align:center;">
  <div class="tab" onclick="showContent('videos')">Videos</div>
  <div class="tab" onclick="showContent('pdfs')">PDFs</div>
  <div class="tab" onclick="showContent('others')">Others</div>
</div>

<div id="videos" class="content"><h2>All Videos</h2><div class="video-list">{video_links}</div></div>
<div id="pdfs" class="content"><h2>All PDFs</h2><div class="pdf-list">{pdf_links}</div></div>
<div id="others" class="content"><h2>Others</h2><div class="other-list">{other_links}</div></div>

<div class="footer">🚩 Extracted By: <a href="https://t.me/" target="_blank">𝐉𝐀𝐈 𝐁𝐀𝐉𝐑𝐀𝐍𝐆 𝐁𝐀𝐋𝐈</a></div>

<script src="https://vjs.zencdn.net/8.10.0/video.min.js"></script>
<script>
  const player = videojs('jai-bajrangbali-player');
  function playVideo(url) {{
    if (url.includes('.m3u8')) {{
      player.src({{ type: 'application/x-mpegURL', src: url }});
      player.play();
    }} else {{
      window.open(url, '_blank');
    }}
  }}
  function playCustomUrl() {{
    const url = document.getElementById("url-input").value;
    if (url) playVideo(url);
  }}
  function showContent(id) {{
    document.querySelectorAll('.content').forEach(el => el.style.display = 'none');
    document.getElementById(id).style.display = 'block';
  }}
  document.addEventListener('DOMContentLoaded', () => showContent('videos'));
</script>

</body>
</html>
"""


# Pyrogram Bot Handler
app = Client("mybot")

@app.on_message(filters.command("url2html") & filters.reply)
async def txt_to_html(client, message: Message):
    if not message.reply_to_message.document:
        return await message.reply("❗Please reply to a .txt file containing Name: URL lines.")

    file = await message.reply_to_message.download()
    file_name = os.path.basename(file)
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()

    pairs = extract_names_and_urls(content)
    videos, pdfs, others = categorize_urls(pairs)
    html_code = generate_html(file_name, videos, pdfs, others)

    html_path = file.replace(".txt", ".html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_code)

    await message.reply_document(html_path, caption=f"`✅ HTML file generated from {file_name}`")
    
    # Optional logging
    if HTML_LOG_CHANNEL:
        await client.send_document(HTML_LOG_CHANNEL, html_path, caption=f"Uploaded from: {message.from_user.mention}")

    os.remove(file)
    os.remove(html_path)
