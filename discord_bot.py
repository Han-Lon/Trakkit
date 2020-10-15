import praw
import csv
import os
import discord


# TODO Move all discord bot functions to this class, and throw in an on_message class for returning actual comments
class OrangeBot(discord.Client):

    comms = []

    # Function for finding new comments based on comment IDs. Takes two lists as x (new comment IDs) and y
    # (old comment IDs). Returns true if new comments have been posted
    def same_comm(self, x, y):
        newComm = False
        numComm = 0
        x_set = set(x)
        y_set = set(y)
        z_set = [x for x in x_set if x not in y_set]
        if (len(z_set) == 0):
            newComm = False
            return newComm, numComm, z_set
        else:
            newComm = True
            numComm = len(z_set)
            return newComm, numComm, z_set

    # Grab the 5 most recent comments and their IDs from a Reddit user
    def grab(self):
        reddit = praw.Reddit(client_id=CONF[0],
                             client_secret=CONF[1],
                             user_agent=CONF[2])

        # Determines the redditor of interest. Instantiates two new arrays for storing comment information
        redditor1 = reddit.redditor(USER)
        commsID = []
        commsBody = []

        # Pulls the comment IDs of the five newest comments posted by the redditor
        for comment in redditor1.comments.new(limit=5):
            commsID.append(comment.id)
            commsBody.append(comment.body)

        return commsID, commsBody

    # Compare a list of 5 comment IDs to a stored list of 5 commend IDs. Actually comparison done in same_comm
    def compare(self, x):
        # TODO a lot of these file handling objects can be changed to io.BytesIO file objects to save space
        if not os.path.exists('Testarooni.csv'):
            with open('Testarooni.csv', 'w+', newline='\n', encoding='utf-8') as csvfile:
                csvfile.truncate()

        # Opens the csv file where the old comment information is stored
        with open('Testarooni.csv', 'r') as csvfile:
            commReader = csv.reader(csvfile)
            oldCommList = []
            # Throws an exception if there are missing comment IDs in Testarooni.csv
            try:
                for row in commReader:
                    oldCommList.append(row[0])
            # Fill oldCommList with placeholder data if Testarooni.csv doesn't have 5 IDs
            except IndexError as e:
                for i in range(5):
                    oldCommList.append('Placeholder')

        results = self.same_comm(x, oldCommList)
        return results

    # When the bot is first instantiated
    async def on_ready(self):
        usr = client.get_user(os.environ['discord_user_id'])
        try:
            await usr.send('Ahoy-hoy! We\'re online!')
            result = await self.activity_check()
            await usr.send('|| We have ' + str(result[1]) + ' new briefings ||')
        except Exception as e:
            await usr.send('An exception occurred: ' + str(e) + '\n' + e.with_traceback())

    # For retrieving comment history (last 5) or logging out
    async def on_message(self, message):
        global comms
        usr = client.get_user(os.environ['discord_user_id'])
        if message.author == usr:
            await usr.send('Hi!')
            if message.content == 'Logout':
                await usr.send('Logging out...')
                await self.logout()
            else:
                for x in comms[1]:
                    await usr.send('|| ' + str(x) + ' ||')

    # Check if the target redditor has posted new comments
    async def activity_check(self):
        global comms
        comms = self.grab()
        res = self.compare(comms[0])
        if res[0]:
            # Overwrites comments.csv with the new comment IDs, and uploads it to AWS S3
            with open('Testarooni.csv', 'w+', newline='\n', encoding='utf-8') as csvfilewrite:
                csvfilewrite.truncate()
                spamwriter = csv.writer(csvfilewrite)
                for item in comms[0]:
                    spamwriter.writerow([item])
        return res


if __name__ == '__main__':

    CONF = []
    USER = ''
    # Grab our config values
    with open('Config.csv', 'r', newline='\n', encoding='utf-8') as confile:
        confrdr = csv.reader(confile)
        for z in confrdr:
            z = ''.join(z)
            CONF.append(z)
    # Grab the Discord user info
    with open('usr.txt', 'r', encoding='utf-8') as usrfile:
        USER = usrfile.read()

    cliToken = os.environ['discord_cli_token']
    # Run the bot
    client = OrangeBot()
    client.run(cliToken)

