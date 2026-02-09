import pandas as pd
from agrodesign.experiment import Experiment

# Test data for GxE
df = pd.DataFrame({
    "Genotype":["G1","G2","G3","G4"]*8,
    "Environment":(["E1"]*4 + ["E2"]*4 + ["E3"]*4 + ["E4"]*4)*2,
    "Rep":[1]*16 + [2]*16,
    "Yield":[
        45,50,55,60,
        40,48,53,58,
        47,52,57,62,
        43,49,54,59,
        46,51,56,61,
        41,47,52,57,
        48,53,58,63,
        44,50,55,60
    ]
})

print("=== Testing Direct Execution (should print full report) ===")
Experiment(df,"Yield").gxe("Genotype","Environment","Rep").run()

print("\n=== Testing Assignment (should be silent) ===")
result = Experiment(df,"Yield").gxe("Genotype","Environment","Rep").run()

print("\n=== Testing repr (snapshot) ===")
print(repr(result))

print("\n=== Testing str (full report) ===")
print(str(result)[:200] + "...")  # Print first 200 chars to avoid too much output

print("\n=== Testing summary (agronomic interpretation) ===")
result.summary()

print("\n=== Testing export (should be silent) ===")
result.export("test_report")
print("Export completed.")
