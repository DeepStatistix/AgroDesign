import pandas as pd
import sys
from agrodesign import Experiment

# Create sample data for 2x2 factorial
df = pd.DataFrame({
    'Yield': [10, 12, 11, 13, 14, 15, 16, 17, 9, 11, 12, 14, 13, 15, 14, 16],
    'A': ['A1']*8 + ['A2']*8,
    'B': (['B1']*4 + ['B2']*4) * 2
})

print('Testing console mode (should print full report):')
exp = Experiment(df, 'Yield').factorial(['A', 'B'])
result = exp.run()

print('\n' + '='*50)
print('Testing library mode (should be silent):')
result2 = Experiment(df, 'Yield').factorial(['A', 'B']).run()

print('\nTesting result.__repr__ (short snapshot):')
print(result2)

print('\nTesting result.summary() (agronomic interpretation):')
result2.summary()

print('\nTesting result.plot(save_dir="test_plots"):')
result2.plot(save_dir='test_plots')

print('\nTesting result.export("test_export"):')
result2.export('test_export')
