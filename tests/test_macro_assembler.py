"""Build and exercise the standalone C assembler against independent CMC8 sources."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def read_ihex(text):
    result = {}
    ended = False
    for line in text.splitlines():
        assert line.startswith(':')
        record = bytes.fromhex(line[1:])
        assert sum(record) & 255 == 0
        count, high, low, kind = record[:4]
        assert len(record) == count+5
        if kind == 1:
            assert count == 0
            ended = True
        else:
            assert kind == 0 and not ended
            address = (high << 8) | low
            for offset, value in enumerate(record[4:-1]):
                assert address+offset not in result
                result[address+offset] = value
    assert ended
    return result


class MacroAssemblerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('cc')
        cmake = shutil.which('cmake')
        if compiler is None or cmake is None:
            raise unittest.SkipTest('CMake and a C99 compiler are required to test the standalone assembler')
        cls.build = tempfile.TemporaryDirectory()
        cls.executable = Path(cls.build.name)/'cmc8asm'
        subprocess.run([cmake,'-S',str(ROOT/'assembler'),'-B',cls.build.name,
                        '-DCMAKE_BUILD_TYPE=Release',f'-DCMAKE_C_COMPILER={compiler}',
                        '-DCMAKE_C_FLAGS=-Werror'],check=True,capture_output=True,text=True)
        subprocess.run([cmake,'--build',cls.build.name],
                       check=True,capture_output=True,text=True)

    @classmethod
    def tearDownClass(cls):
        cls.build.cleanup()

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name)

    def run_source(self, source, *, options=(), ok=True, output='out.hex'):
        filename = self.path/'test.asm'
        filename.write_text(source)
        result = subprocess.run([str(self.executable),'-o',str(self.path/output),*options,str(filename)],
                                capture_output=True,text=True)
        if ok:
            self.assertEqual(result.returncode,0,result.stderr)
        else:
            self.assertNotEqual(result.returncode,0,result.stdout)
        return result

    def hex_source(self, source, **kwargs):
        self.run_source(source,**kwargs)
        return read_ihex((self.path/'out.hex').read_text())

    def test_every_defined_encoding_matches_the_independent_catalogue(self):
        catalogue = json.loads((ROOT/'specification/instructions.json').read_text())
        page, offset, expected, lines = 0, 0, {}, []
        page_branches = {'JMP','BZ0','BZ1','BL0','BL1'}
        immediate = {'LRI','ANI','XRI'}
        for entry in catalogue['instructions']:
            for opcode in range(256):
                if opcode & entry['mask'] != entry['value']:
                    continue
                name, length = entry['mnemonic'], entry['length_bytes']
                if offset+length > 256:
                    page += 1
                    offset = 0
                    lines.append(f'PAGE {page}')
                operands, byte = '', 0x80
                if name in page_branches:
                    operands = f'{opcode & 3},0x80'
                elif name in {'BT0','BT1'}:
                    operands = f'T{opcode & 3},0x80'
                elif name in {'BB0','BB1'}:
                    operands = f'R{opcode & 7},0x80'
                elif name in {'SCW','SCS'}:
                    operands, byte = '#0xA6', 0xA6
                elif name == 'JSR':
                    operands = '0x80'
                elif 'R' in entry['pattern']:
                    operands = f'R{opcode & 7}'
                    if length == 2:
                        operands += ',#0xA6' if name in immediate else ',0x80'
                        if name in immediate:
                            byte = 0xA6
                lines.append(f'{name} {operands}')
                expected[page*256+offset] = opcode
                if length == 2:
                    expected[page*256+offset+1] = byte
                offset += length
        self.assertEqual(self.hex_source('\n'.join(lines)),expected)

    def test_traffic_source_reproduces_all_literal_book_bytes(self):
        result = subprocess.run([str(self.executable),'-o',str(self.path/'traffic.hex'),
                                 str(ROOT/'examples/traffic.asm')],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        source = json.loads((ROOT/'specification/traffic-program.json').read_text())
        expected = {int(c['address'],8):int(c['byte'],8) for c in source['cells']}
        self.assertEqual(read_ihex((self.path/'traffic.hex').read_text()),expected)

    def test_forward_labels_and_equ_chains(self):
        image = self.hex_source('''
            alias EQU target
            count EQU later+1
            later EQU 41
            JMP alias
            BYTE count
            target: LRI X,#LOW(target)
            end_label:
            size EQU end_label-target
            ASSERT size==2
        ''')
        self.assertEqual(image,{0:0xF0,1:3,2:42,3:0x27,4:3})

    def test_expressions_character_and_string_data(self):
        image = self.hex_source(r'''
            BYTE (2+3)*4, 0b1010, $AA, %11, 077o, 20h, <0x3FE, >0x3FE
            BYTE LOW(-1),HIGH(-1),PAGEOF(0x3FF),010,1<<3+1
            BYTE "hi;ok,yes",'\n','\xFF' ; actual comment
            WORD 0x3FF
            ASSERT (3*4==12) && (2!=3) && (1<=1)
        ''')
        expected = bytes([20,10,170,3,63,32,254,3,255,255,3,10,16])+b'hi;ok,yes'+bytes([10,255,255,3])
        self.assertEqual(bytes(image.values()),expected)

    def test_macro_parameters_local_labels_and_nested_calls(self):
        image = self.hex_source(r'''
            MACRO LOAD reg,value
                ; This comment has a literal \not_a_parameter and %%not_a_label.
                LRI \reg,#\value
            ENDM
            MACRO COUNT count
                LOAD R4,\count
            %%again: DCR R4
                BZ0 %%again
            ENDM
            first: COUNT 2
            COUNT 3
        ''',options=('-m',str(self.path/'out.map'),'-l',str(self.path/'out.lst')))
        self.assertEqual(bytes(image.values()),bytes([0x24,2,0xA4,0xE0,2,0x24,3,0xA4,0xE0,7]))
        mapping = (self.path/'out.map').read_text()
        self.assertIn('__M1_again',mapping)
        self.assertIn('__M3_again',mapping)
        self.assertIn('expanded from',(self.path/'out.lst').read_text())

    def test_repetition_and_preprocessing_conditions(self):
        image = self.hex_source(r'''
            COUNT EQU 3
            IF COUNT == 3
                REPT COUNT
                %%here: BYTE \@
                ENDR
            ELSE
                INCLUDE "must-not-be-opened.inc"
            ENDIF
            IFDEF COUNT
                BYTE 9
            ENDIF
            IFNDEF absent
                BYTE 10
            ENDIF
        ''')
        self.assertEqual(bytes(image.values()),bytes([1,2,3,9,10]))

    def test_relative_includes_and_include_guards(self):
        library = self.path/'library'
        library.mkdir()
        (library/'port.inc').write_text(r'''
            IFNDEF PORT_INC
            PORT_INC EQU 1
            INCLUDE "codes.inc"
            MACRO LAMP value
                LRI R3,#\value
                SRD R3,PORT
            ENDM
            ENDIF
        ''')
        (library/'codes.inc').write_text('PORT EQU 4\n')
        image = self.hex_source('INCLUDE "port.inc"\nINCLUDE "port.inc"\nLAMP 044o\n',
                                options=('-I',str(library)))
        self.assertEqual(bytes(image.values()),bytes([0x23,0o44,0x1B,4]))

    def test_page_counters_and_automatic_page_fields(self):
        image = self.hex_source('''
            zero: NOP
            PAGE 3
            ORG 020o
            worker: NOP
            JMP zero
            BZ0 worker
            BL1 3,worker
            PAGE 0
            BYTE 42
            ORGA worker+7
            SCS #0x69
        ''')
        self.assertEqual(image,{0:0,1:42,0x310:0,0x311:0xF0,0x312:0,
                                0x313:0xE3,0x314:0x10,0x315:0xEF,0x316:0x10,
                                0x317:9,0x318:0x69})

    def test_low_page_label_is_not_silently_treated_as_an_offset(self):
        for mnemonic in ('JSR','BB0 R3,','BT1 T1,','LRM R3,','LRS R3,'):
            text = f'zero: NOP\nPAGE 3\nORG 64\n{mnemonic} zero\n'
            result = self.run_source(text,ok=False)
            self.assertIn('cross-page',result.stderr)
        for expression in ('+zero','zero*1','0-zero','-(-zero)'):
            result = self.run_source(f'zero:NOP\nPAGE 3\nJSR {expression}\n',ok=False)
            self.assertIn('cross-page',result.stderr)
        image = self.hex_source('zero:NOP\nPAGE 3\nJSR LOW(zero)\n')
        self.assertEqual(image[0x300],0x0C)
        self.assertEqual(image[0x301],0)

    def test_page_validation_and_explicit_offset_semantics(self):
        result = self.run_source('JMP 0,elsewhere\nPAGE 3\nelsewhere:NOP\n',ok=False)
        self.assertIn('explicit page disagrees',result.stderr)
        image = self.hex_source('PAGE 3\nJMP 16\n')
        self.assertEqual(image,{0x300:0xF3,0x301:16})
        result = self.run_source('LRD R3,0x180\n',ok=False)
        self.assertIn('outside',result.stderr)

    def test_wrap_is_explicit_and_stays_on_the_same_page(self):
        self.assertIn('crosses a page',self.run_source('ORG 255\nLRI R3,#42\n',ok=False).stderr)
        image = self.hex_source('PAGE 3\nWRAP ON\nORG 255\nstart:LRI R3,#42\nJMP start\n')
        self.assertEqual(image,{0x300:42,0x301:0xF3,0x302:255,0x3FF:0x23})
        from cmc8.versions.v018 import InstructionSimulator,Memory,State
        state = State(n=0,pg=3,ir=0)
        state.registers[0] = 255
        cpu = InstructionSimulator(state,Memory(program=image))
        cpu.run_instruction()
        self.assertEqual((cpu.state.registers[0],cpu.state.registers[3]),(1,42))
        cpu.run_instruction()
        self.assertEqual(cpu.state.registers[0],255)

    def test_holes_reservations_binary_fill_and_overlaps(self):
        source = 'BYTE 1\nRES 2\nFILL 2,7\nORGA 0x200\nWORD 0x1234\n'
        self.run_source(source,options=('-f','bin','--fill','0xA6'),output='out.bin')
        data = (self.path/'out.bin').read_bytes()
        self.assertEqual(len(data),1024)
        self.assertEqual(data[:5],bytes([1,0xA6,0xA6,7,7]))
        self.assertEqual(data[0x200:0x202],bytes([0x34,0x12]))
        image = self.hex_source(source)
        self.assertEqual(image,{0:1,3:7,4:7,0x200:0x34,0x201:0x12})
        result = self.run_source('RES 4\nORG 0\nBYTE 1\n',ok=False)
        self.assertIn('overlapping',result.stderr)

    def test_end_skips_following_preprocessing_and_assembly(self):
        self.assertEqual(self.hex_source('NOP\nEND\nINCLUDE "not-present"\nINVALID\n'),{0:0})

    def test_errors_preserve_existing_outputs_and_show_macro_context(self):
        output = self.path/'out.hex'
        output.write_text('existing result\n')
        result = self.run_source(r'''
            MACRO BAD reg
                LRI \reg,#256
            ENDM
            BAD R3
        ''',ok=False)
        self.assertIn('expanded from',result.stderr)
        self.assertIn('outside',result.stderr)
        self.assertEqual(output.read_text(),'existing result\n')

    def test_invalid_programs_are_diagnosed(self):
        programs = {
            'NOP 1':'expects 0', 'LRI R8,1':'outside', 'BT1 T4,0':'outside',
            'BYTE missing':'undefined symbol', 'x:NOP\nx:NOP':'duplicate symbol',
            'a EQU b\nb EQU a\nBYTE a':'circular EQU', 'BYTE 1/0':'division by zero',
            'BYTE 1<<64':'shifts need', 'BYTE 9223372036854775807+1':'overflow',
            'BYTE (-9223372036854775807-1)*-1':'overflow',
            'MACRO A\n A\nENDM\nA':'depth exceeds',
            'IF 1\nNOP':'missing ENDIF', 'REPT -1\nNOP\nENDR':'REPT count',
            'MACRO X a,a\nENDM':'duplicate macro parameter',
            'MACRO NOP\nENDM':'already used', 'PAGE 4':'outside',
            'ASSERT 0,"bad assertion"':'bad assertion',
            'MACRO M a\nBYTE \\b\nENDM\nM 1':'unknown macro parameter',
        }
        for source, message in programs.items():
            with self.subTest(source=source):
                result = self.run_source(source+'\n',ok=False)
                self.assertIn(message,result.stderr)

    def test_output_paths_cannot_replace_root_or_included_sources(self):
        source = self.path/'test.asm'
        source.write_text('NOP\n')
        result = subprocess.run([str(self.executable),'-o',str(self.path/'./test.asm'),str(source)],
                                capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(source.read_text(),'NOP\n')
        header = self.path/'header.inc'
        header.write_text('MACRO M\nNOP\nENDM\n')
        source.write_text('INCLUDE "header.inc"\nNOP\n')
        result = subprocess.run([str(self.executable),'-o',str(header),str(source)],
                                capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('overwrite',result.stderr)
        self.assertEqual(header.read_text(),'MACRO M\nNOP\nENDM\n')

    def test_page_and_absolute_origin_directives_have_distinct_meanings(self):
        image = self.hex_source('PAGE 3\nORG 16\nBYTE 1\nORGA 16\nBYTE 2\n')
        self.assertEqual(image,{16:2,0x310:1})
        result = self.run_source('ORG 256\n',ok=False)
        self.assertIn('outside',result.stderr)
        result = self.run_source('here:NOP\nORG here\n',ok=False)
        self.assertIn('use LOW(label) or ORGA',result.stderr)

    def test_cross_page_call_trampoline_runs_on_the_simulator(self):
        example = ROOT/'assembler/examples/paging.asm'
        result = subprocess.run([str(self.executable),'-o',str(self.path/'out.hex'),str(example)],
                                capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        from cmc8.versions.v018 import InstructionSimulator,Memory,State
        state = State(n=0,pg=0,ir=0)
        state.registers[0] = 0
        cpu = InstructionSimulator(state,Memory(program=read_ihex((self.path/'out.hex').read_text())))
        for _ in range(5):
            cpu.run_instruction()
        self.assertEqual((cpu.state.n,cpu.state.pg,cpu.state.registers[0],cpu.state.registers[3]),
                         (0,0,2,0x69))

    def test_empty_input_maps_and_utf8_bom(self):
        self.assertEqual(self.hex_source('',options=('-m',str(self.path/'empty.map'))),{})
        self.assertIn('Absolute symbols',(self.path/'empty.map').read_text())
        self.assertEqual(self.hex_source('\ufeffNOP\n'),{0:0})

    def test_stdout_hex_and_help(self):
        filename = self.path/'test.asm'
        filename.write_text('NOP\n')
        result = subprocess.run([str(self.executable),'-q','-o','-',str(filename)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(read_ihex(result.stdout),{0:0})
        help_result = subprocess.run([str(self.executable),'--help'],capture_output=True,text=True)
        self.assertEqual(help_result.returncode,0)
        self.assertIn('Intel HEX',help_result.stdout)


if __name__ == '__main__':
    unittest.main()
