import hashlib, json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import catalog, server

class BackendTests(unittest.TestCase):
    def test_catalog(self):
        c=catalog.generate()
        self.assertIn(c['coverage']['runtime_files'],[163,166,172,175,176,180,183])
        self.assertTrue(catalog.UI38_FILES.issubset({f['path'] for f in c['files']}))
        self.assertEqual(c['build']['preserved_builds'][-1]['runtime_file_count'],163)
        self.assertEqual(len(c['tasks']),40)
        self.assertEqual(c['coverage']['semantic_counts']['audio_variants'],19)
        self.assertEqual(len([e for e in c['entities'] if e['type']=='bases']),12)
        self.assertEqual(len({e['id'] for e in c['entities']}),len(c['entities']))
        self.assertEqual(c['coverage']['runtime_extensions']['.gd'],{163:77,166:80,172:82,175:83,176:84,180:85,183:86}[c['coverage']['runtime_files']])
        self.assertEqual({k:c['coverage']['categories'][k] for k in ['equipment','skills','enemies','characters','balance','ui']},{'equipment':12,'skills':3,'enemies':4,'characters':1,'balance':17,'ui':{163:6,166:6,172:7,175:8,176:8,180:8,183:8}[c['coverage']['runtime_files']]})
        if c['coverage']['runtime_files']>=172:
            result=next(e for e in c['entities'] if e['id']=='ui:result')
            self.assertEqual(result['source']['path'],catalog.UI40_FILE)
            self.assertEqual(result['attributes']['function'],'_build_result40')
            self.assertEqual(result['task_ids'],['U08'])
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
        for outcomes,target,attempts in [([None,None,None,None,None,selected],catalog.CANDIDATE38,6),([None,None,None,None,selected],catalog.CANDIDATE40,5),([None,None,None,selected],catalog.CANDIDATE41,4),([None,None,selected],catalog.CANDIDATE42,3),([None,selected],catalog.CANDIDATE43,2),([selected],catalog.CANDIDATE44,1)]:
            with patch.object(catalog,'verified_candidate',side_effect=outcomes) as verify:
                self.assertEqual(catalog.selected_build()[0],target+'/closure.json')
                self.assertEqual([c.args[0] for c in verify.call_args_list],[s['directory'] for s in catalog.CANDIDATES[:attempts]])
    def test_candidate40_and_portrait(self):
        spec=next(s for s in catalog.CANDIDATES if s['number']==40)
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
        self.assertEqual(portrait['usage'],'active-inherited' if c['coverage']['runtime_files']>=175 else 'plan');self.assertEqual(portrait['provenance']['kind'],'AI-generated')
        self.assertIn('creation_snapshot',portrait['attributes'])
        self.assertEqual(portrait['task_ids'],['C03','C05'])
        hero=next(e for e in c['entities'] if e['id']=='actors:hero')
        self.assertTrue(hero['assets'][0].endswith('.glb'))
    def test_candidate41_preservation_gate(self):
        spec=next(s for s in catalog.CANDIDATES if s['number']==41)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=root/'package41';folder.mkdir()
            paths=sorted(spec['required'])+['source/%d.gd'%i for i in range(spec['count']-len(spec['required']))]
            for path in paths:
                target=root/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text('source')
            exe=root/'builds/chapter1/test.exe';exe.parent.mkdir(parents=True);exe.write_bytes(b'package')
            docs={'closure.json':{'build_id':spec['build_id'],'runtime_source_files':paths},'build.json':{'exe':str(exe),'runtime_count':175,'bytes':7,'sha256':hashlib.sha256(b'package').hexdigest()},'pck-audit.json':{'success':True},'packaged-integration-execution.json':{'actual_exit':0,'timed_out':False,'launch_error':None},'PACKAGED-INTEGRATION.json':{'success':True}}
            for name,doc in docs.items():(folder/name).write_text(json.dumps(doc))
            self.assertIsNone(catalog.verified_candidate('package41',root,spec))
            preservation={key:True for key in spec['preservation_fields']}
            (folder/'FINAL-PRESERVATION.json').write_text(json.dumps(preservation))
            self.assertIsNotNone(catalog.verified_candidate('package41',root,spec))
            preservation['profiles_byte_identical']=False
            (folder/'FINAL-PRESERVATION.json').write_text(json.dumps(preservation))
            self.assertIsNone(catalog.verified_candidate('package41',root,spec))
    def test_selected41_title_and_portrait_usage(self):
        closure=json.loads(catalog.read(catalog.CANDIDATE40+'/closure.json'))
        closure['runtime_source_files']+= [catalog.UI41_FILE,catalog.PORTRAIT_PNG,catalog.PORTRAIT_ATTRIBUTION]
        closure['build_id']=next(s['build_id'] for s in catalog.CANDIDATES if s['number']==41)
        original_read=catalog.read
        def with_title_source(path):
            value=original_read(path)
            if path=='chapter1/chapter_one_view.gd':
                value=value.replace('res://chapter1/view/ui40/chapter_hud_quality40.gd','res://'+catalog.UI41_FILE)
            return value
        with patch.object(catalog,'selected_build',return_value=(catalog.CANDIDATE41+'/closure.json',closure,{'exe':'example'})),patch.object(catalog,'read',side_effect=with_title_source):
            c=catalog.generate()
        self.assertEqual(c['coverage']['categories']['ui'],8)
        title=next(e for e in c['entities'] if e['id']=='ui:title')
        self.assertEqual(title['source']['path'],catalog.UI41_FILE)
        self.assertEqual(title['attributes']['function'],'_build_menu41')
        self.assertEqual(title['task_ids'],['C03','C05'])
        portrait=next(e for e in c['entities'] if e['id']=='asset:'+catalog.PORTRAIT_PNG)
        self.assertEqual(portrait['usage'],'active-inherited')
        self.assertEqual(portrait['attributes']['asset_kind'],'타이틀 원화 · 2D')
        self.assertTrue(portrait['attributes']['not_3d'])
        self.assertIn('creation_snapshot',portrait['attributes'])
        self.assertNotIn('status',portrait['attributes'])
        self.assertEqual([e['runtime_file_count'] for e in c['build']['preserved_builds']],[172,166,163])
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
    def test_registered_preview_allowlist(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            image='plans/chapter1-quality04-20261101-01/arc44/proof/scene.png'
            target=root/image;target.parent.mkdir(parents=True);target.write_bytes(b'PNG fixture')
            other=root/'private.png';other.write_bytes(b'private')
            catalog_fixture={'entities':[{'previews':[{'path':image},{'path':'private.png'},{'path':'plans/chapter1-quality04-20261101-01/../../private.png'},{'path':'plans/chapter1-quality04-20261101-01/arc44/proof/state.json'}]}]}
            allowed=server.registered_preview_paths(catalog_fixture,root)
            self.assertEqual(allowed,{image})
            with patch.object(server,'ROOT',root):
                self.assertEqual(server.permitted_file(image,allowed),target.resolve())
                self.assertIsNone(server.permitted_file('private.png',allowed))
    def test_origin(self):
        self.assertTrue(server.trusted_request('127.0.0.1:8781','http://127.0.0.1:8781',8781))
        self.assertFalse(server.trusted_request('evil:8781',None,8781))
        self.assertFalse(server.trusted_request('127.0.0.1:8781','https://evil.example',8781))
        self.assertFalse(server.trusted_request('127.0.0.1:8781','null',8781))
if __name__=='__main__':unittest.main()
