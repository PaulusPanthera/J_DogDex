"""Rebuild only the derived SQLite index from the current reviewed JSON."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from dogdex.catalog_enrich import make_sqlite
ROOT=Path(__file__).resolve().parents[1]
def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    catalog=json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'))
    make_sqlite(catalog)
    print('Rebuilt data/catalog-collector.sqlite3 from catalogue '+catalog['revision'])
if __name__=='__main__':main()
