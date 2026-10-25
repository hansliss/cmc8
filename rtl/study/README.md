# Base control decoder study

Generated from the selected v018 control behavior by:

```sh
python3 -m tools.build_control_pla
python3 -m unittest tests.test_control_pla
```

The VHDL-2008 and Verilog files describe the same combinational AND/OR
function. They are research artifacts, not a complete processor/controller.
See [the design study](../../docs/pla-control-study.md) for bit allocation,
335-term results, exact scope, remaining dynamic controls and validation limits.
No HDL compiler or FPGA synthesis tool was available for this pass.
