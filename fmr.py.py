import logging
import src.measurement as m
from nidaqmx.constants import Edge, TaskMode


def main():
    
    logging.basicConfig(filename='./log/fmr.log', filemode='w', level=logging.INFO)

    edges = {'mode': TaskMode.TASK_COMMIT,
            'read-edge': Edge.FALLING,
            'write-edge': Edge.RISING,}
    fmr = m.FMRHandler('./recipes/fmr_1.yaml', edges)
    fmr.start_FMR()


if __name__ == '__main__':
    main()