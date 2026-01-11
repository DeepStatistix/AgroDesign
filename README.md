agrodesign

agrodesign is a Python package for Design of Experiments (DOE) and Analysis of Variance (ANOVA) in agricultural and biological research.
It provides agricolae-style functionality in Python with support for classical and complex experimental designs, correct error structures, post-hoc mean separation, assumption checking, and journal-ready plots.

🚜 Why agrodesign?

Most Python statistics libraries focus on generic modeling.
agrodesign is built specifically for agricultural experiments, where design structure matters.

It correctly handles:

    blocking
    factorial interactions
    split-plot error strata
    treatment mean separation
    assumption diagnostics

✨ Features

    Completely Randomized Design (CRD)
    Randomized Complete Block Design (RCBD)
    Factorial experiments (two or more factors)
    Split-plot design with correct error terms
    Mean separation tests:
    Least Significant Difference (LSD)
    Tukey’s Honest Significant Difference (HSD)
    Assumption checks:
    Shapiro–Wilk normality test
    Levene’s test
    Bartlett’s test
    Publication-ready plots:
    Mean plots with grouping letters
    Boxplots with grouping letters
    Fully tested using pytest

📦 Installation
    Development installation
    
    git clone https://github.com/DeepStatistix/AgroDesign.git
    cd AgroDesign
    pip install -e .
    (Planned: PyPI release)

🧠 Core Workflow

        The typical workflow in agrodesign is:
        Define the ANOVA model (CRD / RCBD / factorial / split-plot)
        Examine the ANOVA table
        Compute treatment or factor means
        Perform mean separation (LSD / Tukey)
        Check model assumptions
        Visualize results

🔹 Completely Randomized Design (CRD)
    Example
    from agrodesign.analysis.anova import Anova
    aov = Anova(df, response="Yield")
    aov.crd("Treatment")
    
    Treatment means
    aov.means("Treatment")

    Mean separation (LSD)
    from agrodesign.mean_separation.lsd import LSD

    lsd = LSD(aov)
    lsd.test()

🔹 Randomized Complete Block Design (RCBD)
    Example
    aov = Anova(df, response="Yield")
    aov.rcbd(treatment="Treatment", block="Block")

    Means and mean separation
    aov.means("Treatment")

    from agrodesign.mean_separation.tukey import TukeyHSD
    TukeyHSD(aov, factor="Treatment").test()

🔹 Factorial Experiments (Two or More Factors)
    Two-factor factorial
    aov = Anova(df, response="Yield")
    aov.factorial(["A", "B"])

    Main-effect means
    aov.factorial_means("A")
    aov.factorial_means("B")

    Interaction means
    aov.factorial_means(["A", "B"])

    Tukey HSD for interaction
    from agrodesign.mean_separation.tukey import TukeyHSD

    TukeyHSD(aov, factor=["A", "B"]).test()

🔹 Split-Plot Design

    Split-plot designs are handled with correct error structures.

    Model specification
    aov = Anova(df, response="Yield")

    aov.split_plot(
        whole_plot="A",
        sub_plot="B",
        block="Rep"
    )
    
    Sub-plot and interaction means
    aov.factorial_means(["A", "B"])

    Mean separation (subplot error)
    from agrodesign.mean_separation.lsd import LSD

    lsd = LSD(aov)
    lsd.test()

📊 Mean Separation Tests
    Least Significant Difference (LSD)
    from agrodesign.mean_separation.lsd import LSD

    lsd = LSD(aov)
    lsd.test()
    
    Tukey Honest Significant Difference (HSD)
    from agrodesign.mean_separation.tukey import TukeyHSD
    
    TukeyHSD(aov, factor="Treatment").test()
    

Both tests support:

    CRD
    RCBD
    factorial main effects
    factorial interactions
    split-plot sub-plot effects

📈 Visualization
    Mean plot with grouping letters
    from agrodesign.plots.mean_plot import mean_plot
    
    mean_plot(lsd.test(), ylabel="Yield (t ha⁻¹)")
    
    Boxplot with grouping letters
    from agrodesign.plots.boxplot_letters import boxplot_letters
    
    boxplot_letters(aov, factor="Treatment")
    
    
    Plots are journal-ready and display grouping letters directly.

🧪 Assumption Checks

    Assumptions are checked on model residuals.
    
    from agrodesign.analysis.assumptions import Assumptions
    
    assump = Assumptions(aov)
    
    assump.shapiro_test()
    assump.levene_test("Treatment")
    assump.bartlett_test("Treatment")
    assump.qq_plot()
    

Supported for all designs:

    CRD
    RCBD
    factorial
    split-plot
    
🧪 Testing
    Run the full test suite:

    pytest -v


All statistical components are validated using automated tests.

📊 Supported Designs
    Design	Status
    CRD	✅
    RCBD	✅
    Factorial (k-factor)	✅
    Split-plot	✅
    Strip-plot	Planned
    Mixed models	Planned


📖 Citation

If you use agrodesign in academic work, please cite:

Agrodesign (v0.3.0): A Python package for agricultural design of experiments and ANOVA.
GitHub: https://github.com/DeepStatistix/AgroDesign

(Planned: Zenodo DOI)

📜 License

    MIT License

👤 Author

    Aqib Gul
    DeepStatistix