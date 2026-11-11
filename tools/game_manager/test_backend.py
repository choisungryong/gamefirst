import hashlib, json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import catalog, server

class BackendTests(unittest.TestCase):
    def test_catalog(self):
        c=catalog.generate()
        self.assertIn(c['coverage']['runtime_files'],[163,166,172])
        self.assertTrue(catalog.UI38_FILES.issubset({f['path'] for f in c['files']}))
        self.assertEqual(c['build']['preserved_builds'][-1]['runtime_file_count'],163)
        self.assertEqual(len(c['tasks']),40)
        self.assertEqual(c['coverage']['semantic_counts']['audio_variants'],19)
        self.assertEqual(len([e for e in c['entities'] if e['type']=='bases']),12)
        self.assertEqual(len({e['id'] for e in c['entities']}),len(c['entities']))
        self.assertEqual(c['coverage']['runtime_extensions']['.gd'],{163:77,166:80,172:82}[c['coverage']['runtime_files']])
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
            docs={'closure.json':{'build_id':catalog.CANDIDATES[-1]['build_id'],'runtime_source_files':paths},'build.json':{'exe':str(exe),'runtime_count':166,'bytes':7,'sha256':hashlib.sha256(b'package').hexdigest()},'pck-audit.json':{'success':True},'packaged-integration-execution.json':{'actual_exit':0,'timed_out':False,'launch_error':None},'PACKAGED-INTEGRATION.json':{'success':False}}
            for name,doc in docs.items():(folder/name).write_text(json.dumps(doc))
            self.assertIsNone(catalog.verified_candidate('package38',root))
            (folder/'PACKAGED-INTEGRATION.json').write_text('{"success":true}')
            self.assertIsNotNone(catalog.verified_candidate('package38',root))
            # Preserved38 execution schema predates explicit launch_error:null.
            (folder/'packaged-integration-execution.json').write_text('{"actual_exit":0,"timed_out":false}')
            self.assertIsNotNone(catalog.verified_candidate('package38',root))
            exe.write_bytes(b'changed')
            self.assertIsNone(catalog.verified_candidate('package38',root))
    def test_latest_verified_selection(self):
        selected=({'build_id':'verified'},{'exe':'example'})
        with patch.object(catalog,'verified_candidate',side_effect=[None,selected]) as verify:
            self.assertEqual(catalog.selected_build()[0],catalog.CANDIDATE38+'/closure.json')
            self.assertEqual([c.args[0] for c in verify.call_args_list],[catalog.CANDIDATE40,catalog.CANDIDATE38])
        with patch.object(catalog,'verified_candidate',return_value=selected) as verify:
            self.assertEqual(catalog.selected_build()[0],catalog.CANDIDATE40+'/closure.json')
            self.assertEqual(verify.call_count,1)
    def test_candidate40_and_portrait(self):
        spec=catalog.CANDIDATES[0]
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=root/'package40';folder.mkdir()
            paths=sorted(spec['required'])+['source/%d.gd'%i for i in range(spec['count']-len(spec['required']))]
            for p in paths:
                target=root/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_text('source')
            exe=root/'builds/chapter1/test.exe';exe.parent.mkdir(parents=True);exe.write_bytes(b'package')
            docs={'closure.json':{'build_id':spec['build_id'],'runtime_source_files':paths},'build.json':{'exe':str(exe),'runtime_count':172,'bytes':7,'sha256':hashlib.sha256(b'package').hexdigest()},'pck-audit.json':{'success':True},'packaged-integration-execution.json':{'actual_exit':0,'timed_out':False,'launch_error':None},'PACKAGED-INTEGRATION.json':{'success':True}}
            for name,doc in docs.items():(folder/name).write_text(json.dumps(doc))
            self.assertIsNotNone(catalog.verified_candidate('package40',root,spec))
            docs['closure.json']['runtime_source_files'].remove(catalog.UI40_FILE)
            (folder/'closure.json').write_text(json.dumps(docs['closure.json']))
            self.assertIsNone(catalog.verified_candidate('package40',root,spec))
        c=catalog.generate();portraits=[e for e in c['entities'] if e['id']=='asset:'+catalog.PORTRAIT_PNG]
        self.assertEqual(len(portraits),1);portrait=portraits[0]
        self.assertEqual(portrait['usage'],'plan');self.assertEqual(portrait['provenance']['kind'],'AI-generated')
        self.assertEqual(portrait['task_ids'],['C03','C05'])
        hero=next(e for e in c['entities'] if e['id']=='actors:hero')
        self.assertTrue(hero['assets'][0].endswith('.glb'))
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
