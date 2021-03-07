"""
Makes a xkcd style header for the blog that has the number of days since posting.
"""
import os
import datetime as dt
import re
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np


def date_match(date_str: str):
    """Regex match to the date.

    Args:
        date_str (str): The string that might contain a date.

    Returns:
        re.match: Regex match object
    """
    return re.match(r'\d{4}-\d{2}-\d{2}', date_str)


def list_posts(post_path: str = '_posts/'):
    """Lists the blog posts in the given path.

    Args:
        post_path (str, optional): Path to blog posts. Defaults to '_posts/'.

    Returns:
        list: List of the blog posts
    """
    post_list = os.listdir(post_path)
    return [post for post in post_list if date_match(post)]


def extract_dates(post_list: list):
    """

    Args:
        post_list (list): list of posts

    Returns:
        list: list of dt.datetime objects as infered for the blog posts
    """
    dts = [dt.datetime.strptime(date_match(post).group(), '%Y-%m-%d') for post in post_list]
    return dts


def timedelta_dates(date_list: list, compare_date=dt.datetime.today()):
    """Returns the difference in days between the date and the given compare date.

    Args:
        date_list (list): list of dates
        compare_date ([dt.datetime, optional): Date to compare to. Defaults to dt.datetime.today().

    Returns:
        list: Lists of ints, which represent the difference of each date
    """
    deltas = [(date - compare_date).days for date in date_list]
    return deltas


def extract_titles(post_list: list):
    """Given a list of post extract the titles.

    Args:
        post_list (list): list of post filenames

    Returns:
        list: list of post titles
    """
    post_titles = [extract_title(post=post) for post in post_list]
    return post_titles


def extract_title(post: str, base_dir='_posts/'):
    """Given a post.md will read the first few lines to get the title.

    Args:
        post (str): post MD filename
        base_dir (str, optional): Where the posts are stored. Defaults to '_posts/'.

    Returns:
        str: The post title
    """
    with open(os.path.join(base_dir, post), 'r') as f:
        line = f.readline()
        cnt = 0
        while line:
            if 'title:' in line or cnt > 10:
                break
            cnt += 1
            line = f.readline()
    if 'title:' not in line:
        line = 'UH OH!'

    return re.sub('title: ', '', line.strip())


def filter_titles(post_titles: list, deltas: list, cutoff=-30):
    """Filter titles to the ones in certain timeframe as given by cutoff

    Args:
        post_titles (list): The list of post titles
        deltas (list): The list of timedeltas
        cutoff (int, optional): How many days into past for title to be valid. Defaults to -30.

    Returns:
        tuple: filtered_titles, filtered_deltas
    """
    filtered_titles, filtered_deltas = [], []
    for title, delta in zip(post_titles, deltas):
        if delta > cutoff:
            filtered_titles.append(title)
            filtered_deltas.append(delta + 1)
    sorted_pairs = sorted(zip(filtered_titles, filtered_deltas), key=lambda x: x[1])
    tuples = zip(*sorted_pairs)
    filtered_titles, filtered_deltas = [list(tup) for tup in tuples]
    return filtered_titles, filtered_deltas


def line_plot(post_titles: list, deltas: list, cutoff=-30):
    """Creates the line plot in the XKCD style.

    Args:
        post_titles (list): list of post titles
        deltas (list): list of time since comparison time
        cutoff (int, optional): cutoff point. Defaults to -30.

    Returns:
        tuple : plt.fig, plt.ax
    """
    with plt.xkcd():
        f, ax = plt.subplots(1, 1)
        x_vals = [i for i in range(cutoff, 0, 1)]
        y_counts = Counter(deltas)
        y_vals = [y_counts[x] for x in x_vals]
        ax.plot(x_vals, y_vals)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_title('WELCOME TO THE BLOG!', fontweight='bold', y=1.05)
        max_y_val = max(y_vals)
        ax.set_ylim(top=max_y_val+0.3+0.2*len(y_counts))
        ax.set_yticks(range(0, max_y_val+1))
        ax.set_xlabel('Days ago...')
        ax.set_ylabel('Number of posts')

        arrowprops = dict(
                        arrowstyle="->",
                        connectionstyle="angle3,angleA=0,angleB=90")
        titles_arr = np.array(post_titles)
        deltas_arr = np.array(deltas)
        x_offset = 2
        y_offset = max_y_val + 0.2*len(y_counts) + 0.2
        for x, count in y_counts.items():
            post_titles = titles_arr[deltas_arr == x]
            ax.annotate('\n+\n'.join(post_titles), xy=(x, count),
                        xytext=(x+x_offset, y_offset),
                        arrowprops=arrowprops)
            y_offset -= 0.2

        ax.text(x=1.2, y=0.6, s='Days since posting...',
                transform=ax.transAxes)
        bbox_props = dict(boxstyle="round", fc="white", ec="black")
        if len(deltas) > 0:
            last_post_days = str(abs(deltas[-1]))
        else:
            last_post_days = '+' + str(abs(cutoff))
        ax.text(1.3, 0.4, last_post_days, bbox=bbox_props, transform=ax.transAxes,
                fontsize=24)
        exclam = '"Nice!"' if int(last_post_days) < 14 else '"UH OH!"'
        ax.text(1.28, 0.1, exclam, transform=ax.transAxes, rotation=25)
        f.set_size_inches(12, 2.5)
        return f, ax


if __name__ == "__main__":
    posts = list_posts()
    print(f'{len(posts)} Posts found!')
    dates = extract_dates(post_list=posts)
    timedeltas = timedelta_dates(date_list=dates)
    titles = extract_titles(post_list=posts)
    titles, timedeltas = filter_titles(post_titles=titles, deltas=timedeltas)
    print(f'{len(titles)} Posts after filtering')
    print('Making plot...')
    f, ax = line_plot(post_titles=np.array(titles), deltas=np.array(timedeltas))
    print('Saving plot...')
    f.savefig('images/header.png', bbox_inches='tight')
    print('Done')
