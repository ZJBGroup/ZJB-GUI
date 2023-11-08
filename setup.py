import setuptools

setuptools.setup(
    name="zjb-gui",
    version="0.2.5",
    install_requires=[
        "zjb-main>=0.2.5",
        "PyQt-Fluent-Widgets",
        "lmdb",
        "scikit-learn",
        "qtconsole",
        "requests",
        "QCustomPlot_PyQt5",
        "pyqtgraph",
        "PyOpenGL",
        "colorcet",
        "biopython>=1.78",
    ],
    packages=setuptools.find_packages(),
    include_package_data=True,
)
