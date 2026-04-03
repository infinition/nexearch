"""Build writeups_data.js from .md files for offline viewing."""
import sys, os

sys.stdout.reconfigure(encoding='utf-8')

files = {
    'wu-001-neurons': 'solutions/001_entropy_gated_learning/writeups/overview.md',
    'wu-P01-itfromfix': 'solutions/P01_lvs_theory/writeups/it_from_fix.md',
    'wu-P01-pause': 'solutions/P01_lvs_theory/writeups/Et_si_lunivers_etait_en_pause.md',
    'wu-P01-dupointfixe': 'solutions/P01_lvs_theory/writeups/Du Point Fixe au Point de Rupture.md',
}

base = os.path.dirname(os.path.abspath(__file__))
out_lines = ['// Auto-generated from .md files. Regenerate with: python build_writeups.py']
out_lines.append('const WRITEUP_CONTENT = {};')

for wid, relpath in files.items():
    fpath = os.path.join(base, relpath)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    # Escape for JS template literal
    content = content.replace('\\', '\\\\')
    content = content.replace('`', '\\`')
    content = content.replace('${', '\\${')
    out_lines.append(f'WRITEUP_CONTENT["{wid}"] = `{content}`;')
    print(f'  {wid}: {len(content)} chars')

outpath = os.path.join(base, 'writeups_data.js')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(out_lines))

print(f'Written: {outpath} ({os.path.getsize(outpath)} bytes)')
