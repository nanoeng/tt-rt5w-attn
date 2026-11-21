`default_nettype wire
// Copyright 2022 GlobalFoundries PDK Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module gf180mcu_fd_sc_mcu7t5v0__and2_1( A1, A2, Z );
input A1, A2;
output Z;

	and MGM_BG_0( Z, A1, A2 );

endmodule
// Copyright 2022 GlobalFoundries PDK Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module gf180mcu_fd_sc_mcu7t5v0__and3_1( A1, A2, A3, Z );
input A1, A2, A3;
output Z;

	and MGM_BG_0( Z, A1, A2, A3 );

endmodule
// Copyright 2022 GlobalFoundries PDK Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module gf180mcu_fd_sc_mcu7t5v0__and4_1( A1, A2, A3, A4, Z );
input A1, A2, A3, A4;
output Z;

	and MGM_BG_0( Z, A1, A2, A3, A4 );

endmodule
// Copyright 2022 GlobalFoundries PDK Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module gf180mcu_fd_sc_mcu7t5v0__aoi21_1( A2, ZN, A1, B );
input A1, A2, B;
output ZN;

	wire A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi21_1;

	not MGM_BG_0( A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi21_1, A1 );

	wire B_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi21_1;

	not MGM_BG_1( B_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi21_1, B );

	wire ZN_row1;

	and MGM_BG_2( ZN_row1, A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi21_1, B_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi21_1 );

	wire A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi21_1;

	not MGM_BG_3( A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi21_1, A2 );

	wire ZN_row2;

	and MGM_BG_4( ZN_row2, A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi21_1, B_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi21_1 );

	or MGM_BG_5( ZN, ZN_row1, ZN_row2 );

endmodule
// Copyright 2022 GlobalFoundries PDK Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module gf180mcu_fd_sc_mcu7t5v0__aoi22_1( B2, B1, ZN, A1, A2 );
input A1, A2, B1, B2;
output ZN;

	wire A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1;

	not MGM_BG_0( A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1, A1 );

	wire B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1;

	not MGM_BG_1( B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1, B1 );

	wire ZN_row1;

	and MGM_BG_2( ZN_row1, A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1, B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1 );

	wire B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1;

	not MGM_BG_3( B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1, B2 );

	wire ZN_row2;

	and MGM_BG_4( ZN_row2, A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1, B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1 );

	wire A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1;

	not MGM_BG_5( A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1, A2 );

	wire ZN_row3;

	and MGM_BG_6( ZN_row3, A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1, B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1 );

	wire ZN_row4;

	and MGM_BG_7( ZN_row4, A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1, B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1 );

	or MGM_BG_8( ZN, ZN_row1, ZN_row2, ZN_row3, ZN_row4 );

endmodule
// Copyright 2022 GlobalFoundries PDK Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module gf180mcu_fd_sc_mcu7t5v0__aoi221_1( B2, B1, ZN, C, A2, A1 );
input A1, A2, B1, B2, C;
output ZN;

	wire A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi221_1;

	not MGM_BG_0( A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi221_1, A1 );

	wire B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi221_1;

	not MGM_BG_1( B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi221_1, B1 );

	wire C_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi221_1;

	not MGM_BG_2( C_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi221_1, C );

	wire ZN_row1;

	and MGM_BG_3( ZN_row1, A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi221_1, B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi221_1, C_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi221_1 );

	wire B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi221_1;

	not MGM_BG_4( B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi221_1, B2 );

	wire ZN_row2;

	and MGM_BG_5( ZN_row2, A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi221_1, B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi221_1, C_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi221_1 );

	wire A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi221_1;

	not MGM_BG_6( A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi221_1, A2 );

	wire ZN_row3;

	and MGM_BG_7( ZN_row3, A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi221_1, B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi221_1, C_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi221_1 );

	wire ZN_row4;

	and MGM_BG_8( ZN_row4, A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi221_1, B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi221_1, C_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi221_1 );

	or MGM_BG_9( ZN, ZN_row1, ZN_row2, ZN_row3, ZN_row4 );

endmodule
// Copyright 2022 GlobalFoundries PDK Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module gf180mcu_fd_sc_mcu7t5v0__aoi222_1( C2, C1, B1, ZN, B2, A2, A1 );
input A1, A2, B1, B2, C1, C2;
output ZN;

	wire A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1;

	not MGM_BG_0( A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1, A1 );

	wire B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1;

	not MGM_BG_1( B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1, B1 );

	wire C1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1;

	not MGM_BG_2( C1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1, C1 );

	wire ZN_row1;

	and MGM_BG_3( ZN_row1, A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1, B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1, C1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1 );

	wire C2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1;

	not MGM_BG_4( C2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1, C2 );

	wire ZN_row2;

	and MGM_BG_5( ZN_row2, A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1, B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1, C2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1 );

	wire B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1;

	not MGM_BG_6( B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1, B2 );

	wire ZN_row3;

	and MGM_BG_7( ZN_row3, A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1, B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1, C1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1 );

	wire ZN_row4;

	and MGM_BG_8( ZN_row4, A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1, B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1, C2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1 );

	wire A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1;

	not MGM_BG_9( A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1, A2 );

	wire ZN_row5;

	and MGM_BG_10( ZN_row5, A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1, B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1, C1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1 );

	wire ZN_row6;

	and MGM_BG_11( ZN_row6, A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1, B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1, C2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1 );

	wire ZN_row7;

	and MGM_BG_12( ZN_row7, A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1, B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1, C1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1 );

	wire ZN_row8;

	and MGM_BG_13( ZN_row8, A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1, B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1, C2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi222_1 );

	or MGM_BG_14( ZN, ZN_row1, ZN_row2, ZN_row3, ZN_row4, ZN_row5, ZN_row6, ZN_row7, ZN_row8 );

endmodule
// Copyright 2022 GlobalFoundries PDK Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module gf180mcu_fd_sc_mcu7t5v0__clkinv_1( I, ZN );
input I;
output ZN;

	not MGM_BG_0( ZN, I );

endmodule
// Copyright 2022 GlobalFoundries PDK Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module gf180mcu_fd_sc_mcu7t5v0__dffrnq_1( CLK, D, RN, Q, notifier );
input CLK, D, RN, notifier;
output Q;

	not MGM_BG_0( MGM_P0, RN );

	not MGM_BG_1( MGM_D0, D );

	gf180mcu_fd_sc_mcu7t5v0__udp_n_iq_ff( IQ1, 1'b0, MGM_P0, CLK, MGM_D0, notifier );

	not MGM_BG_2( Q, IQ1 );

endmodule
// Copyright 2022 GlobalFoundries PDK Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module gf180mcu_fd_sc_mcu7t5v0__dffsnq_1( CLK, D, SETN, Q, notifier );
input CLK, D, SETN, notifier;
output Q;

	not MGM_BG_0( MGM_C0, SETN );

	not MGM_BG_1( MGM_D0, D );

	gf180mcu_fd_sc_mcu7t5v0__udp_n_iq_ff( IQ1, MGM_C0, 1'b0, CLK, MGM_D0, notifier );

	not MGM_BG_2( Q, IQ1 );

endmodule
// Copyright 2022 GlobalFoundries PDK Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module gf180mcu_fd_sc_mcu7t5v0__mux2_1( Z, I1, S, I0 );
input I0, I1, S;
output Z;

	wire Z_row1;

	and MGM_BG_0( Z_row1, I0, I1 );

	wire S_inv_for_gf180mcu_fd_sc_mcu7t5v0__mux2_1;

	not MGM_BG_1( S_inv_for_gf180mcu_fd_sc_mcu7t5v0__mux2_1, S );

	wire Z_row2;

	and MGM_BG_2( Z_row2, S_inv_for_gf180mcu_fd_sc_mcu7t5v0__mux2_1, I0 );

	wire Z_row3;

	and MGM_BG_3( Z_row3, I1, S );

	or MGM_BG_4( Z, Z_row1, Z_row2, Z_row3 );

endmodule
// Copyright 2022 GlobalFoundries PDK Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module gf180mcu_fd_sc_mcu7t5v0__nand2_1( A2, A1, ZN );
input A1, A2;
output ZN;

	wire A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__nand2_1;

	not MGM_BG_0( A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__nand2_1, A1 );

	wire A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__nand2_1;

	not MGM_BG_1( A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__nand2_1, A2 );

	or MGM_BG_2( ZN, A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__nand2_1, A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__nand2_1 );

endmodule
// Copyright 2022 GlobalFoundries PDK Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module gf180mcu_fd_sc_mcu7t5v0__nand3_1( A3, ZN, A2, A1 );
input A1, A2, A3;
output ZN;

	wire A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__nand3_1;

	not MGM_BG_0( A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__nand3_1, A1 );

	wire A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__nand3_1;

	not MGM_BG_1( A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__nand3_1, A2 );

	wire A3_inv_for_gf180mcu_fd_sc_mcu7t5v0__nand3_1;

	not MGM_BG_2( A3_inv_for_gf180mcu_fd_sc_mcu7t5v0__nand3_1, A3 );

	or MGM_BG_3( ZN, A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__nand3_1, A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__nand3_1, A3_inv_for_gf180mcu_fd_sc_mcu7t5v0__nand3_1 );

endmodule
// Copyright 2022 GlobalFoundries PDK Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module gf180mcu_fd_sc_mcu7t5v0__nand4_1( A4, ZN, A3, A2, A1 );
input A1, A2, A3, A4;
output ZN;

	wire A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__nand4_1;

	not MGM_BG_0( A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__nand4_1, A1 );

	wire A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__nand4_1;

	not MGM_BG_1( A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__nand4_1, A2 );

	wire A3_inv_for_gf180mcu_fd_sc_mcu7t5v0__nand4_1;

	not MGM_BG_2( A3_inv_for_gf180mcu_fd_sc_mcu7t5v0__nand4_1, A3 );

	wire A4_inv_for_gf180mcu_fd_sc_mcu7t5v0__nand4_1;

	not MGM_BG_3( A4_inv_for_gf180mcu_fd_sc_mcu7t5v0__nand4_1, A4 );

	or MGM_BG_4( ZN, A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__nand4_1, A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__nand4_1, A3_inv_for_gf180mcu_fd_sc_mcu7t5v0__nand4_1, A4_inv_for_gf180mcu_fd_sc_mcu7t5v0__nand4_1 );

endmodule
// Copyright 2022 GlobalFoundries PDK Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module gf180mcu_fd_sc_mcu7t5v0__nor2_1( A2, ZN, A1 );
input A1, A2;
output ZN;

	wire A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__nor2_1;

	not MGM_BG_0( A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__nor2_1, A1 );

	wire A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__nor2_1;

	not MGM_BG_1( A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__nor2_1, A2 );

	and MGM_BG_2( ZN, A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__nor2_1, A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__nor2_1 );

endmodule
// Copyright 2022 GlobalFoundries PDK Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module gf180mcu_fd_sc_mcu7t5v0__nor3_1( A3, ZN, A2, A1 );
input A1, A2, A3;
output ZN;

	wire A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__nor3_1;

	not MGM_BG_0( A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__nor3_1, A1 );

	wire A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__nor3_1;

	not MGM_BG_1( A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__nor3_1, A2 );

	wire A3_inv_for_gf180mcu_fd_sc_mcu7t5v0__nor3_1;

	not MGM_BG_2( A3_inv_for_gf180mcu_fd_sc_mcu7t5v0__nor3_1, A3 );

	and MGM_BG_3( ZN, A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__nor3_1, A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__nor3_1, A3_inv_for_gf180mcu_fd_sc_mcu7t5v0__nor3_1 );

endmodule
// Copyright 2022 GlobalFoundries PDK Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module gf180mcu_fd_sc_mcu7t5v0__nor4_1( A4, ZN, A3, A2, A1 );
input A1, A2, A3, A4;
output ZN;

	wire A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__nor4_1;

	not MGM_BG_0( A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__nor4_1, A1 );

	wire A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__nor4_1;

	not MGM_BG_1( A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__nor4_1, A2 );

	wire A3_inv_for_gf180mcu_fd_sc_mcu7t5v0__nor4_1;

	not MGM_BG_2( A3_inv_for_gf180mcu_fd_sc_mcu7t5v0__nor4_1, A3 );

	wire A4_inv_for_gf180mcu_fd_sc_mcu7t5v0__nor4_1;

	not MGM_BG_3( A4_inv_for_gf180mcu_fd_sc_mcu7t5v0__nor4_1, A4 );

	and MGM_BG_4( ZN, A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__nor4_1, A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__nor4_1, A3_inv_for_gf180mcu_fd_sc_mcu7t5v0__nor4_1, A4_inv_for_gf180mcu_fd_sc_mcu7t5v0__nor4_1 );

endmodule
// Copyright 2022 GlobalFoundries PDK Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module gf180mcu_fd_sc_mcu7t5v0__oai21_1( A2, ZN, A1, B );
input A1, A2, B;
output ZN;

	wire A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai21_1;

	not MGM_BG_0( A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai21_1, A1 );

	wire A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai21_1;

	not MGM_BG_1( A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai21_1, A2 );

	wire ZN_row1;

	and MGM_BG_2( ZN_row1, A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai21_1, A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai21_1 );

	wire B_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai21_1;

	not MGM_BG_3( B_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai21_1, B );

	or MGM_BG_4( ZN, ZN_row1, B_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai21_1 );

endmodule
// Copyright 2022 GlobalFoundries PDK Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module gf180mcu_fd_sc_mcu7t5v0__oai211_1( A2, ZN, A1, B, C );
input A1, A2, B, C;
output ZN;

	wire A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai211_1;

	not MGM_BG_0( A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai211_1, A1 );

	wire A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai211_1;

	not MGM_BG_1( A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai211_1, A2 );

	wire ZN_row1;

	and MGM_BG_2( ZN_row1, A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai211_1, A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai211_1 );

	wire B_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai211_1;

	not MGM_BG_3( B_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai211_1, B );

	wire C_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai211_1;

	not MGM_BG_4( C_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai211_1, C );

	or MGM_BG_5( ZN, ZN_row1, B_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai211_1, C_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai211_1 );

endmodule
// Copyright 2022 GlobalFoundries PDK Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module gf180mcu_fd_sc_mcu7t5v0__oai22_1( B2, B1, ZN, A1, A2 );
input A1, A2, B1, B2;
output ZN;

	wire A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai22_1;

	not MGM_BG_0( A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai22_1, A1 );

	wire A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai22_1;

	not MGM_BG_1( A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai22_1, A2 );

	wire ZN_row1;

	and MGM_BG_2( ZN_row1, A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai22_1, A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai22_1 );

	wire B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai22_1;

	not MGM_BG_3( B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai22_1, B1 );

	wire B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai22_1;

	not MGM_BG_4( B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai22_1, B2 );

	wire ZN_row2;

	and MGM_BG_5( ZN_row2, B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai22_1, B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai22_1 );

	or MGM_BG_6( ZN, ZN_row1, ZN_row2 );

endmodule
// Copyright 2022 GlobalFoundries PDK Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module gf180mcu_fd_sc_mcu7t5v0__oai221_1( B2, B1, C, ZN, A2, A1 );
input A1, A2, B1, B2, C;
output ZN;

	wire A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai221_1;

	not MGM_BG_0( A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai221_1, A1 );

	wire A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai221_1;

	not MGM_BG_1( A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai221_1, A2 );

	wire ZN_row1;

	and MGM_BG_2( ZN_row1, A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai221_1, A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai221_1 );

	wire B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai221_1;

	not MGM_BG_3( B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai221_1, B1 );

	wire B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai221_1;

	not MGM_BG_4( B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai221_1, B2 );

	wire ZN_row2;

	and MGM_BG_5( ZN_row2, B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai221_1, B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai221_1 );

	wire C_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai221_1;

	not MGM_BG_6( C_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai221_1, C );

	or MGM_BG_7( ZN, ZN_row1, ZN_row2, C_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai221_1 );

endmodule
// Copyright 2022 GlobalFoundries PDK Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module gf180mcu_fd_sc_mcu7t5v0__oai31_1( B, A1, ZN, A2, A3 );
input A1, A2, A3, B;
output ZN;

	wire A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai31_1;

	not MGM_BG_0( A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai31_1, A1 );

	wire A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai31_1;

	not MGM_BG_1( A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai31_1, A2 );

	wire A3_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai31_1;

	not MGM_BG_2( A3_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai31_1, A3 );

	wire ZN_row1;

	and MGM_BG_3( ZN_row1, A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai31_1, A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai31_1, A3_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai31_1 );

	wire B_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai31_1;

	not MGM_BG_4( B_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai31_1, B );

	or MGM_BG_5( ZN, ZN_row1, B_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai31_1 );

endmodule
// Copyright 2022 GlobalFoundries PDK Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module gf180mcu_fd_sc_mcu7t5v0__oai32_1( A3, A2, A1, ZN, B1, B2 );
input A1, A2, A3, B1, B2;
output ZN;

	wire A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai32_1;

	not MGM_BG_0( A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai32_1, A1 );

	wire A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai32_1;

	not MGM_BG_1( A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai32_1, A2 );

	wire A3_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai32_1;

	not MGM_BG_2( A3_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai32_1, A3 );

	wire ZN_row1;

	and MGM_BG_3( ZN_row1, A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai32_1, A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai32_1, A3_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai32_1 );

	wire B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai32_1;

	not MGM_BG_4( B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai32_1, B1 );

	wire B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai32_1;

	not MGM_BG_5( B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai32_1, B2 );

	wire ZN_row2;

	and MGM_BG_6( ZN_row2, B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai32_1, B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai32_1 );

	or MGM_BG_7( ZN, ZN_row1, ZN_row2 );

endmodule
// Copyright 2022 GlobalFoundries PDK Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module gf180mcu_fd_sc_mcu7t5v0__or2_1( A1, A2, Z );
input A1, A2;
output Z;

	or MGM_BG_0( Z, A1, A2 );

endmodule
// Copyright 2022 GlobalFoundries PDK Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module gf180mcu_fd_sc_mcu7t5v0__or3_1( A1, A2, A3, Z );
input A1, A2, A3;
output Z;

	or MGM_BG_0( Z, A1, A2, A3 );

endmodule
// Copyright 2022 GlobalFoundries PDK Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module gf180mcu_fd_sc_mcu7t5v0__or4_1( A1, A2, A3, A4, Z );
input A1, A2, A3, A4;
output Z;

	or MGM_BG_0( Z, A1, A2, A3, A4 );

endmodule
// Copyright 2022 GlobalFoundries PDK Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module gf180mcu_fd_sc_mcu7t5v0__xnor2_1( A2, A1, ZN );
input A1, A2;
output ZN;

	wire ZN_row1;

	and MGM_BG_0( ZN_row1, A1, A2 );

	wire A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__xnor2_1;

	not MGM_BG_1( A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__xnor2_1, A1 );

	wire A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__xnor2_1;

	not MGM_BG_2( A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__xnor2_1, A2 );

	wire ZN_row2;

	and MGM_BG_3( ZN_row2, A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__xnor2_1, A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__xnor2_1 );

	or MGM_BG_4( ZN, ZN_row1, ZN_row2 );

endmodule
// Copyright 2022 GlobalFoundries PDK Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module gf180mcu_fd_sc_mcu7t5v0__xor2_1( A2, A1, Z );
input A1, A2;
output Z;

	wire A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__xor2_1;

	not MGM_BG_0( A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__xor2_1, A2 );

	wire Z_row1;

	and MGM_BG_1( Z_row1, A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__xor2_1, A1 );

	wire A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__xor2_1;

	not MGM_BG_2( A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__xor2_1, A1 );

	wire Z_row2;

	and MGM_BG_3( Z_row2, A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__xor2_1, A2 );

	or MGM_BG_4( Z, Z_row1, Z_row2 );

endmodule
// tie cells (functional; no _N suffix in the library)
module gf180mcu_fd_sc_mcu7t5v0__tiel(ZN); output ZN; assign ZN = 1'b0; endmodule
module gf180mcu_fd_sc_mcu7t5v0__tieh(Z);  output Z;  assign Z  = 1'b1; endmodule
