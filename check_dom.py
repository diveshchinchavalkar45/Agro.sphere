with open('index.html', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if 'modal-bg' in line or 'class="app"' in line:
            print(f'Line {i}: {line.strip()[:80]}')
