with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

stack = []
for idx, line in enumerate(lines, 1):
    # count <div> and </div>
    open_divs = line.count('<div')
    close_divs = line.count('</div>')
    for _ in range(open_divs):
        stack.append(idx)
    for _ in range(close_divs):
        if stack:
            stack.pop()
        else:
            print(f"Extra closing div at line {idx}")

print(f"Remaining unclosed divs count: {len(stack)}")
for s in stack:
    print(f"Unclosed div opened at line {s}: {lines[s-1].strip()[:60]}")
