# import reddit api wrapper
import praw
import pandas as pd
import numpy as np

# access password and client secret id via local files
with open('_functions/pw.txt', 'r') as file1:
    pw = file1.read()

with open('_functions/client_secret.txt', 'r') as file2:
    cs = file2.read()

# create a praw Reddit instance with app credentials and secret info passed through
reddit = praw.Reddit(
    client_id="XbesrQBvKymjgLdgg_D6lA",
    client_secret=cs,
    user_agent="NFLTextAnalysis/0.0.1",
    username="ta_api",
    password=pw
)

### SUBMISSION FUNCTIONS ###

def get_submissions(subreddit:str, time_filter:str, limit:int) -> pd.DataFrame:
    """ 
    Takes a subreddit name and how many of the last month's most popular posts to return as a dataframe.

    Returns the title, whether the submission is a self-post or external link, the body of the submission (in html),
    the url (to the external link, if not a self-post, otherwise, to the reddit submission itself),
    the number of upvotes, and the ratio of upvotes to downvotes.
    """
    
    # for each submission returned from the subreddit's top month query, gather neccessary meta-data features
    submission_data = [(submission.id,
                            submission.title,
                            submission.created_utc,
                            submission.is_self,
                            submission.selftext,
                            submission.url,
                            submission.ups,
                            submission.upvote_ratio,
                            submission.num_comments) 
                            for submission in reddit.subreddit(subreddit).top(time_filter=time_filter, limit=limit)]
    
    # save and return dataframe of submission data
    submission_df = pd.DataFrame(submission_data, columns=['submission_id', 'title', 'created_utc', 'is_self', 'selftext',
                                                           'url', 'ups', 'upvote_ratio', 'num_comments'])

    return submission_df


### COMMENT FUNCTIONS ### 


def get_comments(reddit: praw.Reddit, submission_id: str) -> pd.DataFrame:
    '''
    Returned dataframe includes the comment's author, content, upvotes, downvotes, created time, and author's flair,
    as well as the comment's polarity and subjectivity.

    Parameters
    --- --- --- 
    reddit: praw.Reddit instance
        The pre-created reddit instance set up by user. Only read rights required.

    submission_id: string
        The unique id associated with the reddit thread of interest. Gain by accessed by the reddit API or extracted from the thread's permalink.
    '''
    print("Submission ID: " + submission_id)

    # create a praw.Submission object based on the subject_id to access comments
    submission = reddit.submission(submission_id)
    
    # ignore all of the "Load More Comment" prompts to return entire comment tree
    submission.comments.replace_more(limit=None)

    print("Comments: " + str(len(submission.comments.list())))

    comment_list = [(comment.id, 
                      submission_id,
                      str(comment.author), 
                      str(comment.body), 
                      int(comment.ups), 
                      comment.created_utc, 
                      comment.author_flair_text) for comment in submission.comments.list()]

    print("Comments stored.")

    comment_df = pd.DataFrame(comment_list, columns=['comment_id', 'submission_id', 'author', 'body', 'upvotes', 
                                                         'utc_time', 'author_flair'])

    return comment_df