"""
This file contains the unit tests for the webscraper.
"""
import unittest
import pytz
import json

from unittest import mock 
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
 
from webscraper import ChangeLogArticle, ChangeLogScraper

class TestChangeLogScraper(unittest.TestCase):

    def setUp(self):
        self.scraper = ChangeLogScraper("")
        self.scraper.date_limit = datetime.now(pytz.utc) - timedelta(weeks=4)

    def mock_get_article(self, td=0):
       cl_article = mock.Mock() 
       cl_article.date_published = datetime.now(pytz.utc) - timedelta(weeks=td) 
       return cl_article

    def mock_get_previous_change_log_url(self, td=0):
        cl_article = mock.Mock()
        cl_article.date_published = datetime.now(pytz.utc) - timedelta(weeks=td)
        print(cl_article.date_published)
        return cl_article

    def mock_retrieve_change_logs(self):
        cl_article1 = mock.Mock()
        cl_article1.date_published = datetime.now(pytz.utc) - timedelta(weeks=2)
        cl_article1.author = "Kim"

        cl_article2 = mock.Mock()
        cl_article2.date_published = datetime.now(pytz.utc) - timedelta(weeks=3)
        cl_article2.author = "Tim"
        return [cl_article1, cl_article2]

    def test_retrieve_change_logs(self):
        with mock.patch.object(ChangeLogScraper, 'get_previous_article', 
            side_effect=[self.mock_get_article(td=5), self.mock_get_article()]):
            with mock.patch.object(ChangeLogScraper, 'get_last_article', return_value=self.mock_get_article()):
                    change_logs = self.scraper.retrieve_change_logs()
                    self.assertEqual(len(change_logs), 1)
    
    def test_avg_time_between_change_logs(self):
        with mock.patch.object(ChangeLogScraper, 'retrieve_change_logs', return_value=self.mock_retrieve_change_logs()):
            td_result = self.scraper.avg_time_between_changelogs()
            #The initial difference was less than 7 days so 6 whole days
            self.assertAlmostEqual(td_result.days, 6)

    def test_change_logs_per_person(self):
        with mock.patch.object(ChangeLogScraper, 'retrieve_change_logs', return_value=self.mock_retrieve_change_logs()):
            result = self.scraper.change_logs_per_person()
            self.assertDictEqual(result, {"Tim": 1, "Kim": 1})

    def test_get_last_article(self):
        with open('main_page_change_log.html') as htmldoc:
            soup = BeautifulSoup(htmldoc, 'html.parser')
        self.scraper.soup = soup
        url = self.scraper.get_last_article().url
        self.assertEqual(url, "https://support.hypernode.com/changelog/" + 
            "release-6249-larger-tmp_table_size-and-max_heap-if-tmp_on_data" + 
            "-option-enabled/")

class TestChangeLogArticle(unittest.TestCase):
    def setUp(self):
        self.article = ChangeLogArticle("")

    def test_get_context(self):
        with open('first_article_change_log.html') as htmldoc:
            soup = BeautifulSoup(htmldoc, 'html.parser')
        context = self.article.get_context(soup)
        with open("context.txt") as string:
            real_context = json.load(string)
        self.assertDictEqual(context, real_context)

    def test_get_previous_change_article(self):
        with open('first_article_change_log.html') as htmldoc:
            soup = BeautifulSoup(htmldoc, 'html.parser')
        self.article.soup = soup
        previous_cl_url = self.article.get_previous_change_log_url()
        self.assertEqual(previous_cl_url, 
            "https://support.hypernode.com/changelog/release-6242-additional-" + 
            "automated-problem-diagnostic-emails/"
        )

if __name__ == '__main__':
    unittest.main()