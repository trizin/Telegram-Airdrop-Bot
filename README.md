# Telegram Airdrop Bot

This bot has all you need and very simple to use!
### Some of the great futures

- Ask user to follow twitter and join telegram groups, multipe groups and twitter links are supported.
- Check if a correct wallet address has been provided
- Very easy to use.
- Persistance, the chat will remain persistant even if you restart the bot.
- Blocks duplicate wallets & twitter usernames
- Refferal support
- Start, stop, pause airdrop anytime.
- Captcha support

### Admin Commands

- `/list` Returns the list of all participants in json format.
- `/stats` Returns number of participants, referrals, distribution amounts
- `/bot stop|pause|start` Manage airdrop status; stop, pause or start.

## Installation with Docker
- [Edit the .env.example file](#env-file)
- Run `cp .env.example .env`
- Run `docker-compose up -d`
- That's all!

## Env Variables
### Important

- `COIN_SYMBOL` Is the coin symbol
    - Example: `BNB, ETH`
- `COIN_NAME` Is the coin name
    - Example: `Bitcoin, Ethereum`
- `AIRDROP_AMOUNT` How many tokens are you going to give
    - Example: `10000` *do not* include "," must be float number
- `AIRDROP_DATE` Date of reward distrubition
    - Example: `20 July 2021`
- `BOT_TOKEN` The token you get from @BotFather
    - Example: `1313552295:AAFxDGKhlco-FoWw-uyxInotlKvalidNEz-Q`
- `COIN_PRICE` Current price of coin
    - Example: `$0.01`
- `REFERRAL_REWARD` Extra reward participants will get for each referral
    - Example: `1000`
- `WEBSITE_URL` Your website url
    - Example: `https://bitcoin.com`
- `EXPLORER_URL` Blockchain explorer url
    - Example: `https://etherscan.io/address/0x0000000000000000000000000000000000000000`
- `ADMIN_USERNAME` Your telegram username
    - Example: `johnboe`
- `MAX_USERS` Maximum number of participants
    - Example: `1000` *do not* include "," must be float number
- `MAX_REFS` Maximum number of referrals per participant
    - Example: `5`
- `CAPTCHA_ENABLED` Enable or disable captcha at start
    - Example: `YES` or `NO`
- `TWITTER_LINKS` Twitter page links seperated by comma
    - Example: `https://twitter.com/bitcoin,`
    - Example: `https://twitter.com/bitcoin,https://twitter.com/ethereum`
- `TELEGRAM_LINKS` Telegram group links seperated by comma
    - Example: `https://t.me/single,`
    - Example: `https://t.me/multi,https://t.me/ple`


### Not Very Important

Leave these to default unless you know what you do.

- `MONGO_INITDB_ROOT_USERNAME` Mongodb username
- `MONGO_INITDB_ROOT_USERNAME` Mongodb password
- `MONGO_INITDB_IP` Mongodb IP
- `MONGO_INITDB_PORT` Mongodb Port

## Some Screenshots
![1](./images/1.jpg)
![1](./images/2.jpg)
