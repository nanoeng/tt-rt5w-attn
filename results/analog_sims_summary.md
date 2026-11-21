# RT5W physical-design verification (2026-11-19 19:19 UTC)

| | area | check | result | criterion |
|---|---|---|---|---|
| PASS | bias | I_u, keep-alive @ typical 27 C | 125.7 nA, gated 1.24 % | I_u 125 nA x PTAT/R (+-40 % corners); gated 0.5..2 % |
| PASS | idac | monotonic / INL @ typical 27 C | INL 0.000 LSB, gain +4.0 % | monotonic, INL < 0.5 LSB |
| PASS | keycell | gain at k=1 over q @ typical 27 C | spread 0.99 % | q-independent within 5 % (buffered gate offset, O1) |
| PASS | softmax | share error / V_B fit @ typical 27 C | 2.89 LSB, V_B residual 1.3 mV | <= 4 LSB vs softmax(x); V_B linear in LSE within 3 mV |
| PASS | readout | SAR codes vs model @ typical 27 C | max |err| 1 LSB | <= 1 LSB (12 codes, mid-step inputs) |
| PASS | vbbuf | ua[1] - V_B, settling @ typical 27 C | 4.0 mV, 5.8 us | <= 6 mV over 1.2..2.3 V, < 20 us |
| PASS | bias | I_u, keep-alive @ ss -40 C | 92.7 nA, gated 1.35 % | I_u 125 nA x PTAT/R (+-40 % corners); gated 0.5..2 % |
| PASS | idac | monotonic / INL @ ss -40 C | INL 0.000 LSB, gain +4.0 % | monotonic, INL < 0.5 LSB |
| PASS | keycell | gain at k=1 over q @ ss -40 C | spread 1.00 % | q-independent within 5 % (buffered gate offset, O1) |
| PASS | softmax | share error / V_B fit @ ss -40 C | 3.97 LSB, V_B residual 1.3 mV | <= 4 LSB vs softmax(x); V_B linear in LSE within 3 mV |
| PASS | readout | SAR codes vs model @ ss -40 C | max |err| 0 LSB | <= 1 LSB (12 codes, mid-step inputs) |
| PASS | vbbuf | ua[1] - V_B, settling @ ss -40 C | 5.5 mV, 1.7 us | <= 6 mV over 1.2..2.3 V, < 20 us |
| PASS | bias | I_u, keep-alive @ ff 125 C | 176.2 nA, gated 1.14 % | I_u 125 nA x PTAT/R (+-40 % corners); gated 0.5..2 % |
| PASS | idac | monotonic / INL @ ff 125 C | INL 0.082 LSB, gain +3.8 % | monotonic, INL < 0.5 LSB |
| PASS | keycell | gain at k=1 over q @ ff 125 C | spread 1.56 % | q-independent within 5 % (buffered gate offset, O1) |
| PASS | softmax | share error / V_B fit @ ff 125 C | 2.20 LSB, V_B residual 1.1 mV | <= 4 LSB vs softmax(x); V_B linear in LSE within 3 mV |
| PASS | readout | SAR codes vs model @ ff 125 C | max |err| 1 LSB | <= 1 LSB (12 codes, mid-step inputs) |
| PASS | vbbuf | ua[1] - V_B, settling @ ff 125 C | 3.9 mV, 5.1 us | <= 6 mV over 1.2..2.3 V, < 20 us |
| PASS | bias | start-up from a 10 us supply ramp | 13.6 us, 125.7 nA | settles < 50 us to I_u |
| PASS | chain | q=[15, 15, 15, 15] ks=[15, 15, 15, 15] | SPICE [255, 0, 0, 0] model [255, 0, 0, 0] | <= 5 LSB per code (tt 27 C) |
| PASS | chain | q=[15, 8, 4, 0] ks=[15, 15, 15, 15] | SPICE [133, 25, 8, 88] model [130, 24, 9, 91] | <= 5 LSB per code (tt 27 C) |
| PASS | chain | q=[7, 7, 7, 7] ks=[15, 15, 15, 15] | SPICE [63, 63, 63, 63] model [64, 64, 64, 64] | <= 5 LSB per code (tt 27 C) |
| PASS | chain | q=[15, 8, 4, 0] ks=[9, 15, 12, 6] | SPICE [85, 118, 27, 25] model [81, 122, 28, 25] | <= 5 LSB per code (tt 27 C) |

23 / 23 checks pass.
