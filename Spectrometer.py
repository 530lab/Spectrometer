from SerialClass import SerialClass


class Spectrometer:
    program_offset = [0.04, -0.32, 0.054]

    def __init__(self):
        with open('cfg.txt', 'r') as file:
            self.stage1_offset, self.stage2_offset, self.stage3_offset = \
                [float(x.split(sep='=')[1]) for x in file.readlines()]
        self.stage1_offset += self.program_offset[0]
        self.stage2_offset += self.program_offset[1]
        self.stage3_offset += self.program_offset[2]
        self.stage1 = SerialClass('COM5')
        self.stage2 = SerialClass('COM6')
        self.stage3 = SerialClass('COM7')

    def goto(self, position):
        goto_stage1 = position + self.stage1_offset
        goto_stage2 = position + self.stage2_offset
        goto_stage3 = position + self.stage3_offset
        self.stage1.query(str(goto_stage1) + ' goto')
        self.stage2.query('-' + str(goto_stage2) + ' goto')
        self.stage3.query(str(goto_stage3) + ' goto')


if __name__ == '__main__':
    dev = Spectrometer()
    print(dev.stage2.query('side-ent-slit ?microns'))
    #print(dev.stage2.query('side-ent-slit 500 microns'))
    #print(dev.stage3.query('exit-mirror side'))
    #print(dev.stage2.query('side-ent-slit ?microns'))