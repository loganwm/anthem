from distutils.core import setup
import py2exe

setup(windows=[{"script":"player.pyw"}], options={"py2exe": {"includes": ["sip"]}})
