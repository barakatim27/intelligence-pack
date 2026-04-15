import unittest
from unittest.mock import patch

from scheduler.daily_job import run_daily_job


class DailyJobTests(unittest.TestCase):
    @patch("scheduler.daily_job.send_email_digest")
    @patch("scheduler.daily_job.build_digest", return_value="digest")
    @patch("scheduler.daily_job.rank_articles", return_value=[{"title": "x"}])
    @patch("scheduler.daily_job.parse_article", side_effect=lambda article: article)
    @patch(
        "scheduler.daily_job.collect_news",
        side_effect=[
            [{"title": "Tech", "link": "https://a", "category": "tech"}],
            [{"title": "Finance", "link": "https://b", "category": "finance"}],
            [{"title": "Geo", "link": "https://c", "category": "geo"}],
        ],
    )
    def test_run_daily_job_sends_digest_when_articles_exist(
        self,
        _collect_news,
        _parse_article,
        _rank_articles,
        _build_digest,
        send_email_digest_mock,
    ) -> None:
        result = run_daily_job()
        self.assertTrue(result)
        send_email_digest_mock.assert_called_once_with("digest")

    @patch("scheduler.daily_job.send_email_digest")
    @patch("scheduler.daily_job.parse_article", side_effect=lambda article: article)
    @patch("scheduler.daily_job.collect_news", side_effect=[[], [], []])
    def test_run_daily_job_skips_email_when_no_articles(
        self,
        _collect_news,
        _parse_article,
        send_email_digest_mock,
    ) -> None:
        result = run_daily_job()
        self.assertFalse(result)
        send_email_digest_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
