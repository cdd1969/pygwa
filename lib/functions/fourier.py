from __future__ import division
import numpy as np
import pandas as pd
import matplotlib.pylab as plt
from numpy import cos, pi, arccos, abs
from scipy import fftpack



def fourier_analysis(sig, timestep, N_MAX_POW=1, generate_plot=False, display_plot=False, **kwargs):
    ''' Calculate sinusoidal signal spectrum using Fast Fourier Transformation,
    pick certain number of frequencies with maximum power (N = N_MAX_FREQ)
    and return an equation in form:
        y = H0 + A1*cos(omega1*t+phi1) + A2*cos(omega2*t+phi2) + ... + A_i*cos(omega_i*t+phi_i)
    where i = N_MAX_FREQ.

    Also can plot a nice graphic.

    Args:
    -----
        sig (1D - array of floats) [m AMSL]:
            Measured with equal intervals values of the signal of interest. In our case
            this array contains measured values of the water level in [m AMSL].
        timestep (int) [s]:
            Number of seconds between two measurements in array `sig` (i.e. measurement interval)
        N_MAX_POW (int):
            Number of frequencies with maximum power to pick for computing the curve equation.
            Example:
            N_MAX_POW = 1 >>> will compute following equation:
            y = H0 + A1*cos(omega1*t+phi1), where
                A1, omega1, phi1 - params of sinusoid which frequency has maximal power

            N_MAX_POW = 3 >>> will compute following equation:
            y = H0 + A1*cos(omega1*t+phi1) + A2*cos(omega2*t+phi2) +  A3*cos(omega3*t+phi3), where
                A1, omega1, phi1 - params of sinusoid which frequency has maximal power
                A2, omega2, phi2 - params of sinusoid which frequency has second maximal power
                A3, omega3, phi3 - params of sinusoid which frequency has third maximal power
        generate_plot (bool):
            flag to visualize result

        **kwargs:
            are passed to plot functions (see code below)

    Return:
    -------
        EQUATION (dict):
            dictionary with estimated parameters.
                EQUATION['0']['A'] >>> freq=0 amplitude (SPECIAL CASE!)
                EQUATION['1']['A'] >>> ampl1
                EQUATION['1']['omega'] >>> omega1
                EQUATION['1']['phi'] >>> phi1
                EQUATION['2']['A'] >>> ampl2
                EQUATION['2']['omega'] >>> omega2
                EQUATION['2']['phi'] >>> phi2
                etc...
        f_str (str):
            string of the generated function
        f (function):
            estimated function `f(t)` that defines water-level (is generated
            from `exec(f_str) in globals(), locals()`)

    '''
    if N_MAX_POW < 1:
        return
    msize = kwargs.get('markersize', 2)
    marker = kwargs.get('marker', 'x')
    hz2day = kwargs.get('convert2day', True)
    datetime_plot = kwargs.get('datetime_plot', None)

    # consider reading example here
    # http://www.scipy-lectures.org/intro/scipy.html#fast-fourier-transforms-scipy-fftpack
    sig_fft = fftpack.fft(sig)  # compute FFT

    # generate sampling frequencies
    sample_freq = fftpack.fftfreq(len(sig), d=timestep)
    # The signal is supposed to come from a real function so the Fourier transform will be symmetric
    # Because the resulting power is symmetric, only the positive part of the spectrum needs to be used for finding the frequency
    pidxs = np.where(sample_freq > 0)  # get indexes where sample_frequency >0, we will treat sample_freq=0 in special case
    freqs = sample_freq[pidxs]
    power = abs(sig_fft)[pidxs]

    # ---------------------------------------
    # get maximum threshold power (each frequency which has power below this value will be ignored)
    thres_power = np.sort(power)[-N_MAX_POW]
    weak_power_idxs = np.where(abs(sig_fft) < thres_power)
    sig_fft[weak_power_idxs] = 0

    # now loop over FFT solution (already with ingored "weak frequencies") and get the curve equation params
    EQUATION = {}
    for i, complex_val in enumerate(sig_fft):
        a = abs(complex_val)/len(sig_fft)  # amplitude
        omega = sample_freq[i]*2*pi  # angular velocity in [rad/s]
        
        if complex_val == 0 or omega <= 0:  # we ignore "weak frequencies" (==0) and negative symmetrical frequencies (omega <0)
            continue

        phi = arccos(complex_val.real/abs(complex_val))
        phi *= 1 if complex_val.imag >= 0 else -1
        
        EQUATION['{0}'.format(i+1)] = {}
        EQUATION['{0}'.format(i+1)]['A']     = a*2.  #amplitude in `sig` units (multiplied by 2 due to ignorance of negative symmetrical frequencies)
        EQUATION['{0}'.format(i+1)]['omega'] = omega  # angular velocity in [rad/sec]
        EQUATION['{0}'.format(i+1)]['phi']   = phi  # phase shift in [rad]

    # finally treat freq=0 special case
    EQUATION['0'] = {}
    EQUATION['0']['A'] = abs(sig_fft[np.where(sample_freq == 0)])/len(sig)
    

    # now generate computation function
    def generate_sig_simplified_function(EQUATION):
        ''' EQUATION dictionary is created above
        y = H0 + A1*cos(omega1*t+phi1) + A2*cos(omega2*t+phi2) + ... + A_i*cos(omega_i*t+phi_i)
        '''
        STR = u"def generated_function(t): return (np.zeros({0}) + {1}".format(len(t), EQUATION['0']['A'])
        for k, v in EQUATION.iteritems():
            if k == '0':
                continue
            STR += u" + {0}*np.cos({1}*t+{2})".format(v['A'], v['omega'], v['phi'])
        STR += ')'
        exec(STR) in globals(), locals()
        return (STR, generated_function)

    # simulate time_vector [seconds]
    t = np.arange(0, len(sig)*timestep, timestep)
    # calculate y-values with simplified equation
    f_str, f = generate_sig_simplified_function(EQUATION)
    y = f(t)

    fig = None
    if generate_plot:
        ampl  = power/len(sig)*2.  # convert power to amplitude
        freqs = np.insert(freqs, 0, 0.)  # insert special case freq==0
        ampl  = np.insert(ampl, 0, EQUATION['0']['A'])  # insert special case freq==0

        fig, axes = plt.subplots(2)
        ax1, ax2 = axes

        if hz2day:
            ax1.plot(freqs*60*60*24, ampl, marker=marker, markersize=msize)
            ax1.set_xlabel('Frequency [cycles/day]')
        else:
            ax1.plot(freqs, ampl, marker=marker, markersize=msize)
            ax1.set_xlabel('Frequency [Hz]')
        ax1.set_title('Amplitude Spectral Density')
        ax1.set_ylabel('Amplitude [m]')
        ax1.set_yscale('log')

        if datetime_plot is None:
            T = t/3600.
            ax2.set_xlabel('Time [hours]')
        else:
            T = datetime_plot
        ax2.scatter(T, sig, color='g', label='Original signal', s=5)
        #ax2.plot(fftpack.ifft(sig_fft), 'b-.', lw=2., label='Fitted signal')
        ax2.plot(T, y, 'r-', lw=2., label='Fitted signal (simplified)')
        ax2.plot(T, y-sig, 'm--', lw=1., label='Residuals')
        ax2.set_title('Timeseries')
        ax2.set_ylabel('Water Level [m AMSL]')
        
        plt.legend()
        fig.tight_layout()
        if display_plot:
            fig.show()
    return (EQUATION, f_str, f, fig)



def pandas_fourier_analysis(df, sig_name, date_name=None, ranges=(), **kwargs):
    ''' wrapper to function "fourier_analysis()".
    Automatically processes pandas DataFrame. Features:
        - find timestep
        - slice data based on datetime ranges

    Args:
    -----
        df (pd.DataFrame):
            data
        sig_name (str):
            name of the column in `df` with investigated signal values
        date_name (str|None):
            name of the column in `df` with datetime information. If `None`
            will try to use datetime indexes
        ranges (tuple(np.datetime64, np.datetime64)):
            tuple of two datetime objects representing slice region. The data
            will be sliced first before processing based on these values.
            If emty (ranges=()) then all timespan will be used
        **kwargs:
            are passed to "fourier_analysis()"

    Return:
    -------
        pd.DataFrame:
            Dataframe with three columns : "Amplitude" (A), "Angular Velocity" (Omega),
            "Phase Shift" (Phi). The data in these columns can be used to create curve
            equation in following way:
                y = A[0] + A[1]*cos(Omega[1]*t+Phi[1]) + A[2]*cos(Omega[2]*t+Phi[2]) + ... +
                    A[n]*cos(Omega[n]*t+Phi[n])
                Note:
                    first row contains only A value (Omega and Phi are NaN), since it represents
                    constant
        f_str (str):
            string representation of the computed function. Function can be generated with:
                exec(f_str)
        f (function):
            function y=f(t) which accepts t as array of time value in seconds
        fig (matplotlib figure|None):
            instance of the generated figure or None. Is usefull for displaying later
    '''
    NEW_DF_CREATED = False
    if date_name is None and type(df.index) == pd.tseries.index.DatetimeIndex:
        time_vector = df.index
        timestep = df.index.diff()[1].total_seconds()  # we assume that dt is uniform al over the df
    elif date_name is not None:
        time_vector = df[date_name]
        timestep = df[date_name].diff()[1].total_seconds()  # we assume that dt is uniform al over the df
        if ranges:
            df = df.set_index(date_name)
            NEW_DF_CREATED = True
    else:
        raise ValueError('Set proper column name to param `date_name` or None if datetime index')

    if ranges:
        time_vector = time_vector[ranges[0]:ranges[1]].values
        sig = df[sig_name][ranges[0]:ranges[1]].values
    else:
        time_vector = time_vector.values
        sig = df[sig_name]

    EQ, f_str, f, fig = fourier_analysis(sig, timestep, datetime_plot=time_vector, **kwargs)
    

    # now create Pandas Dataframe out of equation so we can quickly parse it to excel
    A = []
    omega = []
    phi = []
    for k in sorted(EQ.keys()):
        if k == '0':
            A.append(EQ[k]['A'][0])  # no idea why we need to set index [0]
            omega.append(float('NaN'))
            phi.append(float('NaN'))
        else:
            A.append(EQ[k]['A'])
            omega.append(EQ[k]['omega'])
            phi.append(EQ[k]['phi'])
    A = np.array(A)
    omega = np.array(omega)
    phi = np.array(phi)

    if NEW_DF_CREATED:
        del df
    return (pd.DataFrame({'Amplitude [m]': A, 'Angular Velocity [rad/s]': omega, 'Phase shift [rad]': phi}), f_str, f, fig)




if __name__ == '__main__':
    t = np.arange(0, 100, 0.01)
    sig = 1. + 2*cos(2*pi/360*50*t + 0.01) + 4*cos(2*pi/360*120*t - 0.01)
    fourier_analysis(sig, 1, N_MAX_POW=5, plot=True, convert2day=True, marker=None, markersize=10)
