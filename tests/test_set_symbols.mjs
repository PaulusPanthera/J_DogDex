import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {setSymbol,setSymbolMarkup} from '../static/set-symbols.mjs';

test('symbols match set identity across EN/DE and never substitute an English set for JA/KO',()=>{
 const en=setSymbol({lang:'en',release:'neo1'}),de=setSymbol({lang:'de',release:'neo1'});
 assert.ok(en?.asset);assert.equal(en.asset,de.asset);
 assert.equal(setSymbol({lang:'en',release:'base1'}),null);
 assert.equal(setSymbol({lang:'de',release:'base1'}),null);
 assert.equal(setSymbol({lang:'ja',release:'neo1'}),null);
 assert.equal(setSymbol({lang:'ko',release:'neo1'}),null);
 assert.equal(setSymbol({lang:'en',release:'unknown_product'}),null);
 assert.equal(setSymbol({lang:'ja',release:'unknown',canonical_set_id:'western:neo1'}),null);
 assert.equal(setSymbol({lang:'de',release:'manual',canonical_set_id:'western:neo1'}).asset,en.asset);
 for(const lang of ['ja','ko']){const v=setSymbol({lang,release:'SV3'});assert.equal(v.kind,'identifier');assert.equal(v.code,'SV3');assert.equal(v.asset,undefined);}
});
test('symbol assets are bundled, valid, attributed and safe for a GitHub project path',()=>{
 const root=new URL('../static/set-symbols/',import.meta.url),provenance=JSON.parse(fs.readFileSync(new URL('provenance.json',root),'utf8'));
 assert.ok(Object.keys(provenance.assets).length>140);assert.ok(provenance.credits.some(c=>c.url==='https://pokesymbols.com/tcg/sets'));
 for(const row of Object.values(provenance.assets)){assert.match(row.asset,/^[a-f0-9]{20}\.webp$/);const bytes=fs.readFileSync(new URL(row.asset,root));assert.equal(bytes.subarray(0,4).toString(),'RIFF');assert.equal(bytes.subarray(8,12).toString(),'WEBP');assert.ok(row.source_url.startsWith('https://'));}
 const entry={lang:'de',release:'neo1',set_name:'Neo Genesis'},html=setSymbolMarkup(entry,String,true);
 assert.match(html,/src="\.\/set-symbols\//);assert.doesNotMatch(html,/https?:\/\//);assert.match(html,/width="22" height="18"/);assert.match(html,/aria-label="Neo Genesis set symbol"/);
 assert.equal(setSymbolMarkup({lang:'en',release:'base1'},String),'');
 assert.match(setSymbolMarkup({lang:'ja',release:'SV3'},String),/Set identifier: SV3/);
});
