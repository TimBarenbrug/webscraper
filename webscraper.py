"""
Author: Tim Barenbrug

This module was made to retrieve information from the change logs of hypernode.
It consists of two classes. The ChangeLogScraper handles the logic of going
through every change log within a two-year time frame. Each change log article
is put into a ChangeLogArticle object.
"""
import requests
import re
import json
import time
import pytz

from bs4 import BeautifulSoup
from datetime import datetime, timedelta

class ChangeLogScraper(object):
    """
    Info:
        This change log scraper was made to retrieve the average time between
        change logs and an overview of the amount of change log per author.

    Members:
        url: The main changelog page 
        date_limit: The time frame in which change logs should be taken into
            account.
    """
    def __init__(self, url):
        self.url = url
        try:
            response = requests.get(url)
            self.soup = BeautifulSoup(response.content, "html.parser")
        except Exception:
            print("No connection could be made to %s." % self.url)
        self.date_limit = datetime.now(pytz.utc) - timedelta(weeks=104)

    def retrieve_change_logs(self):
        """
        Info:
            Fills the change log list by retrieving the change log that was 
            last published and it retrieves every previous change log in a set 
            time frame starting from the moment the program is run.
        """
        change_logs = []
        change_logs.append(self.get_last_article())
        publish_date = change_logs[0].date_published 
        while publish_date > self.date_limit:
            article = self.get_previous_article(change_logs[-1])
            if article.date_published > self.date_limit:
                change_logs.append(article)
            publish_date = article.date_published
        return change_logs

    def get_previous_article(self, article):
        """
        Method was extracted for easier unit testing.
        """
        return ChangeLogArticle(article.get_previous_change_log_url())
        
    def avg_time_between_changelogs(self):
        """
        Returns:
            The average time between change log publishings.
        """
        change_logs = self.retrieve_change_logs()
        publish_dates = [changelog.date_published for changelog in\
             change_logs]
        date_deltas = [publish_dates[n - 1] - publish_dates[n] 
            for n in range(1, len(publish_dates))] 
        return sum(date_deltas, timedelta(0))/len(date_deltas)

    def change_logs_per_person(self):
        """
        Returns:
            A dictionary containing an overview of the amount of change logs 
            written per author.
        """
        change_logs = self.retrieve_change_logs()
        authors = [changelog.author for changelog in change_logs]
        overview = {}
        for author_name in list(set(authors)):
            overview[author_name] = sum([1 for author in authors if\
                 author == author_name])
        return overview

    def get_last_article(self):
        """
        Returns:
            The first href that starts with 
            "https://support.hypernode.com/changelog/".
        """
        for link in self.soup.find_all('a'):
            if "https://support.hypernode.com/changelog/" in link.get('href'):
                return ChangeLogArticle(link.get('href'))

class ChangeLogArticle(object):
    """
    Info:
        An object containing information of one change log entry.

    Members:
        url: The url of the change log entry.
        soup: The html soup of the webpage.
        title: The title of the change log entry.
        author: The author of the article.
        date_published: The date that the article was published.
    """
    def __init__(self, url):
        self.url = url
        try:
            response = requests.get(url)
            self.soup = BeautifulSoup(response.content, "html.parser")
            context = self.get_context(self.soup)
            self.title = self.soup.title.text
            try:
                self.author = context['author']['name']
                self.date_published = datetime.strptime(context['datePublished'], 
                    '%Y-%m-%dT%H:%M:%S%z')
            except KeyError:
                print("Author and Date can't be set.")
        except Exception:
            print("No connection could be made to %s." % self.url)

    def get_context(self, soup):
        """
        Returns:
            The context information of the html page as a json object.
        """
        pattern = r'\{\"@context\".*\}'
        context_string = re.findall(pattern, soup.prettify())[0]
        context_dict = json.loads(context_string)
        return context_dict

    def get_previous_change_log_url(self):
        """
        Returns:
            The href of the link with the title "Previous article".
        """
        for link in self.soup.find_all('a'):
            if link.get('title') == "Previous article":
                return link.get('href')