"""Validate a completed CLI run and draw its observed lamp events as an SVG."""
import argparse
from html import escape
import json
from pathlib import Path


def validate(report):
    writes = report['port_writes']
    assert [w['value'] for w in writes] == [0o044,0o046,0o041,0o201,0o301,0o041,0o044]
    assert all(w['address'] == 4 for w in writes)
    assert report['final_n'] == 0 and report['final_pc_octal'] == '004'
    assert report['final_ed4_octal'] == '044'
    count = report['delay_count_decimal']
    if report['literal_book_bytes']:
        assert count == 0o172
    cycles = 4+count*(256*5+5)+2
    assert report['delay_routine_cycles'] == cycles
    for i,repeats in enumerate((1,2,3,2,1),start=1):
        actual = writes[i+1]['subdivision']-writes[i]['subdivision']
        assert actual == 8*(repeats*(cycles+3)+6), (i,actual)
    assert all(w['time_ns'] == w['subdivision']*8000 for w in writes)
    assert report['elapsed_ns'] == report['subdivisions']*8000
    # These CLI scenarios use three complete idle polling loops before and
    # after a single accepted demand. T3 adds one false T1 branch.
    extra = int(report.get('sensor',1) == 3)
    assert report['subdivisions'] == 880+72*cycles+16*extra
    assert report['events'] == 44+9*(3+514*count)+extra


def render(report,path):
    validate(report)
    title = 'Literal figure8.6 program' if report['literal_book_bytes'] else 'Explicit shortened-delay test fixture'
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1160" height="690" viewBox="0 0 1160 690">',
             '<rect width="1160" height="690" fill="white"/>',
             '<style>text{font-family:Arial,sans-serif;fill:#193049}.small{font-size:16px}</style>',
             '<text x="35" y="42" font-size="26">CMC8 traffic lights — observed ED4 writes</text>',
             f'<text x="35" y="74" class="small">{escape(title)}; v018, 8 µs per subdivision</text>']
    for x,label in [(35,'Time (s)'),(220,'ED4 octal'),(380,'Main road R/Y/G'),(650,'Side road R/Y/G'),(915,'Until next write')]:
        parts.append(f'<text x="{x}" y="122" class="small">{label}</text>')
    colors = ['#d32f2f','#edb20a','#20954f']
    writes = report['port_writes']
    for i,event in enumerate(writes):
        y = 170+61*i
        parts.append(f'<path d="M30 {y+27} H1120" stroke="#dfe7ed"/>')
        parts.append(f'<text x="35" y="{y+6}" class="small">{event["time_ns"]/1e9:.6f}</text>')
        parts.append(f'<text x="220" y="{y+6}" class="small">{event["value"]:03o}</text>')
        for offset,start in [(380,0),(650,5)]:
            for bit,color in enumerate(colors):
                on = bool(event['value'] & (1 << (start+bit)))
                fill = color if on else '#e4e9ed'
                parts.append(f'<circle cx="{offset+25+60*bit}" cy="{y}" r="16" fill="{fill}" stroke="#6c7a86"/>')
        duration = (f'{(writes[i+1]["time_ns"]-event["time_ns"])/1e9:.6f}s'
                    if i+1 < len(writes) else 'Idle polling')
        parts.append(f'<text x="915" y="{y+6}" class="small">{duration}</text>')
    parts += [f'<text x="35" y="635" class="small">{report["subdivisions"]:,} executed subdivisions; '
              f'{report["events"]:,} CPU events; all seven observed states and interval counts checked.</text>',
              '<text x="35" y="665" class="small">Green/yellow overlaps follow the book. The diagram reports simulation, not measured hardware.</text>',
              '</svg>']
    path.write_text('\n'.join(parts)+'\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report',type=Path)
    parser.add_argument('svg',type=Path)
    args=parser.parse_args()
    report=json.loads(args.report.read_text())
    render(report,args.svg)
    print(f'Checked lamp sequence, exact intervals and all {report["subdivisions"]:,} subdivisions.')


if __name__=='__main__':
    main()
