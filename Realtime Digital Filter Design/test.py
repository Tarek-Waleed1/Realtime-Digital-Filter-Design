def applied_allpass_filter(self):
    if len(allpasslist) != 0:
        self.correctedphase.clear()

    b = convolve(self.num, [-self.all_pass_values, 1.0])
    a = convolve(self.den, [1.0, -self.all_pass_values])
    w1, h1 = freqz(b, a, worN=10000)
    self.appliedfiltervalue = np.angle(h1)
    self.correctedphase.plot(self.appliedfiltervalue)