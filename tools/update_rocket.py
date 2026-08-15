import base64
import re

with open('assets/skills/rocket.png', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('utf-8')

image_tag = f'''    <!-- Spacecraft (rocket) -->
    <g transform="translate(820, 0)">
      <image href="data:image/png;base64,{b64}" x="-60" y="-23" width="120" height="46"/>
    </g>'''

for filename in ['assets/skills/toolchain-dark.svg', 'assets/skills/toolchain-light.svg']:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace spacecraft section
    pattern = r'<!-- Spacecraft.*?<\/g>'
    new_content = re.sub(pattern, image_tag, content, flags=re.DOTALL)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'Updated {filename}')
