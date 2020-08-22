import constants
from user import User
from database import Database
from twitter_utils import get_authorization, checkInternetSocket, check_dir_exists

checkInternetSocket()
User.create_table()
check_dir_exists()

# username = input('Enter your username to log in ')
username = 'shadow77'
user = User.load_data_by_username(username)

if not user:

    access_token, access_token_secret = get_authorization()
    user = User(username, access_token, access_token_secret)
    user.save_user_to_db()

else:
    print('User already exists')
#ESPNFC
# Football_TaIk

# lst = ['Football_TaIk', 'ESPNFC']
# for a in lst:
#     user.get_tweets(a, hrs=5, time_delay=10)

user.get_tweets('harshit_778', hrs=15, time_delay=2)
