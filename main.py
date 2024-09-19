# SAD Discord Bot
# Made by Jeffery, Jonathan, Samuel, and Eric <3 
#yum yum commit testpin
# Created for Steel City Hacks 2024: Winter Hackathon
# Link: https://schwinter2024.devpost.com/

#all the imports
import os
#For discord commands
import discord
from discord.commands import Option
from discord.ext import commands
from discord.ui import Button, Select, View
import asyncio
#Our commands in other files
from datatool import new_user, read, update_user_feeling, update_userData, update_current_feeling, update_weather
#Other imports
from weather import get_weather_data
import copy
import random

# For the machine learning
from machine import predict, change_to_list
from sklearn import tree
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, confusion_matrix
import matplotlib.pyplot as plt
import numpy as np

#intents / bot permissions
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)


#Command for the user to register
@bot.slash_command(guild_ids = [1206437112715542558], description = "Register a user")
async def register(ctx, 
  name:Option(str,"What is your name?", require = True),
  age:Option(int,"What is your age?", require = True),
  location:Option(str,"What is your location (city)?", require = True),
  ):
  userID = ctx.author.id
  newUser = True
  users = read()
  #Loops through the users in the file to make sure the user isn't already in the file
  for user in users:
    if user["id"] == userID:
      await ctx.respond("You are already registered!")
      newUser = False
  print(userID)
#stores user info
  if newUser:
    new_user(userID, name, age, location)
    
    registerEmbed = discord.Embed(
      title="You registered!",
      description=f"🫵 Name: {name}\n📅 Age: {age}\n:earth_americas: Location: {location}",
      color = 0x00ff00
    )
    registerEmbed.set_thumbnail(url=ctx.author.avatar.url)  # Set user's avatar as thumbnail
    await ctx.respond(embed=registerEmbed)

#Command to display weather at user's location
@bot.slash_command(guild_ids=[1206437112715542558], description="Gathers the weather info")
async def weather(ctx):
  #Getting the user and their location
  users = read()
  userID = ctx.author.id
  id = discordID_to_id(userID)
  location = users[id]["location"]

  #Creating weather embed
  url = "https://www.google.com/search?q=weather+" + location
  weatherEmbed = discord.Embed(
    title="Today's Weather! ️🌤️",
    description="Retrieving weather information...",  # Initial placeholder
    color=0xFFA500,
  )
  weatherEmbed.set_thumbnail(url="https://ssl.gstatic.com/onebox/weather/64/partly_cloudy.png")
  #Getting weather data and sending it to user
  await ctx.respond(embeds=[weatherEmbed])
  weather = get_weather_data(location)
  await asyncio.sleep(5)
  weatherEmbed.description = f"⏰ {weather[1]}"
  weatherEmbed.add_field(name="️🌎 Location:", value=f"[{location}]({url})", inline=True)
  weatherEmbed.add_field(name="️🌡️ Temp:", value=f"{weather[0]}", inline=True)
  weatherEmbed.add_field(name="️🌤️ Sky:", value=f"{weather[2]}.", inline=True)
  #Updating loading message with the weather
  await ctx.interaction.edit_original_response(embeds=[weatherEmbed])

  

#Command to view user's profile
@bot.slash_command(guild_ids = [1206437112715542558], description = "Views user profile")
@commands.has_permissions(manage_messages=True)
async def profile(ctx):
  #Buttons to edit user's info
  editNameButton = Button(label=" edit name", style=discord.ButtonStyle.grey, emoji="📝")
  editAgeButton = Button(label="   edit age",style=discord.ButtonStyle.grey, emoji="📅")
  editLocationButton = Button(label="   edit location",style=discord.ButtonStyle.grey, emoji="🌎")

  #Creating the views for each button 
  view = View()
  view.add_item(editNameButton)
  view.add_item(editAgeButton)
  view.add_item(editLocationButton)
  #Checking if the user exists in the data file
  users = read()
  userID = ctx.author.id
  user_in = False
  for user in users:
    if user["id"] == userID:
      user_in = True
      
      #Retrieving user data
      feelings_feeling = str(user["feelings"]["0"][0])
      feelings_energy_level = str(user["feelings"]["0"][1])
      feelings_sleep = str(user["feelings"]["0"][2])
      feelings_appetite = str(user["feelings"]["0"][3])
      feelings_outside = str(user["feelings"]["0"][4])
      feelings_concentration = str(user["feelings"]["0"][5])
      feelings_weather = str(user["feelings"]["0"][6])

      #Creating the embed's description
      feelings_value1 = f"> Feeling → {feelings_feeling}\n> Energy Level → {feelings_energy_level}\n> Sleep → {feelings_sleep}\n> Appetite → {feelings_appetite}\n> Outside → {feelings_outside}\n> Concentration → {feelings_concentration}\n> Weather → {feelings_weather}"

      #Creating an embed with the user's profile information
      viewEmbed = discord.Embed(title=f"Hello {user['name']}! 👋",
                                    description = f"📅 Age: {user['age']}\n:earth_americas: Location: {user['location']}\n\u200B",
                                    color=0x206694)
      viewEmbed.add_field(name = "\n🤗 Today's Feelings", value=feelings_value1, inline=False)
      viewEmbed.set_thumbnail(url=ctx.author.avatar.url)  #Set user's avatar as thumbnail
      interaction = await ctx.respond(embed=viewEmbed, view=view) #Respond with the data of the current user

      #Edit Name Button Callback
      async def editNameButton_callback(interaction):
        if interaction.user.id == userID:
          #Get the new name from the user
          viewEmbed.title = "Enter your new name..."
          viewEmbed.description = ""
          viewEmbed.remove_field(index=0)
          viewEmbed.remove_thumbnail()
          await interaction.response.defer()
          interactionEnter = await interaction.message.edit(embed=viewEmbed, view=view)
          try:
            userResponse = await bot.wait_for("message", check=lambda message: message.author == ctx.author, timeout=20.0)
            new_name = userResponse.content
            #Update user's name in the JSON file
            update_userData(userID, {"name": new_name})
            #Update viewEmbed title with the new name
            viewEmbed.title = f"Hello {new_name}! 👋"
            viewEmbed.description = f"📅 Age: {user['age']}\n:earth_americas: Location: {user['location']}\n\u200B"
            viewEmbed.add_field(name = "\n🤗 Today's Feelings", value=feelings_value1, inline=False)
            viewEmbed.set_thumbnail(url=ctx.author.avatar.url)
  
            #Edit the original message to reflect the changes
            await interaction.message.edit(embed=viewEmbed, view=view)
            await interaction.followup.send(f"Name updated to {new_name}!", ephemeral=True)
          except asyncio.TimeoutError:
            await interaction.followup.send("Timeout: You took too long to respond!", ephemeral=True)
            viewEmbed.title=f"Hello {user['name']}! 👋"
            viewEmbed.description = description = f"📅 Age: {user['age']}\n:earth_americas: Location: {user['location']}\n\u200B"
            viewEmbed.add_field(name = "\nToday's Feelings 🤗", value=feelings_value1, inline=False)
            viewEmbed.set_thumbnail(url=ctx.author.avatar.url)
            await interaction.message.edit(embed=viewEmbed, view=view)
        else:
          await interaction.response.send_message("This is not your profile!", ephemeral=True)

      #Edit Age Button Callback 
      async def editAgeButton_callback(interaction):
        if interaction.user.id == userID:
          #Get the new age from the user
          viewEmbed.title = "Enter your new age..."
          viewEmbed.description = ""
          viewEmbed.remove_field(index=0)
          viewEmbed.remove_thumbnail()
          await interaction.response.defer()
          interactionEnter = await interaction.message.edit(embed=viewEmbed, view=view)
          try:
            userResponse = await bot.wait_for("message", check=lambda message: message.author == ctx.author, timeout=20.0)
            new_age = userResponse.content
            try:
              new_age = int(new_age)
              #Update user's name in the JSON file
              update_userData(userID, {"age": new_age})
              #Update entire viewEmbed 
              viewEmbed.title=f"Hello {user['name']}! 👋"
              viewEmbed.description = description = f"📅 Age: {new_age}\n:earth_americas: Location: {user['location']}\n\u200B"
              viewEmbed.add_field(name = "\n🤗 Today's Feelings", value=feelings_value1, inline=False)
              viewEmbed.set_thumbnail(url=ctx.author.avatar.url)

              #Edit the original message to reflect the changes
              await interaction.message.edit(embed=viewEmbed, view=view)
              await interaction.followup.send(f"Age updated to {new_age}!", ephemeral=True)
            except ValueError:
              await interaction.followup.send("Invalid age format. Please interact again and enter a valid number!", ephemeral=True)
          except asyncio.TimeoutError:
            await interaction.followup.send("Timeout: You took too long to respond!", ephemeral=True)
            viewEmbed.title=f"Hello {user['name']}! 👋"
            viewEmbed.description = description = f"📅 Age: {user['age']}\n:earth_americas: Location: {user['location']}\n\u200B"
            viewEmbed.add_field(name = "\n🤗 Today's Feelings", value=feelings_value1, inline=False)
            viewEmbed.set_thumbnail(url=ctx.author.avatar.url)
            await interaction.message.edit(embed=viewEmbed, view=view)
        else:
          await interaction.response.send_message("This is not your profile!", ephemeral=True)

      #Edit Location Button Callback 
      async def editLocationButton_callback(interaction):
        if interaction.user.id == userID:
          #Get the new location from the user
          viewEmbed.title = "Enter your new location..."
          viewEmbed.description = ""
          viewEmbed.remove_field(index=0)
          viewEmbed.remove_thumbnail()
          await interaction.response.defer()
          interactionEnter = await interaction.message.edit(embed=viewEmbed, view=view)
          try:
            userResponse = await bot.wait_for("message", check=lambda message: message.author == ctx.author, timeout=20.0)
            new_location = userResponse.content
            #Update user's name in the JSON file
            update_userData(userID, {"location": new_location})
            # Update viewEmbed title with the new name
            viewEmbed.title=f"Hello {user['name']}! 👋"
            viewEmbed.description = description = f"📅 Age: {user['age']}\n:earth_americas: Location: {new_location}\n\u200B"
            viewEmbed.add_field(name = "\n🤗 Today's Feelings", value=feelings_value1, inline=False)
            viewEmbed.set_thumbnail(url=ctx.author.avatar.url)
  
            #Edit the original message to reflect the changes
            await interaction.message.edit(embed=viewEmbed, view=view)
            await interaction.followup.send(f"Location updated to {new_location}!", ephemeral=True)
          except asyncio.TimeoutError:
            await interaction.followup.send("Timeout: You took too long to respond!", ephemeral=True)
            viewEmbed.title=f"Hello {user['name']}! 👋"
            viewEmbed.description = description = f"📅 Age: {user['age']}\n:earth_americas: Location: {user['location']}\n\u200B"
            viewEmbed.add_field(name = "\n🤗 Today's Feelings", value=feelings_value1, inline=False)
            viewEmbed.set_thumbnail(url=ctx.author.avatar.url)
            await interaction.message.edit(embed=viewEmbed, view=view)
        else:
          await interaction.response.send_message("This is not your profile!", ephemeral=True)

      editNameButton.callback = editNameButton_callback
      editAgeButton.callback = editAgeButton_callback
      editLocationButton.callback = editLocationButton_callback
      break  #Exit the loop once the user is found
  #Tell the user to register if they arent in the data file
  if not user_in:
      await ctx.respond("You are not registered! Type /register to register.")

#Command for users to see all the commands
@bot.slash_command(guild_ids = [1206437112715542558], description = "List of the commands")
async def help(ctx):
  embedHelp = discord.Embed(
    title="All Commands", 
    description=f"📝 **/register** → Register a profile \n⭐ **/profile** → View your profile \n😎 **/daily** → Do your daily questions \n📚 **/activity** → Get an activity to boost your mental health\n⏳ **/predicts** → Predict whether you may have SAD\n🌤️ **/weather** → Get today's weather based on your location!",  
    color=0x206694
  )
  await ctx.respond(embed=embedHelp)

seasons = ["winter", "spring", "summer", "fall"]

#Command that gives the user an activity to use
@bot.slash_command(guild_ids = [1206437112715542558], description = "Get an idea for an activity!")
async def activity(ctx):
  #Buttons for each season
  springButton = Button(label="Spring", style=discord.ButtonStyle.grey, emoji="🌸")
  summerButton = Button(label="Summer",style=discord.ButtonStyle.grey, emoji="☀️")
  autumnButton = Button(label="Autumn",style=discord.ButtonStyle.grey, emoji="🍂")
  winterButton = Button(label="Winter",style=discord.ButtonStyle.grey, emoji="❄️")

  users = read()
  userID = ctx.author.id

  #Creating the views for each button
  view = View()
  view.add_item(springButton)
  view.add_item(summerButton)
  view.add_item(autumnButton)
  view.add_item(winterButton)
  
  #WINTER activities
  winterActivities = [
    "Build a snowman", 
    "Play a board game", 
    "Hang out with friends", 
    "Play a sport",
    "Go to the park",
    "Go to the movies",
    "Try a new hobby",
    "Go snowboarding",
    "bake something",
    "try new food recipe",
    "Travel to somewhere new",
    "Have a snowball fight with your friends",
    "Learn to play an instrument",
    "Make hot chocolate",
    "Try crocheting",
    "Try skating",
    "Go snow tubing",
    "Go skiing",
    "Arts and Crafts",
    "Warm Baths and Aromatherapy"
  ]
  #Summer activities
  summerActivities = [
    "biking",
    "go to the beach",
    "hiking", 
    "go to the pool",
    "go to the gym",
    "Feel the sun on your back", 
    "Picnics",
    "Camping",
    "Barbecues",
    "Fruit Picking",
    "Outdoor Yoga",
    "Gardening", 
    "Outdoor Water Parks",
    "meditation",
    "nature walks",
    "outdoor concerts",
    "wildlife observation",
    "listening to nature sound therapy",
    "tai chi",
    "Outdoor Gratitude Journaling"
  ]
  #Spring activities
  springActivities = [
    "Morning Sunlight Exposure", 
    "Gardening",
    "Nature Walks", 
    "Outdoor Yoga", 
    "Picnics", 
    "Bird Watching",
    "Volunteer Gardening",
    "Outdoor Sports",
    "Al Fresco Dining",
    "Visit Botanical Gardens",
    "Spring Cleaning",
    "plan a short trip to a nearby beach, lake, or countryside.",
    "Stargazing",
    "Outdoor Meditation",
    "Join Outdoor fitness classes",
    "Plan a Flower-Viewing Outing", 
    "Create a Nature Journal",
    "outdoor movie nights"
  ]
  #Autumn activities
  autumnActivities = [
    "Morning Light Therapy",
    "Outdoor Walks",
    "Autumn Foliage Drives", 
    "Photography", 
    "Yoga", 
    "Pumpkin Carving", 
    "Apple Picking",
    "Cooking/Baking", 
    "Bonfires", 
    "Reading by the Fireplace", 
    "Autumn-themed crafts such as making wreaths",
    "Mindfulness Meditation",
    "Warm Baths", 
    "Get involved in community service activities", 
    "Birdwatching",
    "Harvest Festivals", 
    "Journaling", 
    "Indoor Gardening", 
    "Creative Writing", 
    "Stargazing"
  ]
  #Creating the embed to display the activity
  embedActivity = discord.Embed(
    title=f"Activities!",
    description = "Choose your season to get activity suggestions that\nmay help with SAD based on your local season.",
    color=0x206694
  )
  embedActivity.set_thumbnail(url="https://www.clker.com/cliparts/F/5/I/M/f/U/running-icon-white-on-transparent-background-hi.png")  # Set user's avatar as thumbnail
  embedActivity.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
  interaction = await ctx.respond(embed=embedActivity, view=view) 
  #Callback function for spring button
  async def springButton_callback(interaction):
    if interaction.user.id == userID:
      # Edit the original message to reflect the changes
      randSpringActivity = random.choice(springActivities)
      embedActivity.title="🌸 Spring Activities 🌸"
      embedActivity.description = f"**{randSpringActivity}**"
      embedActivity.set_thumbnail(url="https://wallpapercave.com/wp/wp5379951.jpg")
      embedActivity.color = 0xe91e63
        
      await interaction.response.defer()
      await interaction.message.edit(embed=embedActivity, view=view)
    else:
      await interaction.response.send_message("This is not your activity!", ephemeral=True)
  #Callback function for summer button
  async def summerButton_callback(interaction):
    if interaction.user.id == userID:
      # Edit the original message to reflect the changes
      randSummerActivity = random.choice(summerActivities)
      embedActivity.title="☀️ Summer Activities ☀️"
      embedActivity.description = f"**{randSummerActivity}**"
      embedActivity.set_thumbnail(url="https://wallpapercave.com/wp/mLFxPZG.jpg")
      embedActivity.color = 0xf1c40f
      
      await interaction.response.defer()
      await interaction.message.edit(embed=embedActivity, view=view)
    else:
      await interaction.response.send_message("This is not your activity!", ephemeral=True)
  #Callback function for autumn button
  async def autumnButton_callback(interaction):
    if interaction.user.id == userID:
      # Edit the original message to reflect the changes
      randAutumnActivity = random.choice(autumnActivities)
      embedActivity.title="🍂 Autumn Activities 🍂"
      embedActivity.description = f"**{randAutumnActivity}**"
      embedActivity.set_thumbnail(url="https://www.wallpapertip.com/wmimgs/26-264985_fall-foliage-pictures-data-src-beautiful-forest-in.jpg")
      embedActivity.color = 0xe67e22

      await interaction.response.defer()
      await interaction.message.edit(embed=embedActivity, view=view)
    else:
      await interaction.response.send_message("This is not your activity!", ephemeral=True)
  #Callback function for winter button
  async def winterButton_callback(interaction):
    if interaction.user.id == userID:
      # Edit the original message to reflect the changes
      randWinterActivity = random.choice(winterActivities)
      embedActivity.title="❄️ Winter Activities ❄️"
      embedActivity.description = f"**{randWinterActivity}**"
      embedActivity.set_thumbnail(url="https://cdn.discordapp.com/attachments/1206437113202089996/1208918957667655730/OIP.png?ex=65e50884&is=65d29384&hm=ba4cf904981faade77f853e85492ff7f53fd553ee12cec3f4030a07947241a9d&")
      embedActivity.color = 0x1abc9c
      
      await interaction.response.defer()
      await interaction.message.edit(embed=embedActivity, view=view)
    else:
      await interaction.response.send_message("This is not your activity!", ephemeral=True)
  
  springButton.callback = springButton_callback
  summerButton.callback = summerButton_callback
  autumnButton.callback = autumnButton_callback
  winterButton.callback = winterButton_callback
  
#Command for daily test
@bot.slash_command(guild_ids=[1206437112715542558], description="Daily test log")
@commands.cooldown(1, 30, commands.BucketType.user)
async def daily(ctx):
  users = read()
  userID = ctx.author.id
  user_in = False
  feelings = ["","","","","",""]
  #Checking if user is in the data file
  for user in users:
    if user["id"] == userID:
      user_in = True
  if user_in:
      feeling_select = Select(
        min_values = 1, # Minimum number of options that must be chosen
        max_values = 1, # Maximum number of options that can be chosen
        #options for the selcect drop down
        placeholder="Choose your feeling" ,options=[
          discord.SelectOption(
            label="Bad", 
            emoji="😥", 
          ),
          discord.SelectOption(
            label="Neutral", 
            emoji="🙂", 
          ),
          discord.SelectOption(
            label="Good", 
            emoji="😄", 
          )
        ]
      )
      #Callback for this select
      async def my_callback(interaction):
        if interaction.user.id == userID:
          selected_option = interaction.data['values'][0]
          feelings[0] = selected_option
          await interaction.response.defer()
          await energy_level(ctx, feelings)
    
      feeling_select.callback = my_callback
      view = View()
      view.add_item(feeling_select)
      await ctx.respond("**How do you feel right now?**", view=view)
  else:
    await ctx.respond("You are not registered! Type /register to register.")

#Function for energy select
async def energy_level(ctx, feelings):
  userID = ctx.author.id
  feelings = feelings
  energy_select = Select(
    min_values = 1, # Minimum number of options that must be chosen
    max_values = 1, # Maximum number of options that can be chosen
    #options for the selcect drop down
    placeholder="Choose your energy level" ,options=[
      discord.SelectOption(
        label="Low", 
        emoji="😴", 
      ),
      discord.SelectOption(
        label="Medium", 
        emoji="🙂", 
      ),
      discord.SelectOption(
        label="High", 
        emoji="🤩", 
      )
    ]
  )
  #Callback for this select
  async def my_callback(interaction):
    if interaction.user.id == userID:
        selected_option = interaction.data['values'][0]
        feelings[1] = selected_option
        await interaction.response.defer()
        await sleep_quality(ctx, feelings)

  energy_select.callback = my_callback
  view = View()
  view.add_item(energy_select)
  await ctx.respond("**Whats your energy level?**", view=view)

#Function for sleep quality select
async def sleep_quality(ctx, feelings):
  userID = ctx.author.id
  feelings = feelings
  sleep_select = Select(
    min_values = 1,
    max_values = 1,
    placeholder="How was your sleep last night?" ,options=[
      discord.SelectOption(
        label="Poor", 
        emoji="😪", 
      ),
      discord.SelectOption(
        label="Normal", 
        emoji="😀", 
      ),
      discord.SelectOption(
        label="Great", 
        emoji="😇", 
      )
    ]
  )
  #Callback for this select
  async def my_callback(interaction):
    if interaction.user.id == userID:
        selected_option = interaction.data['values'][0]
        feelings[2] = selected_option
        await interaction.response.defer()
        await appetite(ctx, feelings)

  sleep_select.callback = my_callback
  view = View()
  view.add_item(sleep_select)
  await ctx.respond("**How was your sleep last night?**", view=view)

#Function for appetite select
async def appetite(ctx, feelings):
  userID = ctx.author.id
  feelings = feelings
  appetite_select = Select(
    min_values = 1,
    max_values = 1,
    placeholder="How's your appetite?" ,options=[
      discord.SelectOption(
        label="Poor", 
        emoji="🤢", 
      ),
      discord.SelectOption(
        label="Normal", 
        emoji="😀", 
      ),
      discord.SelectOption(
        label="Extreme", 
        emoji="😰", 
      )
    ]
  )
  #Callback for this select
  async def my_callback(interaction):
    if interaction.user.id == userID:
        selected_option = interaction.data['values'][0]
        feelings[3] = selected_option
        await interaction.response.defer()
        await outside_time(ctx, feelings)

  appetite_select.callback = my_callback
  view = View()
  view.add_item(appetite_select)
  await ctx.respond("**How's your appetite?**", view=view)

#Function for outside time select
async def outside_time(ctx, feelings):
  userID = ctx.author.id
  feelings = feelings
  outside_time_select = Select(
    min_values = 1,
    max_values = 1,
    placeholder="How long did you spend outside today?" ,options=[
      discord.SelectOption(
        label="< 30 minutes", 
        emoji="🏠", 
      ),
      discord.SelectOption(
        label="1 hour", 
        emoji="🌳", 
      ),
      discord.SelectOption(
        label="2 hour+", 
        emoji="☀️", 
      )
    ]
  )
  #Callback for this select
  async def my_callback(interaction):
    if interaction.user.id == userID:
        selected_option = interaction.data['values'][0]
        feelings[4] = selected_option
        await interaction.response.defer()
        await concentration(ctx, feelings)

  outside_time_select.callback = my_callback
  view = View()
  view.add_item(outside_time_select)
  await ctx.respond("**How long did you spend outside?**", view=view)

#Function for concentration select
async def concentration(ctx, feelings):
  data = read()
  userID = ctx.author.id
  feelings = feelings
  concentration_select = Select(
    min_values = 1,
    max_values = 1,
    placeholder="How's your concentration level?" ,options=[
      discord.SelectOption(
        label="Poor", 
        emoji="🥱", 
      ),
      discord.SelectOption(
        label="Normal", 
        emoji="😀", 
      ),
      discord.SelectOption(
        label="Great", 
        emoji="🧘", 
      )
    ]
  )
  #Callback for this select
  async def my_callback(interaction):
    if interaction.user.id == userID:
        await pushback(ctx)
        selected_option = interaction.data['values'][0]
        id = discordID_to_id(userID)
        await interaction.response.send_message("Your log is complete!")
        weather = get_weather_data(data[id]["location"])
        await asyncio.sleep(10)
        feelings[5] = selected_option
        feelings.append(weather[2])
        update_current_feeling(userID, feelings)
        await ctx.respond("Your data has been updated!")

  concentration_select.callback = my_callback
  view = View()
  view.add_item(concentration_select)
  await ctx.respond("**How's your concentration level?**", view=view)

  await asyncio.sleep(30)
  await ctx.respond(f"{ctx.author.mention}: Reminder to do /Daily")

#Function for command erros
@bot.event
async def on_application_command_error(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    await ctx.respond(error)
  else:
    raise error

#Function that pushes user's feelings back a day
async def pushback(ctx):
  userID = ctx.author.id
  users = read()
  usercounter = 0
  #Loops through users to get the user's id in the data
  for user in users:
    if user["id"] == userID:
      break
    usercounter += 1
  feelings_dict = copy.deepcopy(users[usercounter]["feelings"])

  #Loops through each day of feelings and pushes it back
  for i in range(7, 0, -1):
    feelings_dict[str(i)] = feelings_dict[str(i-1)]

  feelings_dict["1"] = feelings_dict["0"]
  feelings_dict["0"] = ["","","","","","",""]

  update_user_feeling(usercounter, feelings_dict)
  #await ctx.respond("Your pushback has been updated!")

#Function that turns the discord id of a user to the index in the data file
def discordID_to_id(discordID):
  data = read()
  discordID = discordID
  usercounter = 0
  for user in data:
    if user["id"] == discordID:
      return usercounter
    usercounter += 1

#Command that predicts if the user has SAD 
@bot.slash_command(guild_ids = [1206437112715542558], description = "Predicts if you may have SAD")
async def predicts(ctx):
  #Checking if the user is in the data file and stores their feelings dict in a variable
  users = read()
  userID = ctx.author.id
  user_in = False
  feelingsDict = {}
  for user in users:
    if user["id"] == userID:
      user_in = True
      feelingsDict = user["feelings"]
      break
  if user_in == True:
    embedPrediction = discord.Embed(
      title="Your Results:", 
      description="Predicting...",
      color=0x206694
    )

    #Putting user's feelings in ML model
    feelingsList = [feelingsDict]
    await ctx.respond(embed=embedPrediction)
    prediction = predict(feelingsList)
    await asyncio.sleep(10)
    good_string = str("✅ You aren't likely to have Seasonal Affective Disorder. You are displaying little to no symptoms of SAD.")
    bad_string = str("⚠️ You may have Seasonal Affective Disorder. You are displaying multiple symptoms of SAD.")
    
    #Creating different responses based on ML descision
    if prediction == ['good']:
      embedPrediction.description = good_string
      embedPrediction.color=0x2ecc71
      embedPrediction.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
      embedPrediction.add_field(name="️🚨 DISCLAIMER:", value="It's important to seek guidance from a medical professional for further assistance. Please consult a doctor for more accurate results.")
      embedPrediction.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Eo_circle_green_checkmark.svg/2048px-Eo_circle_green_checkmark.svg.png")

      await ctx.interaction.edit_original_response(embed=embedPrediction)
    else:
      embedPrediction.description = bad_string
      embedPrediction.color=0xe74c3c
      embedPrediction.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
      embedPrediction.add_field(name="️🚨 DISCLAIMER:", value="It's important to seek guidance from a medical professional for further assistance. Please consult a doctor for more accurate results.")
      embedPrediction.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/6897/6897039.png")
      
      await ctx.interaction.edit_original_response(embed=embedPrediction)
  else:
    await ctx.respond("You are not registered! Type /register to register.")
  
#This tells us when the bot comes online
@bot.event
async def on_ready():
  print("Bot is Up and Ready!")
  await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.playing, name="Listening to /help"))


my_secret = os.environ['SECRET_KEY']
bot.run(my_secret)
