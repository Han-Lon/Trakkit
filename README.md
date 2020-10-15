## Welcome to Trakkit, an automated way to be alerted to new posts from a Reddit user

### Trakkit allows you to be notified, whether by email or Discord direct message, of a new post from a Redditor as soon as it's posted

Basic architecture
&nbsp;
- Trakkit Cloudwatch event fires off once every x minutes (default is 60, so once an hour)
- Trakkit Lambda uses Reddit's PRAW API to scrape a user's account for most recent comments
- If a comment is found, Trakkit triggers a notification via SNS topic to email/text recipients alerting them of it
- Added functionality to alert users via Discord bot

Trakkit is still a WIP but is relatively stable at the moment. Roadmap includes writing detailed setup instructions so YOU can easily start tracking your favorite Redditors