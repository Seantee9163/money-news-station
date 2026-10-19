from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import fetch_daily_news as news
from scripts.news_analysis import analyze, validate_payload

FIXTURE = Path(__file__).resolve().parent / 'fixtures' / 'bbc-2026-10-18.xml'


def real_candidates():
    out = []
    for title, link, desc, date, source in news.parse_items(FIXTURE.read_bytes(), 'BBC'):
        dt = news.parse_date(date)
        out.append(dict(original_title=title, original_desc=desc,
                        source_url=link, source_name=source,
                        category=news.detect_category(title + ' ' + desc)[0],
                        date=dt.date().isoformat(), published_at=dt.isoformat(),
                        published_raw=date,
                        feed_url='https://feeds.bbci.co.uk/news/business/rss.xml'))
    return out


class FrozenDatetime(datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(2026, 10, 19, 12, tzinfo=timezone.utc)


class PipelineTests(unittest.TestCase):
    def setUp(self):
        mock = patch.object(news, 'datetime', FrozenDatetime)
        mock.start()
        self.addCleanup(mock.stop)

    def test_real_articles_have_distinct_supported_analysis(self):
        with patch.object(news, 'request_bytes', side_effect=AssertionError('No network')):
            data = [news.localize_item(c) for c in real_candidates()]
        validate_payload(data)
        self.assertEqual([x['analysis']['rule_id'] for x in data],
                         ['ai_impersonation', 'data_centre_withdrawal', 'tidal_prototype'])
        for field in ('opportunity', 'risk', 'why_it_matters'):
            # Removing the title anchor must still leave distinct substantive analysis.
            self.assertEqual(len({x[field].split('》：', 1)[1] for x in data}), 3)
        self.assertIn('回拨', data[0]['opportunity'])
        self.assertIn('不等于整个项目取消', data[1]['risk'])
        self.assertIn('研发者的说法', data[2]['risk'])
        self.assertNotIn('超级收费', data[0]['summary'])
        self.assertNotIn('网站', data[1]['summary'])
        self.assertTrue(all(x['translation_status'] == 'reviewed' for x in data))
        self.assertTrue(all(x['date'] == '2026-10-18' for x in data))
        self.assertEqual(data[0]['published_at'], '2026-10-18T23:24:59+00:00')
        self.assertEqual(data[1]['source_url'], real_candidates()[1]['source_url'])

    def test_unknown_or_negated_event_abstains(self):
        for title, desc in [('AI news', ''),
                            ('Company denies it will withdraw from data centre', ''),
                            ('Company may withdraw from data centre', ''),
                            ('AI scams', 'A new data centre opens.')]:
            c = dict(original_title=title, original_desc=desc, source_url='https://www.bbc.com/news/a')
            self.assertEqual(analyze(c, '待核实消息')['metadata']['status'], 'insufficient_evidence')

    def test_category_cannot_change_analysis(self):
        c = real_candidates()[0]
        first = analyze(c, '诈骗消息')
        c['category'] = '赚钱机会'
        self.assertEqual(first, analyze(c, '诈骗消息'))

    def test_dates_and_atom_published(self):
        self.assertIsNone(news.parse_date('invalid'))
        self.assertIsNone(news.parse_date(''))
        self.assertIsNone(news.parse_date('2026-10-18'))
        xml = b'''<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>AI</title>
        <link rel="self" href="bad"/><link rel="alternate" href="https://www.bbc.com/a"/>
        <published>2026-10-18T08:00:00Z</published><updated>2026-10-19T08:00:00Z</updated>
        </entry></feed>'''
        result = news.parse_items(xml, 'BBC')[0]
        self.assertEqual(result[1], 'https://www.bbc.com/a')
        self.assertEqual(result[3], '2026-10-18T08:00:00Z')
        self.assertEqual(news.parse_items(xml.replace(b'published', b'unknown'), 'BBC')[0][3], '')

    def test_bad_feed_does_not_abort_other_feeds(self):
        with patch.object(news, 'request_bytes', side_effect=[b'broken', FIXTURE.read_bytes(), b'broken']):
            items = news.build_candidates()
        self.assertGreaterEqual(len(items), 2)

    def test_invalid_future_stale_dates_and_links_are_rejected(self):
        for date, link in [('bad', 'https://www.bbc.co.uk/a'),
                           ('Sun, 18 Oct 2099 00:00:00 GMT', 'https://www.bbc.co.uk/a'),
                           ('Sun, 18 Oct 2000 00:00:00 GMT', 'https://www.bbc.co.uk/a'),
                           ('Sun, 18 Oct 2026 00:00:00 GMT', 'javascript:alert(1)')]:
            xml = f'<rss><channel><item><title>AI automation</title><link>{link}</link><pubDate>{date}</pubDate></item></channel></rss>'.encode()
            with patch.object(news, 'request_bytes', return_value=xml):
                self.assertEqual(news.build_candidates(), [])

    def test_translation_failure_preserves_existing_data(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'news-data.json'
            target.write_text('["existing"]')
            import os
            previous = os.getcwd()
            try:
                os.chdir(directory)
                with patch.object(news, 'build_candidates', return_value=real_candidates()), \
                     patch.object(news, 'localize_item', side_effect=RuntimeError('translation unavailable')):
                    with self.assertRaises(SystemExit):
                        news.main()
                self.assertEqual(target.read_text(), '["existing"]')
            finally:
                os.chdir(previous)

    def test_truncation_and_tampered_evidence_fail(self):
        with self.assertRaises(ValueError):
            news.translate_mymemory('a' * 451)
        data = [news.localize_item(c) for c in real_candidates()]
        data[0]['analysis']['evidence'][0]['quote'] = 'invented'
        with self.assertRaises(ValueError):
            validate_payload(data)

    def test_success_writes_valid_json(self):
        import os
        with tempfile.TemporaryDirectory() as directory:
            previous = os.getcwd()
            try:
                os.chdir(directory)
                with patch.object(news, 'build_candidates', return_value=real_candidates()):
                    news.main()
                validate_payload(json.loads(Path('news-data.json').read_text()))
                self.assertFalse(Path('news-data.json.tmp').exists())
            finally:
                os.chdir(previous)


if __name__ == '__main__':
    unittest.main()
