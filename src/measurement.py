from genericpath import exists
import logging
import numpy as np
from numpy.core.fromnumeric import shape
import yaml
import pyvisa as vi
from time import sleep, strftime
from tqdm import tqdm
import numpy as np
from nidaqmx import stream_readers
from scipy import signal
from pathlib import Path
import threading
import matplotlib.pyplot as plt

import os, sys

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)

import src.visa_devices as devs



class FMRHandler:
    
    def __init__(self, _path, _edges) -> None:
        self.params = FMRHandler.read_setup(_path)
        self.params.update(_edges)
        rm = vi.ResourceManager()
        self.params['rf-rm'] = rm
        self.waves = WaveForm(self.params['h-max'], self.params['N'], self.params['h-zero'])
        self.params['H-set'] = self.waves.triangle_10()

        tmp_dir = self.params['dir']
        self.do_single_f = (self.params['rf-start'] == self.params['rf-stop'])
        if not self.do_single_f:
            self.params['dir']  = '{}/{}/{}'.format(
                tmp_dir,
                'measurement',
                '{}_{}-{}GHz_sweep'.format(
                    self.params['name'],
                    self.params['rf-start'],
                    self.params['rf-stop']
                )
            )
        else:
            self.params['dir']  = '{}/{}/{}'.format(
                tmp_dir,
                'measurement',
                '{}_{}GHz'.format(
                    self.params['name'],
                    self.params['rf-freq'],
                )
            )

        Path(self.params['dir']).mkdir(parents=True, exist_ok=True)


    @staticmethod
    def measure_thread(_fmr_meas):
        _fmr_meas.cfg_measurement()
        _fmr_meas.start_measurement()
        _fmr_meas.release_resources()    


    def start_FMR(self):
        """For every frequency defined in the parameters one measurement will be taken.
        If the start and the stop frequency are identical, there will be only one file."""
        for i in np.arange(self.params['rf-start'], 
            self.params['rf-stop'] + self.params['rf-step'], 
            self.params['rf-step']):
            self.params['rf-freq'] = i
            meas = FMRMeasurement(self.params)
            name, params = meas.f_name, meas.params
            tr = threading.Thread(target=FMRHandler.measure_thread, args=(meas,))
            tr.start()
            
            self.live_plot_subs(name, params)
            
            
    def live_plot_subs(self, _fname, _params):
        """Live Plot from the date in _FNAME and corresponding parameters in _PARAMS.
        ATTENTION: Crappy! Only works with 4 or more columns in the _FNAME data file."""
        to_plot = os.path.isfile(_fname)
        while not to_plot:
            sleep(.2)
            to_plot = os.path.isfile(_fname)
        
        reps = int(_params['N']/_params['buffer-size'])
        plt_pause = _params['buffer-size']/_params['rate']

        fig, (field, lock) = plt.subplots(2, 1)
        fig.canvas.set_window_title('{} {}GHz'.format(
            _params['name'],
            _params['rf-freq']
        ))
        
        for i in range(reps):
            field.cla()
            lock.cla()
            r = np.genfromtxt(_fname, delimiter=',', names=True, skip_header=3)
            row_names = r.dtype.names
            field.plot(r[row_names[0]],'g--', label=row_names[0])
            field.plot(r[row_names[1]],'r', label=row_names[1])
            lock.plot(r[row_names[2]], label=row_names[2])
            lock.plot(r[row_names[3]], label=row_names[3])
            field.legend(loc='upper left')
            field.grid()
            lock.legend(loc='upper left')
            lock.grid()
            plt.pause(plt_pause)
        plt.show(block=False)
        plt.pause(2)
        plt.close()

        
    @staticmethod
    def read_setup(_path) -> dict:
        """Return a dictionary from the yaml-file in _PATH."""
        with open(_path) as f:
            return yaml.safe_load(f)


class FMRMeasurement:
    """
    Container for a single measuremnt process (channels, frequency etc. can NOT be reconfigured).

    ATTENTION: Works with a arbitrary number of Input Channels, but only one Output Channel
    at a time!
    """
    def __init__(self, _params) -> None:
        """
        _PARAMS dictionary must contain the following
        {
            'rf-freq': 2,
            'rf-p': 0,
            'rf-rm': rm,    # vi resource manager
            'rf-conf': './config/hp83508.yaml',
            'h-max': 150,
            'h-zero': 0.1,   # p.u. for zero field start and end
            'N': 1000,
            'rate': 1000,
            'name': 'fmr-test',
            'dir': './measurement/', # must be terminated with a "/"
            'daq-dev': 'Dev1',
            'ai': {'field-set-measure': 'ai1', 'field-is-measure': 'ai2', 'x-value-lockin': 'ai0', 'y-value-lockin': 'ai4', },
            'ao': ['ao0'],
            'impuls': 'ctr0',
            'trigger': 'Ctr0InternalOutput',
            'mode': TaskMode.TASK_COMMIT,
            'read-edge': Edge.FALLING,
            'write-edge': Edge.RISING,
            'read-timeout': 30,
            'buffer-size': 200
        }
        """
        self.params = _params

        # move to handler
       # Path(self.params['dir'] + self.params['name']).mkdir(parents=True, exist_ok=True)
        
        self.f_name = self.generate_filename()
        self.daq_tasks = {}

        # move to handler
        #self.waves = WaveForm(self.params['h-max'], self.params['N'], self.params['h-zero'])
        #self.params['H-set'] = self.waves.triangle_10()

        if isinstance(self.params['ai'], str):
            self.cols = self.params['ai']
        elif issubclass(type(self.params['ai']), dict):
            self.cols = ",".join(self.params['ai'].keys())
        else:
            self.cols = ",".join(self.params['ai'])


    def release_resources(self):
        logging.info('Releasing daq resource')
        for task in self.daq_tasks.values():
            if task.task._handle is None:
                return
            task.task.close()
            
            
    def __read_callback(self, task_handle, event_type, num_samples, callback_data=None):
        buf=np.zeros((self.in_channels,self.params['buffer-size']))
        self.in_stream.read_many_sample(buf,num_samples)
        self.write_results(buf.T)
        
        return 0

    def generate_filename(self) -> str:
        return  '{d}/{n}-{f}GHz_{t}.csv'.format(
            d=self.params['dir'],
            n=self.params['name'],
            f=self.params['rf-freq'],
            t=strftime("%Y-%m-%d_%H-%M-%S"))

    def setup_rf(self) -> None:
        """Sets up the RF-source with the paramters from self.PARAMS (dict)"""
        self.rf = devs.HP83508(self.params['rf-rm'], self.params['rf-conf'])
        self.rf.setF(self.params['rf-freq'])
        self.rf.setP(self.params['rf-p'])
        

    def setup_daq_inputs(self) -> None:
        """Sets up the DAQ input with the paramters from self.PARAMS (dict)"""
        self.daq_tasks.update(
            {'reader' : devs.NIUSB6259()}
        )

        self.daq_tasks['reader'].add_channels(
            self.params['daq-dev'], self.params['ai'], _type='ai'
        )

        self.daq_tasks['reader'].config_sample_clk(
            self.params['rate'], 
            self.daq_tasks['clock'].trigger, 
            self.params['read-edge'],
            self.params['N']
        )

        self.in_channels = len(self.daq_tasks['reader'].task.channels)
        self.in_stream = stream_readers.AnalogMultiChannelReader(
            self.daq_tasks['reader'].task.in_stream
        )

        self.daq_tasks['reader'].task.register_every_n_samples_acquired_into_buffer_event(
            self.params['buffer-size'], self.__read_callback)

    def setup_daq_outputs(self) -> None:
        """Sets up the DAQ output with the paramters from self.PARAMS (dict)"""
        self.daq_tasks.update(
            {'writer' : devs.NIUSB6259()}
        )

        self.daq_tasks['writer'].add_channels(
            self.params['daq-dev'], self.params['ao'], _type='ao'
        )

        self.daq_tasks['writer'].config_sample_clk(
            self.params['rate'], 
            self.daq_tasks['clock'].trigger, 
            self.params['write-edge'],
            self.params['N']
        )


    def setup_daq_clk(self) -> None:
        """Sets up the DAQ clock and trigger with the paramters from self.PARAMS (dict)"""
        self.daq_tasks.update(
            {'clock' : devs.NIUSB6259()}
        )

        self.daq_tasks['clock'].config_clk(
            self.params['daq-dev'],
            self.params['impuls'],
            self.params['rate'],
            self.params['N'],
            self.params['mode']
        )

        self.daq_tasks['clock'].set_trigger(
            self.params['daq-dev'],
            self.params['trigger'])


    def start_measurement(self) -> None:
        """Start a measurement. Depends on :func:`~self.setup_daq_inputs`
        :func:`~self.setup_daq_outputs` and :func:`~self.setup_daq_clk`.
        I.e. will raise an error if those were not called before."""
        with open('./config/daq_limits.yaml', 'r') as f:
            limits = yaml.safe_load(f)
            if max(abs(self.params['H-set'])) > limits['max-v-output']:
                raise ValueError('Set field exeeds limits!')
                
        self.daq_tasks['writer'].analog_write(self.params['H-set'])

        self.daq_tasks['reader'].start()
        self.daq_tasks['writer'].start()
        self.daq_tasks['clock'].start()
        
        self.m_time = self.params['N']/self.params['rate']
        
        logging.info('Meas:  Measurement will take {} seconds.'.format(self.m_time))
        
        for i in tqdm(range(int(self.m_time))):
            sleep(1)
        
   
    def cfg_measurement(self) -> None:
        """Configure the measurement in the appropriate order."""
        self.setup_rf()   # (disabled for testing) uncomment when RF-source is connected and running
        self.setup_daq_clk()
        self.setup_daq_inputs()
        self.setup_daq_outputs()


    def write_results(self, _arr):
        """Writes the array _ARR to the file path provided in """
        meta = 'H-field ramp:\t{hlow} to {hup}\n \
                f:\t{f}\n \
                samples:\t{n}\n{cols}'.format(
                    hlow=min(self.params['H-set']),
                    hup=max(self.params['H-set']),
                    f=self.params['rf-freq'],
                    n=self.params['N'],
                    cols=self.cols
                )
        ex = os.path.isfile(self.f_name)
        
        with open(self.f_name,'a') as f:
            if ex:
                np.savetxt(f, 
                np.array(_arr), delimiter=',')
            else:
                logging.info("File {} created.".format(self.f_name))
                np.savetxt(f, 
                    np.array(_arr), delimiter=',',
                    header=meta)
        

class WaveForm():
    def __init__(self, _hmax, _n, _hzero = 0) -> None:
        self.hmax = _hmax
        self.N = _n
        self.h_zero = _hzero
    

    def triangle(self):
        """Returns a triangular (single-peak) wave of form /\\
            peak:   self.hmax/100
            len:    self.N"""
        return (signal.sawtooth(
            2*np.pi*np.linspace(0, 1, self.N),
            0.5
            ) + 1) / 2 * self.hmax/100
        
    
    def triangle_10(self):
        """Returns a triangular (single-peak) wave of form with 10% 0 field _/\\_
            peak:   self.hmax/100
            len:    self.N"""
        no_field = int(self.h_zero*self.N)
        ramp = self.N - 2 * no_field
        saw = (signal.sawtooth(2*np.pi*np.linspace(0, 1, ramp), 0.5) + 1) / 2 * self.hmax/100
        no_field_vec = np.zeros(shape=(no_field,))
        return np.append(np.append(no_field_vec, saw), no_field_vec)


