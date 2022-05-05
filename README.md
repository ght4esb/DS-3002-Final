# NYT-Discord-Bot
Final project submission for DS3002 Database Systems

## Motivation
The motivation of this project was to build a discord bot that interacts with user instructions and connects to an external data source to provide valuable real-time information.

## Benchmarks
### 1. "help" Message
Users can access the help message by typing '!help' in the discord guild chat. The bot replys with user instructions. For more detailed help, users can type '!help' followed by the name of the commannd (ex: '!help game').
### 2. Three Commands or Functions
1. The '!game' command starts a publishing year guessing game. The player has three guesses to guess the same year in which the New York Times published three articles. After three guesses, the game is over. If the user submits a non-year guess, the game ends and instructs the user to begin again with a new set of articles.
2. The '!top' command sends the current day's most viewed New York Times article headline and url in the discord chat.
3. The '!movie' command sends a random movie review from the New York Times movie review section. These results are ordered by most recent publish date and restricted to critic's choice movies to ensure users recieve up-to-date, quality movie recommendations.

## 3. Informative Errors
The bot is coded to catch various errors in making each API call and sending non-integer guesses in the game.

## 4. External Data Sources
This project makes api calls on three different New York Times APIs. Developers can make accounts at https://developer.nytimes.com/. The '!game' command uses the Archive Search API by generating a random year, month, and day to restrict API calls. The '!top' command uses the Most Popular API and parameters include a period of 1 days included and article view counts. The '!movie' command uses the Movie Reviews API. Importantly, this implementation of the Movie Reviews API restricts results to movies that reviewers recommended to others and the 20 most recent reviews by movie opening date.

## 5. Hosting the bot
This project uses Repl.it to host a server for free. After an hour of inactivity on a free Repl.it account, the bot dies. So, following a tutorial from (https://www.freecodecamp.org/news/create-a-discord-bot-with-python/), the bot uses UptimeBot to ping the Repl.it server every five minutes to keep the bot alive.
