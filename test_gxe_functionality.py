import pandas as pd
from agrodesign.experiment import Experiment

# Create test data
df = pd.DataFrame({
    "Genotype": ["G1", "G2", "G3", "G4"] * 8,
    "Environment": (["E1"] * 4 + ["E2"] * 4 + ["E3"] * 4 + ["E4"] * 4) * 2,
    "Rep": [1] * 16 + [2] * 16,
    "Yield": [
        45, 50, 55, 60,
        40, 48, 53, 58,
        47, 52, 57, 62,
        43, 49, 54, 59,

        46, 51, 56, 61,
        41, 47, 52, 57,
        48, 53, 58, 63,
        44, 50, 55, 60
    ]
})

print("Testing GxE functionality...")

# Test the gxe method
result = Experiment(df, "Yield").gxe("Genotype", "Environment", "Rep").run()

print("Result type:", type(result))
print("Result design:", result.design)
print("Result response:", result.response)

# Test the different output methods
print("\n--- Short snapshot (result) ---")
print(result)

print("\n--- Full report (print(result)) ---")
print(result)

print("\n--- Summary (result.summary()) ---")
result.summary()

print("\n--- Plot (result.plot()) ---")
try:
    result.plot(show=False)  # Don't show plots in test
    print("Plot generation successful")
except Exception as e:
    print(f"Plot error: {e}")

print("\n--- Export (result.export('test_gxe_report')) ---")
try:
    result.export("test_gxe_report")
    print("Export successful")
except Exception as e:
    print(f"Export error: {e}")

print("\nTest completed successfully!")
