"""A review archive must include committed WAL rows and omit generated copies."""
import importlib.util,json,sqlite3,sys,tempfile,unittest,zipfile
from contextlib import closing
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
class ReviewZipTests(unittest.TestCase):
    def test_coherent_snapshot_and_curated_scope(self):
        spec=importlib.util.spec_from_file_location('review_zip',ROOT/'tools/create_review_zip.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)/'DogDex';(root/'my_collection').mkdir(parents=True);(root/'my_collection/catalog_images').mkdir();(root/'my_collection/backups').mkdir();(root/'dogdex').mkdir();(root/'static').mkdir();(root/'data').mkdir();(root/'docs').mkdir();(root/'runtime').mkdir();(root/'__pycache__').mkdir()
            (root/'tests/node_modules/example').mkdir(parents=True)
            for name in ('tests/node_modules/example/package.json','app.py','dogdex/example.py','static/example.css','data/example.json','my_collection/catalog_images/picture.jpg','my_collection/backups/old.sqlite3','runtime/python.exe','docs/snapshot.json','__pycache__/old.pyc'): (root/name).write_text('fixture',encoding='utf-8')
            db=sqlite3.connect(root/'my_collection/collection.sqlite3');db.execute('PRAGMA journal_mode=WAL');db.execute('CREATE TABLE copies(id TEXT, price_minor INTEGER, notes TEXT)');db.execute("INSERT INTO copies VALUES('one',425,'keep purchase note')");db.commit()
            output=Path(t)/'review.zip'
            real_connect=sqlite3.connect;opened=[]
            def track(*args,**kwargs):
                connection=real_connect(*args,**kwargs);opened.append(connection);return connection
            with patch.object(m,'ROOT',root),patch.object(sys,'argv',['review','--output',str(output)]),patch.object(m.sqlite3,'connect',side_effect=track):m.main()
            self.assertEqual(len(opened),2)
            for connection in opened:
                with self.assertRaises(sqlite3.ProgrammingError):connection.execute('SELECT 1')
            with zipfile.ZipFile(output) as z:
                names=set(z.namelist());self.assertIn('DogDex/dogdex/example.py',names);self.assertIn('DogDex/my_collection/catalog_images/picture.jpg',names)
                self.assertFalse(any('/runtime/' in n or '/docs/' in n or '/backups/' in n or '__pycache__' in n or '/node_modules/' in n or n.endswith(('-wal','-shm')) for n in names));saved=Path(t)/'saved.sqlite3';saved.write_bytes(z.read('DogDex/my_collection/collection.sqlite3'))
            with closing(sqlite3.connect(saved)) as check:self.assertEqual(check.execute('SELECT * FROM copies').fetchone(),('one',425,'keep purchase note'))
            db.close()
if __name__=='__main__':unittest.main()
