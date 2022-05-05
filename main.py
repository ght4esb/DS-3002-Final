# Import necessary packages
from keep_alive import keep_alive
import os
import discord
from discord.ext import commands
import random
import requests
from datetime import datetime 
from datetime import date
import calendar

# define api key for New York Times API
my_apikey = os.environ['NYT_APIKEY']

# define discord guild token and discord bot token 
TOKEN = os.getenv('DISCORD_TOKEN') 
my_secret = os.environ['BOT_TOKEN']

client = discord.Client()

@client.event

async def on_ready():
  print(f'{client.user} has connected to Discord!')

# define prefix to mark each bot command (ex: '!game')
bot = commands.Bot(command_prefix='!')

# send a welcome message to new guild members
# @commands.Cog.listener()
# async def on_member_join(self, member):
#     channel = member.guild.system_channel
#     if channel is not None:
#         await channel.send(f"Welcome to the server {member.mention}! I am NYTBot! I can play a game where you guess what year three articles were published in the NYT. I can show you today's most viewed NYT article. I can also show you a random movie review for a recent movie. Try typing !help to read about all the cool things I can do.\nOr try\n!help game\n!help top\n!help movie\nto learn more about each command.")



'''
!game command plays year guessing game
using three New York Times articles
from a random year. The player must 
guess the correct year with +-5 accuracy.
After three guesses, the game ends.
'''
# refine response to selected day
def get_day(list, day):
	result = []
	for item in list:
    # return a date time object
		d = datetime.strptime(item['pub_date'], '%Y-%m-%dT%H:%M:%S%z')
		if d.day == day:
			result.append(item)
	return result

# declare the !game command
@bot.command(
  name='game',
  help = "Prints three article headlines from a random year between 1851 and the current year to start a year guessing game. The player has three guesses to input the correct year into the channel with +-5 accuracy to win the game. User inputs must be years.",
  brief = "Prints three article headlines for user to guess publication year."
)
async def year_guesser(ctx):
  # get a random year between earliest NYT archive year and current year
  year = random.randint(1851, date.today().year)
  # get a random month (with 1 being January, etc.)
  month = random.randint(1,12)
  # calendar library monthrange function gets total days for month
  numDays = calendar.monthrange(year,month)[1]
  # get a random day for chosen month
  day = random.randint(1, numDays)

  # make NYT Archive API call with year and month
  try:
        response = requests.get(f'https://api.nytimes.com/svc/archive/v1/{year}/{month}.json?api-key={my_apikey}')
        r = response.json()
  except requests.exceptions.HTTPError as errh:
      return "An Http Error occurred:" + repr(errh)
  except requests.exceptions.ConnectionError as errc:
      return "An Error Connecting to the API occurred:" + repr(errc)
  except requests.exceptions.Timeout as errt:
      return "A Timeout Error occurred:" + repr(errt)
  except requests.exceptions.RequestException as err:
      return "An Unknown Error occurred" + repr(err)

  # parse the json response object to documents
  articles = r['response']['docs']

  # get list of articles for the random day
  articles = get_day(articles, day)

  # get three random articles
  randArticleList = random.sample(articles, 3)

  # make a list of three random article headlines
  randArticles = []
  for a in randArticleList:
    headline = a["headline"]["main"]
    randArticles.append(headline)

  # separate each article with one line of whitespace
  r = "\n\n".join(randArticles)
  response = r
  # bot sends three articles and instructs user to guess a year
  await ctx.send(response + "\n\n These articles all come from the same year, guess")

  # user gets three guesses to guess the year with +-5 accuracy
  guess_count = 0
  while guess_count < 3:
    response = await bot.wait_for('message')
    guess_count += 1
    try:
      guess = int(response.content)
    except ValueError: # catch if the user does not enter a number
      await ctx.send('Could not convert data to an integer, type !game to play again')
    high = guess+5
    low = guess-5
    if guess == year: # if the guess is the random year, player wins game
      await ctx.send('You got it!')
      break
    elif guess in range(low,high): # if guess is within +-5, player wins
      await ctx.send('You win! Close enough.')
    elif guess < (year-6): # guess is too low
      await ctx.send('Higher!')
    elif guess > (year+6): # guess is too high
      await ctx.send('Lower!')
  else:
    await ctx.send('You lost. It was ' + year 
                   + ' type !game to play again')



'''
!top command displays the title, abstract, 
and url of the most viewed New York Times article 
of the day based on NYT site traffic data from the NYT Most Popular API.
'''

# declare the !top command
@bot.command(name='top',
            help = 'Calls the NYT Most Popular API to print the most viewed NYT article of the day and its URL to the channel.',
            brief = 'Prints the most viewed NYT news article of the day to the channel.' )
async def top_story(ctx):
  # get all articles with view counts from today
  period = 1 # today
  try:
      query_url = f"https://api.nytimes.com/svc/mostpopular/v2/viewed/{period}.json?api-key={my_apikey}"
      # make the api call and create a json object
      r = requests.get(query_url).json()
  except requests.exceptions.HTTPError as errh:
      return "An Http Error occurred:" + repr(errh)
  except requests.exceptions.ConnectionError as errc:
      return "An Error Connecting to the API occurred:" + repr(errc)
  except requests.exceptions.Timeout as errt:
      return "A Timeout Error occurred:" + repr(errt)
  except requests.exceptions.RequestException as err:
      return "An Unknown Error occurred" + repr(err)
    
  # parse json to most viewed article
  topArticle = r["results"][0]

  # gather the title, abstract, and url
  attributes = []
  attributes.append(topArticle["title"])
  attributes.append(topArticle["abstract"])
  attributes.append(topArticle["url"])
  r = "\n\n".join(attributes)
  response = r

  # send the response to the user
  await ctx.send(response)
  


'''
!movie command displays one random headline, short summary, 
and url from one of the 20 most recent critic's choice New York Times
movie reviews.
'''
# declare the !movie command
@bot.command(name='movie',
            help = 'Bot prints a random NYT critic movie review to the channnel using the NYT Moview Review API. Reviews are limited to the 20 most recent by opening-date for which the critic recommended others see the movie.',
            brief = 'Prints a random movie review to the channel.',)
async def random_movie(ctx):
  # make the api call sorted by opening date and convert to json object
  # *** the api limits calls to the 20 most recent movie reviews
  # *** and reviews that the critic favorably recommends the movie
  try:
      requestUrl = f"https://api.nytimes.com/svc/movies/v2/reviews/search.json?critics-pick=Y&opening-date=1930-01-01%3A2022-05-01&order=by-opening-date&api-key={my_apikey}"
      requestHeaders = {
    "Accept": "application/json"
      }
      response = requests.get(requestUrl, headers=requestHeaders).json()
  except requests.exceptions.HTTPError as errh:
      return "An Http Error occurred:" + repr(errh)
  except requests.exceptions.ConnectionError as errc:
      return "An Error Connecting to the API occurred:" + repr(errc)
  except requests.exceptions.Timeout as errt:
      return "A Timeout Error occurred:" + repr(errt)
  except requests.exceptions.RequestException as err:
      return "An Unknown Error occurred" + repr(err)
  
  # make a list of review headline, summary, and url
  reviewedMovies = []
  for i in response["results"]:
    reviewedMovies.append(i["headline"])
    reviewedMovies.append(i["summary_short"])
    reviewedMovies.append(i["link"]["url"])

  # chunk the review attributes into sections
  movies = [reviewedMovies[x:x+3] for x in range(0, len(reviewedMovies), 3)]
  # randomly choose a chunk
  randMovie = random.choice(movies)

  # separate the review parts by a line of whitespace
  r = "\n\n".join(randMovie)
  # bot sends moview review
  await ctx.send(r)

# keep the bot running on a server
keep_alive()

# run the bot
bot.run(my_secret)
client.run(my_secret)
