# _patch_cap5.py  →  python _patch_cap5.py
import json, shutil
p = r'data/scripts/91bea3b0-eb43-4797-a32d-90a45fccf1c8.json'
shutil.copy(p, p + '.bak')
d = json.load(open(p, encoding='utf-8'))
S = " Shot with documentary-style cinematography, gritty digital film emulation, low-key dramatic lighting, cold desaturated palette, coarse analog noise texture."
nuevos = {
 8:  "The 1880s Old Jail in Charleston seen from the street against a pale clear sky, its roofline now low and simple where an upper level and tower once rose, weathered red brick walls and a plain capped parapet, calm even daytime light over the quiet facade." + S,
 14: "A tight low-angle view of a narrow enclosed courtyard inside the 1880s Old Jail in Charleston at cold dawn in 1911, towering weathered brick walls pressing in on all sides over the small bare stone floor, a single hard shaft of pale light cutting diagonally through the deep shadow and striking one empty patch of damp cobblestone, a heavy coiled rope left abandoned at the base of the wall, long stark shadows stretching across the ground, oppressive silence and dread hanging in the cold air." + S,
 15: "A wide low-angle view of the oppressive inner courtyard of the 1880s Old Jail in Charleston in cold grey 1911 dawn light, towering tiers of barred windows in weathered brick looming over a worn stone floor smoothed by long use, a single heavy rusted iron ring bolted into the base of the wall catching a thin band of pale light, deep overlapping shadows stretching across the cobblestones, an atmosphere of institutional weight and grim inevitability." + S,
 16: "The narrow enclosed courtyard of the Old Jail in Charleston as the cold 1911 dawn light fades, a thin shaft of pale light dissolving slowly into rising grey mist over empty damp cobblestones, the towering brick walls sinking into deep shadow around a single bare patch of ground where the light still falls, heavy motionless air, a profound emptiness marking the close of an era." + S,
}
ch = [c for c in d['chapters'] if c.get('chapter_number') == 5][0]
for n, txt in nuevos.items():
    ch['image_prompts'][n-1]['prompt'] = txt
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('OK — 4 prompts de cap5 reescritos (AP9 calma TENSA). backup en', p + '.bak')
