# Easy to use Telegram Airdrop Bot

This bot has all you need and very simple to use!
### Some of the great futures

- Ask user to follow twitter and join telegram groups, multipe groups and twitter links are supported.
- Checks if the wallet address is correct.
- Very easy to use.
- Persistance, the chat will remain persistant even if you restart the bot.
- Blocks duplicate wallets
- Blocks duplicate twitter usernames

## Usage
- [Edit the .env.example file](#env-file)
- Run `cp .env.example .env`
- Run `docker-compose up -d`
- That's all!

## Env file
### Important (must be edited)

- `COIN_SYMBOL` Is the coin symbol
    - Example: `BNB, ETH`
- `COIN_NAME` Is the coin name
    - Example: `Bitcoin, Ethereum`
- `AIRDROP_AMOUNT` How many tokens are you going to give
    - Example: `10,000`
- `AIRDROP_DATE` Date of reward distrubition
    - Example: `20 July 2021`
- `BOT_TOKEN` The token you get from @BotFather
    - Example: `1313552295:AAFxDGKhlco-FoWw-uyxInotlKvalidNEz-Q`
- `COIN_PRICE` Current price of coin
    - Example: `$0.01`
- `REFERRAL_REWARD` Extra reward users will get for each referral
    - Example: `1000`
- `WEBSITE_URL` Your website url
    - Example: `https://bitcoin.com`
- `TWITTER_LINKS` Twitter page links seperated by comma
    - Example: `https://twitter.com/bitcoin,`
    - Example: `https://twitter.com/bitcoin,https://twitter.com/ethereum`
- `TELEGRAM_LINKS` Telegram group links seperated by comma
    - Example: `https://t.me/single,`
    - Example: `https://t.me/multi,https://t.me/ple`


### Not Important (can be set to anything)

- `MONGO_INITDB_ROOT_USERNAME` Mongodb username
- `MONGO_INITDB_ROOT_USERNAME` Mongodb password 

## TODO

- [ ] Make Telegram & Twitter follow optional
- [ ] Admin dashboard