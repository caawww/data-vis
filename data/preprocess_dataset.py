import pandas as pd

columns = [
    'AppID', 'Name', 'Release date', 'Estimated owners', 'Peak CCU', 'Required age', 'Price',
    'Discount', 'DLC count', 'About the game', 'Supported languages', 'Full audio languages', 'Reviews',
    'Header image', 'Website', 'Support url', 'Support email', 'Windows', 'Mac', 'Linux', 'Metacritic score',
    'Metacritic url', 'User score', 'Positive', 'Negative', 'Score rank', 'Achievements', 'Recommendations',
    'Notes', 'Average playtime forever', 'Average playtime two weeks', 'Median playtime forever',
    'Median playtime two weeks', 'Developers', 'Publishers', 'Categories', 'Genres', 'Tags', 'Screenshots',
    'Movies'
]

df = pd.read_csv(
    'games_original.csv',
    sep=',',  # columns are comma-separated
    quotechar='"',  # respect quotes around text
    names=columns,
    skiprows=1,
)

keep_columns = list([
    'AppID',
    'Name',
    'Release date',
    'Estimated owners',
    'Peak CCU',
    'Required age',
    'Price',
    'Discount',
    'DLC count',
    # 'About the game',
    'Supported languages',
    'Full audio languages',
    # 'Reviews',
    # 'Header image',
    # 'Website',
    # 'Support url',
    # 'Support email',
    'Windows',
    'Mac',
    'Linux',
    'Metacritic score',
    # 'Metacritic url',
    'User score',
    'Positive',
    'Negative',
    'Score rank',
    'Achievements',
    'Recommendations',
    # 'Notes',
    'Average playtime forever',
    'Average playtime two weeks',
    'Median playtime forever',
    'Median playtime two weeks',
    'Developers',
    'Publishers',
    'Categories',
    'Genres',
    'Tags',
    # 'Screenshots',
    # 'Movies',
])

df = df[keep_columns]

df.to_csv("games.csv", index=False)
