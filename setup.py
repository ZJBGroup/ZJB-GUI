import setuptools

setuptools.setup(
    name="zjb-gui",
    version="0.2.6",
    description="The GUI of Zhejiang Lab's digital twin brain platform",
    author="ZJB Group",
    url="https://github.com/ZJBGroup/ZJB-GUI",
    license="GPL-3.0",
    install_requires=[
        "zjb-main @ https://github.com/ZJBGroup/ZJB-Main/archive/refs/tags/v0.2.6.tar.gz",
        "PyQt-Fluent-Widgets",
        "lmdb",
        "qtconsole",
        "requests",
        "QCustomPlot_PyQt5",
        "pyqtgraph!=0.13.3",
        "PyOpenGL",
        "colorcet",
        "biopython>=1.78",
    ],
    packages=setuptools.find_packages(),
    include_package_data=True,
)
