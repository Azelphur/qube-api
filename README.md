# qube-api
Interact with qube smart bulbs via the (unofficial) API

I don't even own these bulbs, so YMMV with this library, but it worked well enough for me to start a disco party at my friends house.

Example code which will set all your Qube bulbs to green.
```
# Login to the Qube cloud service, obtain access token
q = Qube('your@email.com', 'your_password')

# Obtain a list of houses, and moods
houses, moods = q.get_users()

# Appliances are in rooms, in houses. Appliances are bulbs.
for house in houses:
    for room in house.rooms:
        for appliance in room.appliances:
            q.set_appliance(appliance.uuid, "00FF0000", Qube.STATE_ON)
```
