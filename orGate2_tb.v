/**
 * Automatically generated Verilog testbench
 */
module orGate2_tb ();

localparam depth = 4'd2;
localparam width = 4'd2;

wire a;		//input
wire b;		//input
wire y;		//output

// Unit Under Test
orGate2 #(
	.depth	(depth),
	.width	(width)
) UUT (
	.a	(a),
	.b	(b),
	.y	(y)
);
