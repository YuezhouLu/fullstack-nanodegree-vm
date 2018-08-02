# "Database code" for the DB Forum.

# import datetime

# POSTS = [("This is the first post.", datetime.datetime.now())]

import psycopg2

import bleach

DBNAME = "forum"

def get_posts():
  """Return all posts from the 'database', most recent first."""
  # return reversed(POSTS)
  db = psycopg2.connect(database = DBNAME)
  c = db.cursor()
  query = "select content, time from posts order by time desc"
  c.execute(query)
  return c.fetchall()
  db.close()

def add_post(content):
  """Add a post to the 'database' with the current timestamp."""
  # POSTS.append((content, datetime.datetime.now()))
  db = psycopg2.connect(database = DBNAME)
  c = db.cursor()
  c.execute("insert into posts values (%s)", (bleach.clean(content),)) # we put a Python tuple parameter here, therefore with a comma
  db.commit()
  db.close()