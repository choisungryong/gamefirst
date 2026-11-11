import hashlib, json, tempfile, unittest
from pathlib import Path
import catalog, server

class BackendTests(unittest.TestCase):
    def test_catalog(self):
        c=catalog.generate()
        self.assertIn(c['coverage']['runtime_files'],[163,166])
        self.assertTrue(catalog.UI38_FILES.issubset({f['path'] for f in c['files']}))
        self.assertEqual(c['build']['preserved_builds'][0]['runtime_file_count'],163)
        self.assertEqual(len(c['tasks']),40)
        self.assertEqual(c['coverage']['semantic_counts']['audio_variants'],19)
        self.assertEqual(len([e for e in c['entities'] if e['type']=='bases']),12)
        self.assertEqual(len({e['id'] for e in c['entities']}),len(c['entities']))
        self.assertEqual(c['coverage']['runtime_extensions']['.gd'],77+(3 if c['coverage']['runtime_files']==166 else 0))
        self.assertEqual({k:c['coverage']['categories'][k] for k in ['equipment','skills','enemies','characters','balance','ui']},{'equipment':12,'skills':3,'enemies':4,'characters':1,'balance':17,'ui':6})
        self.assertTrue(all(e['category']=='implementation' for e in c['entities'] if e['type'] in ['presenter_class','implementation']))
        self.assertTrue(all(e['assets'][0].endswith('.glb') for e in c['entities'] if e['type']=='actor_role'))
        self.assertTrue(any(e['attributes'].get('skins') for e in c['entities'] if e['type']=='glb'))
    def test_verified38_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=root/'package38';folder.mkdir()
            paths=sorted(catalog.UI38_FILES)+['source/%d.gd'%i for i in range(163)]
            for p in paths:
                target=root/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_text('source')
            exe=root/'builds/chapter1/test.exe';exe.parent.mkdir(parents=True);exe.write_bytes(b'package')
            docs={'closure.json':{'runtime_source_files':paths},'build.json':{'exe':str(exe),'runtime_count':166,'bytes':7,'sha256':hashlib.sha256(b'package').hexdigest()},'pck-audit.json':{'success':True},'packaged-integration-execution.json':{'actual_exit':0},'PACKAGED-INTEGRATION.json':{'success':False}}
            for name,doc in docs.items():(folder/name).write_text(json.dumps(doc))
            self.assertIsNone(catalog.verified_candidate('package38',root))
            (folder/'PACKAGED-INTEGRATION.json').write_text('{"success":true}')
            self.assertIsNotNone(catalog.verified_candidate('package38',root))
            exe.write_bytes(b'changed')
            self.assertIsNone(catalog.verified_candidate('package38',root))
    def test_state_persistence_conflict_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'local-state.json'
            status,value=server.update_state({'revision':0,'id':'x','changes':{'status':'review','priority':'high','notes':'검토'}},{'x'},p)
            self.assertEqual(status,200);self.assertEqual(server.load_state(p),value)
            status,value=server.update_state({'revision':0,'id':'x','changes':{'notes':'stale'}},{'x'},p)
            self.assertEqual(status,409);self.assertEqual(value['records']['x']['notes'],'검토')
            for payload in [{'revision':1,'id':'bad','changes':{'notes':'x'}},{'revision':1,'id':'x','changes':{'path':'bad'}},{'revision':1,'id':'x','changes':{'status':'fake'}}]:
                with self.assertRaises(ValueError):server.update_state(payload,{'x'},p)
    def test_paths(self):
        allowed={'chapter1/core/chapter_items.gd'}
        self.assertIsNotNone(server.permitted_file('chapter1/core/chapter_items.gd',allowed))
        for p in ['../.env','%2e%2e/project.godot','C:/Users/a','chapter1/../../project.godot','.git/config','tools/game_manager/local-state.json','project.godot']:
            self.assertIsNone(server.permitted_file(p,allowed),p)
    def test_origin(self):
        self.assertTrue(server.trusted_request('127.0.0.1:8781','http://127.0.0.1:8781',8781))
        self.assertFalse(server.trusted_request('evil:8781',None,8781))
        self.assertFalse(server.trusted_request('127.0.0.1:8781','https://evil.example',8781))
        self.assertFalse(server.trusted_request('127.0.0.1:8781','null',8781))
if __name__=='__main__':unittest.main()
