def help():
    print("""
AgroDesign Quick Help
---------------------

Single experiment:
    Experiment(df,"Yield").rcbd("Variety","Block").run()

Grouped:
    Experiment(df,"Yield").by("Year").rcbd("Variety","Block").run()

Multi-trait:
    Experiment(df,["Yield","Height"]).rcbd("Variety","Block").run()

G×E:
    Experiment(df,"Yield").gxe("Genotype","Environment","Rep").run()

Datasets:
    load_dataset("rcbd")
""")
