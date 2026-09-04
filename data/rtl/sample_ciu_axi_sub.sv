// -----------------------------------------------------------------------------
// sample_ciu_axi_sub.sv  (SYNTHETIC RTL for Spec-RTL Sentinel demo)
//
// This module intentionally contains several DRIFTS from sample_mas.md so the
// tool has something to catch:
//   1. s_axi_wdata is 32-bit, spec §2.1 requires 64-bit         -> WIDTH DRIFT
//   2. STATUS register (spec §3.2) is not implemented           -> MISSING
//   3. FSM is missing the ERROR state (spec §4.1)               -> MISSING
//   4. DEBUG_SCRATCH register at 0x20 is not in the spec        -> UNDOCUMENTED
// -----------------------------------------------------------------------------
module sample_ciu_axi_sub #(
    parameter int ADDR_WIDTH = 8
) (
    input  wire        aclk,
    input  wire        aresetn,          // active-low reset (matches spec §2.2)

    input  wire [ADDR_WIDTH-1:0] s_axi_awaddr,
    input  wire        s_axi_awvalid,
    output wire        s_axi_awready,

    input  wire [31:0] s_axi_wdata,      // DRIFT: spec §2.1 requires 64-bit
    input  wire        s_axi_wvalid,
    output wire        s_axi_wready
);

    // ---- CSR address map (byte offsets) ----
    localparam ADDR_CTRL  = 8'h00;   // matches spec §3.1
    localparam ADDR_BEK_KEY = 8'h10; // matches spec §3.3
    localparam ADDR_DEBUG = 8'h20;   // UNDOCUMENTED: not present in the spec
    // NOTE: no ADDR_STATUS here -> STATUS register is MISSING (spec §3.2)

    // ---- CSR storage ----
    logic [31:0] ctrl_reg;
    logic [31:0] bek_key_reg;
    logic [31:0] debug_scratch_reg;   // undocumented behavior

    // ---- Control FSM (missing ERROR state, spec §4.1) ----
    typedef enum logic [1:0] {
        IDLE,
        ACTIVE
    } ciu_fsm_e;

    ciu_fsm_e ciu_fsm;

    always_ff @(posedge aclk or negedge aresetn) begin
        if (!aresetn) begin
            ctrl_reg          <= 32'h0;   // reset value 0x0 (spec §3.1)
            bek_key_reg       <= 32'h0;
            debug_scratch_reg <= 32'h0;
            ciu_fsm           <= IDLE;
        end else begin
            case (ciu_fsm)
                IDLE:   if (s_axi_wvalid) ciu_fsm <= ACTIVE;
                ACTIVE: ciu_fsm <= IDLE;
                default: ciu_fsm <= IDLE;
            endcase
        end
    end

    assign s_axi_awready = 1'b1;
    assign s_axi_wready  = 1'b1;

endmodule
