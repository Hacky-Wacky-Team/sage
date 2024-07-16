import json

def new_user(id, name, age, location):
  data = read()
  
  data.append({"id": id, "name": name, "age": age, "location": location, 
               "feelings": {"7": ["", "", "", "", "", "", ""], 
                            "6": ["", "", "", "", "", "", ""], 
                            "5": ["", "", "", "", "", "", ""], 
                            "4": ["", "", "", "", "", "", ""], 
                            "3": ["", "", "", "", "", "", ""], 
                            "2": ["", "", "", "", "", "", ""], 
                            "1": ["", "", "", "", "", "", ""],
                            "0": ["", "", "", "", "", "", ""]
                           }
              }
             )
  with open("userinfo.json", "w") as file:
    json.dump(data, file, indent=2)

def read():
  try:
    with open("userinfo.json", "r") as file:
      data = json.load(file)
  except FileNotFoundError:
    return []
  return data


# Function to update user data
def update_userData(user_id, new_data):
  users = read()
  for user in users:
      if user["id"] == user_id:
          for key, value in new_data.items():
              user[key] = value  # Update each field individually
          break

  with open("userinfo.json", "w") as file:
      json.dump(users, file, indent=2)

def update_user_feeling(user, feelings):
  data = read()
    
  data[user]["feelings"] = feelings
  
  with open("userinfo.json", "w") as file:
    json.dump(data, file, indent=2)

#Function that updates the user's current feelings for the day
def update_current_feeling(user, feeling):
  data = read()

  usercounter = 0
  for person in data:
    if person["id"] == user:
      data[usercounter]["feelings"]["0"] = feeling
      break
    usercounter += 1
  with open("userinfo.json", "w") as file:
    json.dump(data, file, indent=2)
  return

#Function that updates the user's weather info
def update_weather(user, weather):
  data = read()
  
  data[user]["feelings"]["0"][6] = weather
  
  with open("userinfo.json", "w") as file:
    json.dump(data, file, indent=2)
