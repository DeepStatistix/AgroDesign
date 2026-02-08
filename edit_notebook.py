import json

with open('examples/test_anova.ipynb', 'r') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = cell['source']
        new_source = []
        skip = False
        for line in source:
            if 'mean_plot(' in line:
                skip = True
            if skip:
                if ')' in line:
                    skip = False
                continue
            new_source.append(line)
        cell['source'] = new_source

with open('examples/test_anova.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)
