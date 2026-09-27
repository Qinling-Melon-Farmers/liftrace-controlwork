from pathlib import Path
import json,sys,shutil,subprocess,html
out=Path(sys.argv[1]);links=[];latest={};mock_calls=0
if (out/'vision_events.jsonl').exists():
    for line in (out/'vision_events.jsonl').read_text().splitlines():
        try:e=json.loads(line)
        except ValueError:continue
        latest[e['kind']]=e['data'];mock_calls+=int(e['kind']=='mock')
        if e['kind']=='mission' and e['data'].get('active_command')=='LAND':latest['landing_command']=e['data']
supervisor=json.loads((out/'supervisor_result.json').read_text()) if (out/'supervisor_result.json').exists() else {}
from trial_result import evaluate
reference=json.loads((out/'ground_reference.json').read_text()) if (out/'ground_reference.json').exists() else {}
result=evaluate(supervisor,latest,reference.get('settings',{}))
committed=result['committed_deliveries'];result['mock_service_calls']=mock_calls
# Compatibility for existing report readers; real service completions are not labelled mock.
result['expected_mock_deliveries']=result['expected_deliveries'] if result['actuator_mode']=='mock' else 0
result['committed_mock_deliveries']=committed if result['actuator_mode']=='mock' else 0
(out/'result.json').write_text(json.dumps(result,indent=2))
for name in ('camera_raw','camera_annotated'):
    source=out/(name+'.mp4');target=out/(name+'_h264.mp4')
    if not source.exists():continue
    if shutil.which('ffmpeg') and not target.exists():
        completed=subprocess.run(['ffmpeg','-nostdin','-v','error','-i',str(source),'-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','23','-movflags','+faststart',str(target)])
        if completed.returncode:target.unlink(missing_ok=True)
    video=target if target.exists() else source;links.append(f'<h2>{name}</h2><video controls src="{video.name}" style="max-width:100%"></video>')
(out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Modular board camera review</title><p>Actuator: '+html.escape(result['actuator_mode'])+'</p><h1>相机与视觉链回看</h1><p>结果：'+result['status']+'；投递确认 '+str(committed)+' 次。<a href="result.json">结果详情</a></p><p>橙色：YOLO；绿色：几何精修/地图投影。时间未匹配的框不画在当前图像上。底栏为任务/记忆/对准状态，详见 vision_events.jsonl 与 camera_frames.csv。INCOMPLETE保留中途停止、预览、缺靶与失败，不伪报成功。</p>'+''.join(links))
print('Camera review:',out/'index.html')
