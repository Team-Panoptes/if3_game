import setuptools
import if3_game


setuptools.setup(
    name="if3_game",
    version=if3_game.__version__,
    author="Bastien Gorissen & Thomas Stassin",
    author_email="info@panopticgame.com",
    description="Small engine to learn game design with Python",
    packages=setuptools.find_packages(),
    install_requires=['cocos2d==0.6.5', 'pyglet==1.3.3']
)
