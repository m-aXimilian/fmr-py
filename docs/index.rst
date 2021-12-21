.. FMR Python Implementation documentation master file, created by
   sphinx-quickstart on Wed Dec 15 19:10:02 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

FMR Python Implementation -- Documentation
=====================================================
Automated FMR-measurements based on simple yaml-recipe files.
Code lives `here <https://github.com/m-aXimilian/fmr-py>`_

Prerequisites
-------------
- Python3.# and pyvisa (`pip install pyvisa`)
- NI-DAQmx Pyhton API (`python -m pip install git+https://github.com/ni/nidaqmx-python.git`) [1]_
- NIVisa
- pyyaml (`pip install pyyaml`)
- tqdm for progressbar (`pip install tqdm`)

.. [1] `Sequence` moved from `collections` to `collections.abc` in Python 3.10 which yiedls include errors when using pip nidaqmx `issue 129 <https://github.com/ni/nidaqmx-python/issues/129>`_



Usage
-----

1. Create a yaml-file making up the desired measurement routine (see a `template <https://github.com/m-aXimilian/fmr-py/blob/dev/recipes/template_recipe.yaml>`_).
2. Import the :doc:`measurement` module.
3. Create an object of the FMRHandler class and
4. pass it the path to the yaml-file created in 1. as well as a dictionary providing the task-mode and the read- and write-edge for the DAQ process.
5. Call the start method of the created object.

This should look something like this:
::
    import src.measurement as m
    from nidaqmx.constants import Edge, TaskMode


    def main():
        
        logging.basicConfig(filename='./log/fmr.log', filemode='w', level=logging.DEBUG)

        edges = {'mode': TaskMode.TASK_COMMIT,
                'read-edge': Edge.FALLING,
                'write-edge': Edge.RISING,}

        fmr = m.FMRHandler('./recipes/fmr_1.yaml', edges)

        fmr.start_FMR()
        
    if __name__ == '__main__':
        main()

.. toctree::
    modules


Indices
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
