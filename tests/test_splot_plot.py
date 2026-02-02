def test_split_plot_runs():
    from agrodesign.analysis.anova import Anova
    import pandas as pd
    
    df = pd.DataFrame({
        "Rep": [1,1,1,1, 2,2,2,2],
        "A": ["A1","A1","A1","A1","A2","A2","A2","A2"],
        "B": ["B1","B2","B1","B2","B1","B2","B1","B2"],
        "Yield": [10,12,11,13,15,17,16,18]
    })
    
    aov = Anova(df, response="Yield")
    table = aov.split_plot("A", "B", "Rep")

    assert 'C(A)' in table.index

    assert 'C(Rep):C(A)' in table.index
    assert 'Residual' in table.index


