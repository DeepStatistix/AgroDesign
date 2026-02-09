import pandas as pd
from agrodesign.experiment import Experiment

df = pd.DataFrame({
    "Block":[1,1,1,2,2,2,3,3,3],
    "Treatment":["T1","T2","T3"]*3,
    "Yield":[42,50,55,40,48,54,43,49,56]
})
result = Experiment(df,"Yield").mixed(fixed=["Treatment"], random=["Block"]).run()
print(result)
print("blups:", result.blups)
print("type:", type(result.blups))
print("variance_components:", result.variance_components)
print("type vc:", type(result.variance_components))
print("\nTrying to plot...")
try:
    result.plot(show=False)
    print("Plot successful!")
except Exception as e:
    print(f"Plot failed: {e}")
