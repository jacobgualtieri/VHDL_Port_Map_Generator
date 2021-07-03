--
-- Automatically generated VHDL testbench
--
library IEEE; use IEEE.std_logic_1164.all;
-- use IEEE.numeric_std.all;

entity andGate2_tb is
end entity;

architecture testbench of andGate2_tb is

constant depth : integer := 2;
constant width : integer := 2;

signal a : std_logic;
signal b : std_logic;
signal y : std_logic;

component andGate2 is
	generic (
		depth : integer := 2;
		width : integer := 2
	);
	port (
		a : in std_logic;
		b : in std_logic;
		y : out std_logic
	);
end component;

begin

end architecture testbench;