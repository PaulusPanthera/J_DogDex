"""Maintenance commands remain safe to inspect and never include private data in Git."""
import hashlib
import importlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from tools.check_project import check
ROOT=Path(__file__).resolve().parents[1]

def hashes(root):
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}

class MaintenanceTests(unittest.TestCase):
    def test_maintenance_imports_and_help_do_not_rewrite_catalogue_or_evidence(self):
        before=hashes(ROOT/'data')
        for name in ['audit_catalog','reconcile_catalog','reconciliation_audit','completion_audit','asia_audit','source_structure_build','create_review_zip','package','build_index','check_project','install_update']:
            with self.subTest(command=name):
                importlib.import_module('tools.'+name)
                result=subprocess.run([sys.executable,str(ROOT/'tools'/f'{name}.py'),'--help'],capture_output=True,text=True,encoding='utf-8',timeout=30)
                self.assertEqual(result.returncode,0,result.stderr);self.assertIn('usage:',result.stdout.lower())
        self.assertEqual(hashes(ROOT/'data'),before)

    @unittest.skipUnless(shutil.which('git'),'Git is needed to test the publication allowlist')
    def test_git_allowlist_excludes_personal_files_and_includes_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);shutil.copyfile(ROOT/'.gitignore',root/'.gitignore')
            subprocess.run(['git','init','-q',str(root)],check=True,capture_output=True)
            public=['app.py','dogdex/collector.py','tools/check_project.py','static/app.js','data/catalog.json','data/catalog.sqlite3','data/images/reference.webp','data/research/facts.json','tests/test_collector.py','tests/package-lock.json','project_notes/UPDATE_1_8_18.md','docs/snapshot.json','.github/workflows/checks.yml','DEVELOPMENT.md','CHECK_DOGDEX.bat','.gitattributes']
            private=['my_collection/collection.sqlite3','my_collection/photos/card.jpg','my_collection/catalog_images/card.webp','my_collection/checks/latest.json','DogDex_Review.zip','unknown_personal_notes.txt','runtime/python.exe','data/catalog-collector.sqlite3','data/collection.sqlite3','data/research/.env','data/research/collection.sqlite3','project_notes/previous_layout/editor.py','project_notes/DogDex_Collection_Audit_private.md','tests/node_modules/jsdom/package.json','dogdex/__pycache__/app.pyc','.github/unknown.yml']
            for name in public+private:
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.touch()
            for name in public+private:
                result=subprocess.run(['git','check-ignore','--no-index','-q',name],cwd=root)
                self.assertEqual(result.returncode,1 if name in public else 0,name)

    def test_diagnostics_are_read_only_and_detect_a_damaged_catalogue(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'data').mkdir()
            (root/'data/catalog.json').write_text('{broken',encoding='utf-8')
            before=hashes(root);report=check(root)
            self.assertFalse(report['ok']);self.assertEqual(hashes(root),before)
            self.assertFalse((root/'my_collection').exists())
            self.assertTrue(any(r['name']=='catalogue' and not r['ok'] for r in report['checks']))

if __name__=='__main__':unittest.main()
