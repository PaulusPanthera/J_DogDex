"""Current data contract, kept separate from historical audit boundaries."""
import collections
import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from catalog_history import catalog_at, read
from dogdex.collector import Collection
from dogdex.printing_model import physical_key
from tools.audit_catalog import digest
ROOT=Path(__file__).resolve().parents[1]

class ReleaseContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=read('data/catalog.json')

    def test_current_1819_catalogue_contract(self):
        c=self.c
        self.assertEqual(c['revision'],'1.8.19')
        self.assertEqual((len(c['roster']),len(c['entries'])),(41,3832))
        self.assertEqual(c['statistics']['printings'],4615)
        self.assertEqual(len({e['id'] for e in c['entries']}),3832)
        pids=[p['id'] for e in c['entries'] for p in e['printings']]
        self.assertEqual((len(pids),len(set(pids))),(4615,4615))
        self.assertEqual(collections.Counter(e['lang'] for e in c['entries']),dict(en=1011,de=960,ja=1059,ko=802))
        for e in c['entries']:
            keys=[physical_key(e['id'],p) for p in e['printings']]
            self.assertEqual(len(keys),len(set(keys)),e['id'])
        with tempfile.TemporaryDirectory() as user:
            entries=Collection(ROOT,user).entries().values()
            counts=collections.Counter(e['lang'] for e in entries for p in e['printings'])
            self.assertEqual(counts,dict(en=1757,de=1471,ja=847,ko=530))
            self.assertEqual(sum(counts.values()),4605)
        with sqlite3.connect((ROOT/'data/catalog-collector.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM printings').fetchone()[0],4615)
            self.assertEqual(db.execute('PRAGMA quick_check').fetchone()[0],'ok')
        self.assertEqual(hashlib.sha256((ROOT/'data/catalog.sqlite3').read_bytes()).hexdigest(),'e79d48ff8d056d88fa0d6b1f0771f220d79f62d82797c886183e20ada9c22da0')

    def test_historical_replays_match_independent_golden_hashes(self):
        for version,path in [('1.7','printing_184/baseline_183.json'),('1.8.4','printing_186/baseline_185.json')]:
            with self.subTest(version=version):
                c=catalog_at(version);gold=read('data/research/'+path)
                self.assertEqual({e['id']:digest(e) for e in c['entries']},gold['entry_hashes'])
        c={e['id']:e for e in catalog_at('1.8.9')['entries']}
        for e in read('data/research/corrections_1812/before_records.json')['entries']:
            self.assertEqual(digest(c[e['id']]),digest(e),e['id'])

    def test_history_copy_cannot_mutate_another_test_fixture(self):
        a=catalog_at('1.8.4');before=digest(a['entries'][0]);a['entries'][0]['name']='Isolated change'
        self.assertEqual(digest(catalog_at('1.8.4')['entries'][0]),before)

if __name__=='__main__':unittest.main()
