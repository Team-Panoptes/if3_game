import setuptools
import if3_game


setuptools.setup(
    name="if3_game",
    version=if3_game.__version__,
    author="Bastien Gorissen & Thomas Stassin",
    author_email="info@panopticgame.com",
    description="small engine to learn game design with python",
    packages=setuptools.find_packages(),
    install_requires=['cocos2d', 'pyglet==1.3.1']
)